"""
composer.py – Combine video + audio, and concatenate multiple clips.
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


# ── merge audio into video ────────────────────────────────────────────────────

def add_audio(video_path: str, audio_path: str, output_path: str) -> bool:
    """
    Merge an audio file into a video. Video length is preserved;
    audio is trimmed or padded with silence if needed.
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
    Join a list of .mp4 clips into one final video (stream-copy, no re-encode).
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
    """
    After a `manim render` call, locate the output .mp4.
    Manim puts it at:  media_dir/videos/{ClassName}/{quality}/{ClassName}.mp4
    """
    candidates = list(Path(media_dir).rglob(f"{class_name}.mp4"))
    if not candidates:
        candidates = list(Path(media_dir).rglob("*.mp4"))
    if candidates:
        # Prefer the most recently modified file
        return str(max(candidates, key=lambda p: p.stat().st_mtime))
    return None
