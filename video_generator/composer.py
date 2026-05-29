"""
composer.py – Combine video + audio, set duration, mix music, burn captions,
and concatenate clips. Uses FFmpeg (must be built with libass for caption burn-in).
"""

import subprocess
import shutil
from pathlib import Path


def _run(cmd: list) -> bool:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [composer] FFmpeg error:\n{result.stderr[-600:]}")
        return False
    return True


def _escape_sub_path(p) -> str:
    """Escape a path for use inside an FFmpeg subtitles= filter argument."""
    p = str(p).replace("\\", "/")
    p = p.replace(":", r"\:")
    return p


# ── get video duration ────────────────────────────────────────────────────────

def get_duration(video_path: str) -> float:
    """Return the duration of a video in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            str(video_path),
        ],
        capture_output=True, text=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


# ── set exact duration (trim or pad) ─────────────────────────────────────────

def set_duration(input_path: str, output_path: str, duration: float) -> bool:
    """
    Force a clip to be exactly `duration` seconds.

    - If the clip is LONGER  → trim it at the cut point.
    - If the clip is SHORTER → freeze the last frame to fill the gap.

    This lets you write "duration": 8 in your script and get exactly 8 seconds,
    regardless of how long the Manim animation actually ran.
    """
    current = get_duration(input_path)
    if current <= 0:
        return False

    if current >= duration:
        # Trim to target duration
        return _run([
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-t", str(duration),
            "-c:v", "libx264",   # re-encode so the cut is clean
            "-c:a", "aac",
            "-preset", "fast",
            str(output_path),
        ])
    else:
        # Pad by freezing the last frame
        pad_secs = duration - current
        return _run([
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-vf", f"tpad=stop_mode=clone:stop_duration={pad_secs:.3f}",
            "-af", f"apad=pad_dur={pad_secs:.3f}",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-preset", "fast",
            str(output_path),
        ])


# ── merge audio into video ────────────────────────────────────────────────────

def add_audio(video_path: str, audio_path: str, output_path: str) -> bool:
    """
    Merge an audio track into a video.
    The video length is kept; audio is trimmed or padded with silence.
    """
    return _run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path),
    ])


# ── concatenate clips ─────────────────────────────────────────────────────────

def concatenate(clip_paths: list, output_path: str) -> bool:
    """
    Join a list of .mp4 clips into one final video.
    All clips must share the same resolution and frame rate.
    """
    clip_paths = [p for p in clip_paths if Path(p).exists()]
    if not clip_paths:
        print("  [composer] No clips to concatenate.")
        return False

    if len(clip_paths) == 1:
        shutil.copy(clip_paths[0], output_path)
        return True

    list_file = Path(output_path).parent / "_concat_list.txt"
    list_file.write_text(
        "\n".join(f"file '{Path(p).resolve()}'" for p in clip_paths)
    )

    ok = _run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path),
    ])

    list_file.unlink(missing_ok=True)
    return ok


# ── find the mp4 manim rendered ───────────────────────────────────────────────

def find_rendered_mp4(media_dir: str, class_name: str) -> str | None:
    """Locate the .mp4 Manim wrote after rendering."""
    hits = list(Path(media_dir).rglob(f"{class_name}.mp4"))
    if not hits:
        hits = list(Path(media_dir).rglob("*.mp4"))
    return str(max(hits, key=lambda p: p.stat().st_mtime)) if hits else None


# ── FFmpeg capability check ────────────────────────────────────────────────────

def ffmpeg_capabilities() -> dict:
    """Report which FFmpeg pieces we rely on are available."""
    caps = {
        "ffmpeg":  shutil.which("ffmpeg") is not None,
        "ffprobe": shutil.which("ffprobe") is not None,
    }
    if not caps["ffmpeg"]:
        return caps
    try:
        filt = subprocess.run(["ffmpeg", "-hide_banner", "-filters"],
                              capture_output=True, text=True).stdout
        for f in ("subtitles", "sidechaincompress", "amix",
                  "apad", "atrim", "tpad", "aloop", "fade"):
            caps[f] = (f" {f} " in filt) or (f"={f}=" in filt) or (f in filt)
        # libass powers the subtitles filter
        caps["libass"] = caps.get("subtitles", False)
    except Exception:
        pass
    return caps


# ── caption burn-in (standalone) ───────────────────────────────────────────────

def burn_subtitles(video_in: str, ass_path: str, output_path: str) -> bool:
    """Burn an ASS subtitle file into the video (needs FFmpeg+libass)."""
    sub = _escape_sub_path(ass_path)
    return _run([
        "ffmpeg", "-y", "-i", str(video_in),
        "-vf", f"subtitles='{sub}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        str(output_path),
    ])


# ── ducked music mix (delegates to music.py) ────────────────────────────────────

def mix_audio_ducked(video_in, voice, music_track, output_path, **kw) -> bool:
    import music as _music
    return _music.mix_ducked(video_in, voice, music_track, output_path, **kw)


# ── combined finalize: mix audio + burn captions in ONE pass ─────────────────────

def finalize_clip(video_in, output_path, *, voice=None, music=None, ass=None,
                  music_db=-18.0, duck=True, ratio=8, attack=5, release=300,
                  threshold=0.05) -> bool:
    """
    Produce the final per-scene clip in a single FFmpeg pass:
      - optional voice track (padded to clip length)
      - optional background music (looped/trimmed, ducked under voice)
      - optional burned-in ASS captions
    Only re-encodes video when captions are burned; otherwise copies it.
    """
    dur = get_duration(video_in)
    if dur <= 0:
        return False

    inputs = ["-i", str(video_in)]
    idx = 1
    voice_idx = music_idx = None
    if voice and Path(voice).exists():
        inputs += ["-i", str(voice)]; voice_idx = idx; idx += 1
    if music and Path(music).exists():
        inputs += ["-stream_loop", "-1", "-i", str(music)]; music_idx = idx; idx += 1

    fc = []

    # video chain
    if ass:
        fc.append(f"[0:v]subtitles='{_escape_sub_path(ass)}'[vout]")
        vmap, encode_v = "[vout]", True
    else:
        vmap, encode_v = "0:v", False

    # audio chain
    aout = None
    if voice_idx is not None and music_idx is not None:
        fc.append(f"[{music_idx}:a]aresample=44100,atrim=0:{dur:.3f},"
                  f"volume={music_db}dB[bed]")
        if duck:
            # Voice feeds the mix AND the compressor sidechain → split it in two
            # (a filter output pad can only connect to one input).
            fc.append(f"[{voice_idx}:a]aresample=44100,apad,atrim=0:{dur:.3f},"
                      f"asplit=2[vmix][vkey]")
            fc.append(f"[bed][vkey]sidechaincompress=threshold={threshold}:"
                      f"ratio={ratio}:attack={attack}:release={release}[ducked]")
            fc.append("[vmix][ducked]amix=inputs=2:duration=first:"
                      "dropout_transition=0[aout]")
        else:
            fc.append(f"[{voice_idx}:a]aresample=44100,apad,atrim=0:{dur:.3f}[voc]")
            fc.append("[voc][bed]amix=inputs=2:duration=first:"
                      "dropout_transition=0[aout]")
        aout = "[aout]"
    elif voice_idx is not None:
        fc.append(f"[{voice_idx}:a]aresample=44100,apad,atrim=0:{dur:.3f}[aout]")
        aout = "[aout]"
    elif music_idx is not None:
        fc.append(f"[{music_idx}:a]aresample=44100,atrim=0:{dur:.3f},"
                  f"volume={music_db}dB[aout]")
        aout = "[aout]"

    cmd = ["ffmpeg", "-y"] + inputs
    if fc:
        cmd += ["-filter_complex", ";".join(fc)]
    cmd += ["-map", vmap]
    if aout:
        cmd += ["-map", aout]
    else:
        cmd += ["-map", "0:a?"]   # keep original audio if present
    if encode_v:
        cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", "20"]
    else:
        cmd += ["-c:v", "copy"]
    cmd += ["-c:a", "aac", "-b:a", "192k", str(output_path)]
    return _run(cmd)


# ── re-encoding concatenation (uniform params) ───────────────────────────────────

def concatenate_reencode(clip_paths: list, output_path: str,
                         w: int = 1080, h: int = 1920, fps: int = 60) -> bool:
    """
    Concatenate clips, re-encoding to uniform W×H@fps so heterogeneous per-scene
    encodes join cleanly (the stream-copy `concatenate` breaks on mismatches).
    """
    clips = [p for p in clip_paths if Path(p).exists()]
    if not clips:
        print("  [composer] No clips to concatenate.")
        return False

    list_file = Path(output_path).parent / "_concat_reencode.txt"
    list_file.write_text(
        "\n".join(f"file '{Path(p).resolve()}'" for p in clips)
    )
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
          f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}")
    ok = _run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        str(output_path),
    ])
    list_file.unlink(missing_ok=True)
    return ok


# ── loop-friendly fades ──────────────────────────────────────────────────────────

def make_loopable(video_in: str, output_path: str, fade: float = 0.4) -> bool:
    """Add short fade-in/out so the video loops smoothly (end blends to start)."""
    dur = get_duration(video_in)
    if dur <= 0:
        return False
    vf = (f"fade=t=in:st=0:d={fade},"
          f"fade=t=out:st={max(0.0, dur - fade):.3f}:d={fade}")
    return _run([
        "ffmpeg", "-y", "-i", str(video_in),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        str(output_path),
    ])
