#!/usr/bin/env python3
"""
generate.py – YouTube Shorts Video Generator
=============================================
Generates animated Shorts (1080×1920 @ 60fps) for AI, Tech & Gaming content.
Runs 100% locally – no AI API, no internet required.

QUICK START
-----------
  pip install -r requirements.txt

  python generate.py list                       # see all scenes
  python generate.py render neural_network      # render one scene
  python generate.py render all                 # render every scene
  python generate.py render all --tag gaming    # only gaming scenes

OPTIONS
-------
  --format   shorts (default) | instagram | youtube
  --quality  preview (fast) | draft (720p) | high (1080p 60fps)
  --output   ./output  (default)
"""

import argparse
import subprocess
import sys
import os
import random
from pathlib import Path

# ── locate scenes dir relative to this file ──────────────────────────────────
ROOT = Path(__file__).parent
SCENES_DIR = ROOT / "scenes"

sys.path.insert(0, str(ROOT))
from config import FORMATS, QUALITY, DEFAULT_FORMAT
from scenes import REGISTRY


# ─────────────────────────────────────────────────────────────────────────────
def cmd_list(args):
    tag = getattr(args, "tag", None)
    rows = [
        (name, info) for name, info in REGISTRY.items()
        if not tag or tag in info["tags"]
    ]

    bar = "─" * 62
    print(f"\n  YouTube Shorts Video Generator")
    print(f"  {bar}")
    print(f"  {'NAME':<18}  {'DUR':<6}  {'TAGS':<22}  DESCRIPTION")
    print(f"  {bar}")
    for name, info in rows:
        tags = " ".join(info["tags"])
        print(f"  {name:<18}  {info['dur']:<6}  {tags:<22}  {info['desc']}")
    print(f"  {bar}")
    print(f"\n  Total: {len(rows)} scene(s)\n")
    print("  Example commands:")
    print("    python generate.py render neural_network")
    print("    python generate.py render all --tag gaming --quality preview")
    print("    python generate.py render tech_title --format instagram\n")


# ─────────────────────────────────────────────────────────────────────────────
def _manim_cmd(scene_name, fmt, quality, output_dir):
    """Build the manim subprocess command for a given scene."""
    info       = REGISTRY[scene_name]
    scene_file = SCENES_DIR / info["file"]
    scene_cls  = info["class"]
    fmt_cfg    = FORMATS.get(fmt, FORMATS[DEFAULT_FORMAT])
    q_flag     = QUALITY.get(quality, QUALITY["draft"])

    out_path = Path(output_dir) / fmt
    out_path.mkdir(parents=True, exist_ok=True)

    cmd = [
        "manim", "render",
        str(scene_file),
        scene_cls,
        q_flag,
        "--media_dir", str(out_path),
        "--disable_caching",
    ]

    # Shorts / Instagram: portrait resolution override
    if fmt in ("shorts", "instagram"):
        pw, ph = fmt_cfg["pixel_width"], fmt_cfg["pixel_height"]
        cmd += ["--resolution", f"{pw},{ph}"]

    return cmd, out_path


def _render_one(scene_name, fmt, quality, output_dir, verbose=True):
    if scene_name not in REGISTRY:
        print(f"  ERROR: unknown scene '{scene_name}'")
        print("  Run 'python generate.py list' to see available scenes.")
        return False

    info = REGISTRY[scene_name]
    cmd, out_path = _manim_cmd(scene_name, fmt, quality, output_dir)
    fmt_cfg = FORMATS.get(fmt, FORMATS[DEFAULT_FORMAT])

    if verbose:
        print(f"\n  ▶  {scene_name}  ({info['class']})")
        print(f"     Format : {fmt_cfg['label']}")
        print(f"     Quality: {quality}")
        print(f"     Output : {out_path}/")

    try:
        result = subprocess.run(cmd, check=True,
                                capture_output=not verbose,
                                text=True)
        if verbose:
            print(f"  ✓  Done – {scene_name}")
        return True
    except subprocess.CalledProcessError as exc:
        print(f"  ✗  FAILED – {scene_name}")
        if not verbose and exc.stderr:
            print(exc.stderr[-800:])   # last 800 chars of error
        return False
    except FileNotFoundError:
        print("\n  ERROR: 'manim' not found.")
        print("  Install: pip install manim")
        sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
def cmd_render(args):
    fmt     = args.format
    quality = args.quality
    outdir  = args.output
    tag     = getattr(args, "tag", None)

    if args.scene == "all":
        scenes = [
            name for name, info in REGISTRY.items()
            if not tag or tag in info["tags"]
        ]
        print(f"\n  Rendering {len(scenes)} scene(s) …")
        ok, fail = 0, []
        for name in scenes:
            if _render_one(name, fmt, quality, outdir):
                ok += 1
            else:
                fail.append(name)
        print(f"\n  Finished: {ok}/{len(scenes)} succeeded")
        if fail:
            print(f"  Failed  : {', '.join(fail)}")
    else:
        _render_one(args.scene, fmt, quality, outdir)


# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="YouTube Shorts video generator (Manim-based, fully local)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── list ──────────────────────────────────────────────────────────────────
    p_list = sub.add_parser("list", help="List all available scenes")
    p_list.add_argument("--tag", help="Filter by tag (ai, gaming, tech, …)")

    # ── render ────────────────────────────────────────────────────────────────
    p_render = sub.add_parser("render", help="Render a scene (or 'all')")
    p_render.add_argument("scene", help="Scene name or 'all'")
    p_render.add_argument(
        "--format", "-f",
        choices=list(FORMATS.keys()),
        default=DEFAULT_FORMAT,
        help=f"Output format (default: {DEFAULT_FORMAT})",
    )
    p_render.add_argument(
        "--quality", "-q",
        choices=list(QUALITY.keys()),
        default="draft",
        help="Render quality (default: draft)",
    )
    p_render.add_argument(
        "--output", "-o",
        default="./output",
        help="Output directory (default: ./output)",
    )
    p_render.add_argument(
        "--tag", "-t",
        help="When scene='all', filter by tag",
    )

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "render":
        cmd_render(args)


if __name__ == "__main__":
    main()
