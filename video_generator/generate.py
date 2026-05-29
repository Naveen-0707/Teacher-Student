#!/usr/bin/env python3
"""
generate.py – YouTube Shorts Video Generator
=============================================
Generates animated Shorts (1080×1920 @ 60fps) for AI, Tech & Gaming content.
Runs 100% locally – no AI API required.

COMMANDS
--------
  python generate.py list                           # see all built-in scenes
  python generate.py render neural_network          # render one scene
  python generate.py render all --tag gaming        # render all gaming scenes
  python generate.py script my_script.json          # create video from YOUR script
  python generate.py voices                         # list available TTS voices

SCRIPT WORKFLOW (recommended)
------------------------------
  1. Copy script_example.json → my_script.json
  2. Edit: change title, channel, scenes, narration text
  3. python generate.py script my_script.json
  4. Find your final video in ./output/final/

OPTIONS
-------
  --format   shorts (default) | instagram | youtube
  --quality  preview (fast) | draft (720p) | high (1080p 60fps)
  --output   ./output  (default)
  --voice    en-US-GuyNeural (default, needs internet)
  --engine   online (default) | offline (no internet, basic quality)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT       = Path(__file__).parent
SCENES_DIR = ROOT / "scenes"
ACTIVE_CFG = ROOT / "_active_scene.json"

sys.path.insert(0, str(ROOT))
from config import FORMATS, QUALITY, DEFAULT_FORMAT
from scenes  import REGISTRY

# Mapping from script template name → (scene_file, class_name)
TEMPLATES = {
    "title_card":    ("script_scene.py", "ScriptTitleScene"),
    "text_reveal":   ("script_scene.py", "ScriptTextRevealScene"),
    "bullet_points": ("script_scene.py", "ScriptBulletScene"),
    "stats_chart":   ("script_scene.py", "ScriptStatsScene"),
    # reuse existing animated scenes
    "neural_network": ("neural_network.py", "NeuralNetworkScene"),
    "neural_training":("neural_network.py", "NeuralTrainingScene"),
    "matrix_rain":   ("code_typing.py",    "MatrixRainScene"),
    "code_typing":   ("code_typing.py",    "CodeTypingScene"),
    "gaming_intro":  ("gaming_intro.py",   "GamingIntroScene"),
    "xp_bar":        ("gaming_intro.py",   "XPBarScene"),
    "achievement":   ("gaming_intro.py",   "AchievementScene"),
    "data_flow":     ("data_visual.py",    "DataFlowScene"),
}

NICE_VOICES = [
    ("en-US-GuyNeural",    "Male  – US, clear & professional (recommended)"),
    ("en-US-TonyNeural",   "Male  – US, deep & energetic (great for gaming)"),
    ("en-GB-RyanNeural",   "Male  – UK, calm & authoritative"),
    ("en-US-JennyNeural",  "Female – US, friendly & clear"),
    ("en-US-AriaNeural",   "Female – US, expressive"),
    ("en-GB-SoniaNeural",  "Female – UK, professional"),
]


# ── list command ─────────────────────────────────────────────────────────────

def cmd_list(args):
    tag  = getattr(args, "tag", None)
    rows = [(n, i) for n, i in REGISTRY.items()
            if not tag or tag in i["tags"]]
    bar  = "─" * 64
    print(f"\n  YouTube Shorts Video Generator  –  Built-in Scenes")
    print(f"  {bar}")
    print(f"  {'NAME':<20}  {'DUR':<6}  {'TAGS':<22}  DESCRIPTION")
    print(f"  {bar}")
    for name, info in rows:
        print(f"  {name:<20}  {info['dur']:<6}  {' '.join(info['tags']):<22}  {info['desc']}")
    print(f"  {bar}")
    print(f"\n  Tip: python generate.py script script_example.json")
    print(f"       to create a fully custom video from your own script.\n")


# ── voices command ────────────────────────────────────────────────────────────

def cmd_voices(_args):
    print("\n  Available online voices (edge-tts, needs internet):\n")
    for voice, desc in NICE_VOICES:
        print(f"    {voice:<28}  {desc}")
    print("\n  Use: --voice en-US-TonyNeural  in the script command.")
    print("  Or set  \"voice\": \"en-US-TonyNeural\"  in your script JSON.\n")


# ── low-level render helpers ─────────────────────────────────────────────────

def _build_manim_cmd(scene_file, scene_cls, fmt, quality, out_dir):
    fmt_cfg = FORMATS.get(fmt, FORMATS[DEFAULT_FORMAT])
    q_flag  = QUALITY.get(quality, QUALITY["draft"])
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "manim", "render",
        str(SCENES_DIR / scene_file),
        scene_cls,
        q_flag,
        "--media_dir", str(out_dir),
        "--disable_caching",
    ]
    if fmt in ("shorts", "instagram"):
        pw, ph = fmt_cfg["pixel_width"], fmt_cfg["pixel_height"]
        cmd += ["--resolution", f"{pw},{ph}"]
    return cmd


def _run_manim(cmd) -> bool:
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        print("\n  ERROR: 'manim' not found. Install: pip install manim")
        sys.exit(1)


def _find_mp4(media_dir: Path, cls_name: str) -> Path | None:
    hits = list(media_dir.rglob(f"{cls_name}.mp4"))
    if not hits:
        hits = list(media_dir.rglob("*.mp4"))
    return max(hits, key=lambda p: p.stat().st_mtime) if hits else None


# ── render command ────────────────────────────────────────────────────────────

def _render_one(name, fmt, quality, output_dir, verbose=True) -> bool:
    if name not in REGISTRY:
        print(f"  ERROR: unknown scene '{name}'. Run 'list' to see options.")
        return False
    info    = REGISTRY[name]
    out_dir = Path(output_dir) / fmt
    cmd     = _build_manim_cmd(info["file"], info["class"], fmt, quality, out_dir)
    if verbose:
        fmt_label = FORMATS.get(fmt, FORMATS[DEFAULT_FORMAT])["label"]
        print(f"\n  ▶  {name}  |  {fmt_label}  |  {quality}")
    ok = _run_manim(cmd)
    print(f"  {'✓' if ok else '✗'}  {name}")
    return ok


def cmd_render(args):
    fmt, quality, outdir = args.format, args.quality, args.output
    tag = getattr(args, "tag", None)

    if args.scene == "all":
        scenes = [n for n, i in REGISTRY.items()
                  if not tag or tag in i["tags"]]
        ok, fail = 0, []
        for n in scenes:
            if _render_one(n, fmt, quality, outdir):
                ok += 1
            else:
                fail.append(n)
        print(f"\n  Done: {ok}/{len(scenes)}")
        if fail:
            print(f"  Failed: {', '.join(fail)}")
    else:
        _render_one(args.scene, fmt, quality, outdir)


# ── script command ────────────────────────────────────────────────────────────

def cmd_script(args):
    script_path = Path(args.script_file)
    if not script_path.exists():
        print(f"  ERROR: script file not found: {script_path}")
        sys.exit(1)

    script    = json.loads(script_path.read_text())
    fmt       = getattr(args, "format", DEFAULT_FORMAT)
    quality   = getattr(args, "quality", script.get("quality", "draft"))
    outdir    = Path(getattr(args, "output", "./output"))
    engine    = getattr(args, "engine",  script.get("voice_engine", "online"))
    voice     = getattr(args, "voice",   script.get("voice", "en-US-GuyNeural"))
    scenes    = script.get("scenes", [])

    channel   = script.get("channel", "@YourChannel")
    vid_title = script.get("title",   "My Shorts Video")

    print(f"\n  Script : {script_path.name}")
    print(f"  Title  : {vid_title}")
    print(f"  Scenes : {len(scenes)}")
    print(f"  Voice  : {voice}  [{engine}]")
    print(f"  Quality: {quality}\n")

    final_clips = []
    tmp_dir     = outdir / "_tmp"
    final_dir   = outdir / "final"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)

    # Lazy imports so the script command still works if narrator/composer
    # can't be imported (missing optional deps)
    try:
        import narrator as _narrator
        import composer as _composer
        HAS_AUDIO = True
    except ImportError:
        HAS_AUDIO = False
        print("  [warning] narrator/composer not found – rendering video only (no voice)")

    for idx, scene_cfg in enumerate(scenes):
        template  = scene_cfg.get("template",  "title_card")
        narration = scene_cfg.get("narration", "")
        duration  = scene_cfg.get("duration",  None)   # seconds, or None = keep as-is

        dur_label = f"  duration={duration}s" if duration else ""
        print(f"  [{idx+1}/{len(scenes)}] template={template}{dur_label}")

        # ── write active config for script_scene.py ──────────────────────────
        merged_cfg = {**scene_cfg, "channel": channel}
        ACTIVE_CFG.write_text(json.dumps(merged_cfg, ensure_ascii=False))

        # ── figure out which manim file / class to render ────────────────────
        if template in TEMPLATES:
            scene_file, scene_cls = TEMPLATES[template]
        else:
            print(f"     Unknown template '{template}', skipping.")
            continue

        # ── render manim scene ───────────────────────────────────────────────
        render_dir = tmp_dir / f"scene_{idx:02d}"
        cmd = _build_manim_cmd(scene_file, scene_cls, fmt, quality, render_dir)
        ok  = _run_manim(cmd)
        if not ok:
            print(f"     ✗  render failed, skipping.")
            continue

        mp4 = _find_mp4(render_dir, scene_cls)
        if not mp4:
            print(f"     ✗  mp4 not found after render, skipping.")
            continue

        # ── apply exact duration (trim or freeze-pad) ─────────────────────────
        if HAS_AUDIO and duration:
            sized_mp4 = tmp_dir / f"clip_{idx:02d}_sized.mp4"
            ok = _composer.set_duration(str(mp4), str(sized_mp4), float(duration))
            if ok:
                actual = _composer.get_duration(str(sized_mp4))
                print(f"     ✓  duration set to {actual:.1f}s")
                mp4 = sized_mp4
            else:
                print(f"     ~ duration adjustment failed, keeping original")

        # ── generate narration audio ─────────────────────────────────────────
        final_clip = tmp_dir / f"clip_{idx:02d}_final.mp4"

        if HAS_AUDIO and narration.strip():
            audio_path = tmp_dir / f"audio_{idx:02d}.mp3"
            audio_ok   = _narrator.generate(
                narration, str(audio_path), engine=engine, voice=voice
            )
            if audio_ok:
                merged_ok = _composer.add_audio(str(mp4), str(audio_path),
                                                str(final_clip))
                if merged_ok:
                    print(f"     ✓  video + voice")
                else:
                    print(f"     ~ voice merge failed, using silent clip")
                    final_clip = mp4
            else:
                print(f"     ~ narration failed, using silent clip")
                final_clip = mp4
        else:
            final_clip = mp4
            print(f"     ✓  video (no narration)")

        final_clips.append(str(final_clip))

    # ── concatenate all clips ─────────────────────────────────────────────────
    if not final_clips:
        print("\n  ERROR: No clips were rendered.")
        return

    safe_title = "".join(c if c.isalnum() or c in "-_ " else "_"
                         for c in vid_title).replace(" ", "_")
    out_mp4 = final_dir / f"{safe_title}.mp4"

    if HAS_AUDIO:
        ok = _composer.concatenate(final_clips, str(out_mp4))
    else:
        import shutil
        shutil.copy(final_clips[0], str(out_mp4))
        ok = True

    if ok:
        print(f"\n  ✅  Final video: {out_mp4}")
        print(f"      Upload to YouTube Shorts → done!\n")
    else:
        print(f"\n  ✗  Concatenation failed. Individual clips are in {tmp_dir}\n")

    # Clean up temp config
    ACTIVE_CFG.unlink(missing_ok=True)


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="YouTube Shorts video generator (Manim, fully local)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="List all built-in scenes")
    p.add_argument("--tag", help="Filter by tag")

    # voices
    sub.add_parser("voices", help="List available TTS voices")

    # render
    p = sub.add_parser("render", help="Render a built-in scene")
    p.add_argument("scene", help="Scene name or 'all'")
    p.add_argument("--format",  "-f", choices=list(FORMATS.keys()), default=DEFAULT_FORMAT)
    p.add_argument("--quality", "-q", choices=list(QUALITY.keys()), default="draft")
    p.add_argument("--output",  "-o", default="./output")
    p.add_argument("--tag",     "-t", help="Filter when scene='all'")

    # script  ← NEW
    p = sub.add_parser("script", help="Create a full video from your script JSON")
    p.add_argument("script_file", help="Path to your script .json file")
    p.add_argument("--format",  "-f", choices=list(FORMATS.keys()), default=DEFAULT_FORMAT)
    p.add_argument("--quality", "-q", choices=list(QUALITY.keys()), default=None,
                   help="Override quality set inside the script")
    p.add_argument("--output",  "-o", default="./output")
    p.add_argument("--engine",  choices=["online", "offline"], default=None,
                   help="TTS engine (overrides script setting)")
    p.add_argument("--voice",   default=None,
                   help="TTS voice (overrides script setting)")

    args = parser.parse_args()

    dispatch = {
        "list":   cmd_list,
        "voices": cmd_voices,
        "render": cmd_render,
        "script": cmd_script,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
