"""
music.py – pick royalty-free background music and mix it under narration.

- pick_track(genre): choose a track from assets/music/ (user-supplied and/or
  downloaded by `generate.py setup`).
- mix_ducked(...): overlay the music under the voice on a video, looping/trimming
  the music to the clip length and DUCKING it (sidechain compression) so it drops
  in volume whenever the narration is speaking.

No external Python deps – just FFmpeg (must include sidechaincompress + amix).
"""

import os
import random
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as appcfg

AUDIO_EXTS = (".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac")


# ── local ffprobe (no composer import → no circular dependency) ──────────────
def _duration(path: str) -> float:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True,
        )
        return float(out.stdout.strip())
    except Exception:
        return 0.0


# ── track selection ──────────────────────────────────────────────────────────
def list_tracks(music_dir=None) -> list:
    music_dir = Path(music_dir or appcfg.MUSIC_DIR)
    if not music_dir.exists():
        return []
    return sorted(
        str(p) for p in music_dir.iterdir()
        if p.suffix.lower() in AUDIO_EXTS
    )


def pick_track(genre=None, music_dir=None, seed=None) -> str | None:
    """Pick a track. If `genre` is given, prefer filenames containing it."""
    tracks = list_tracks(music_dir)
    if not tracks:
        return None
    rng = random.Random(seed)
    if genre:
        g = genre.lower()
        matches = [t for t in tracks if g in Path(t).stem.lower()]
        if matches:
            return rng.choice(matches)
    return rng.choice(tracks)


# ── mixing ───────────────────────────────────────────────────────────────────
def mix_ducked(video_in, voice_audio, music_track, out_path, *,
               music_db=-18.0, duck=True, ratio=8, attack=5, release=300,
               threshold=0.05) -> bool:
    """
    Mix `music_track` under `voice_audio` onto `video_in` → `out_path`.
    Music is looped/trimmed to the video's duration and (optionally) ducked under
    the voice. Video stream is copied (no re-encode here).
    """
    dur = _duration(video_in)
    if dur <= 0:
        print("  [music] could not read video duration")
        return False

    # No voice → just lay music under the video for its full length.
    if not voice_audio or not Path(voice_audio).exists():
        fc = (
            f"[1:a]aresample=44100,atrim=0:{dur:.3f},"
            f"volume={music_db}dB[aout]"
        )
        cmd = [
            "ffmpeg", "-y", "-i", str(video_in),
            "-stream_loop", "-1", "-i", str(music_track),
            "-filter_complex", fc,
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            str(out_path),
        ]
        return _run(cmd, out_path)

    if duck:
        # Voice feeds the mix AND the sidechain key → split it (a filter output
        # pad can only connect to one input).
        fc = (
            f"[1:a]aresample=44100,apad,atrim=0:{dur:.3f},asplit=2[vmix][vkey];"
            f"[2:a]aresample=44100,atrim=0:{dur:.3f},volume={music_db}dB[bed];"
            f"[bed][vkey]sidechaincompress=threshold={threshold}:ratio={ratio}:"
            f"attack={attack}:release={release}[ducked];"
            f"[vmix][ducked]amix=inputs=2:duration=first:dropout_transition=0[aout]"
        )
    else:
        fc = (
            f"[1:a]aresample=44100,apad,atrim=0:{dur:.3f}[voc];"
            f"[2:a]aresample=44100,atrim=0:{dur:.3f},volume={music_db}dB[bed];"
            f"[voc][bed]amix=inputs=2:duration=first:dropout_transition=0[aout]"
        )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_in),          # 0: video (+ unused audio if any)
        "-i", str(voice_audio),       # 1: voice (sidechain KEY)
        "-stream_loop", "-1", "-i", str(music_track),   # 2: music (looped)
        "-filter_complex", fc,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        str(out_path),
    ]
    return _run(cmd, out_path)


def _run(cmd, out_path) -> bool:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not Path(out_path).exists():
        print(f"  [music] FFmpeg error:\n{r.stderr[-700:]}")
        return False
    return True


# ── CLI helper ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Tracks in", appcfg.MUSIC_DIR, ":")
    for t in list_tracks():
        print("  ", t)
    print("pick_track(genre='energetic') →", pick_track(genre="energetic"))
