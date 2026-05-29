"""
composer.py – Combine video + audio, set duration, and concatenate clips.
Uses FFmpeg (already installed as a Manim dependency).
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
