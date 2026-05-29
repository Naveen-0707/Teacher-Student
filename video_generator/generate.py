#!/usr/bin/env python3
"""
generate.py – End-to-End Shorts / Reels Generator
==================================================
Builds complete, upload-ready vertical videos (1080×1920) for YouTube Shorts &
Instagram Reels from a JSON script: animation + natural voice + synced burned-in
captions + ducked background music + metadata. Runs locally, free, no paid API.

COMMANDS
--------
  python generate.py setup                          # one-time: voices, music, checks
  python generate.py list                           # built-in scenes / templates
  python generate.py voices                         # TTS voices
  python generate.py render hook                    # render one scene
  python generate.py script my_script.json          # full video from YOUR script

SCRIPT WORKFLOW (recommended)
------------------------------
  1. python generate.py setup           (downloads offline voice + CC0 music)
  2. cp script_example.json my_script.json   then edit it
  3. python generate.py script my_script.json -q preview     (fast check)
  4. python generate.py script my_script.json -q high        (final upload)
  5. Final video + metadata: ./output/final/

OPTIONS (script)
----------------
  --format   shorts (default) | instagram | youtube
  --quality  preview (fast) | draft | high (1080p60 upload)
  --engine   edge (default, online) | piper | kokoro | pyttsx3
  --voice    edge voice name (e.g. en-US-GuyNeural)
  --length   target seconds (band 35–50)
  --music FILE | --no-music | --no-captions | --loop | --no-hook
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
from config import (FORMATS, QUALITY, DEFAULT_FORMAT, DEFAULTS,
                    CAPTION_STYLE, DEFAULT_CAPTION_STYLE, MUSIC_DIR)
from scenes import REGISTRY

# script template name → (scene_file, class_name)
TEMPLATES = {
    "hook":           ("script_scene.py", "ScriptHookScene"),
    "title_card":     ("script_scene.py", "ScriptTitleScene"),
    "text_reveal":    ("script_scene.py", "ScriptTextRevealScene"),
    "bullet_points":  ("script_scene.py", "ScriptBulletScene"),
    "stats_chart":    ("script_scene.py", "ScriptStatsScene"),
    # reuse existing animated scenes
    "neural_network": ("neural_network.py", "NeuralNetworkScene"),
    "neural_training":("neural_network.py", "NeuralTrainingScene"),
    "matrix_rain":    ("code_typing.py",    "MatrixRainScene"),
    "code_typing":    ("code_typing.py",    "CodeTypingScene"),
    "gaming_intro":   ("gaming_intro.py",   "GamingIntroScene"),
    "xp_bar":         ("gaming_intro.py",   "XPBarScene"),
    "achievement":    ("gaming_intro.py",   "AchievementScene"),
    "data_flow":      ("data_visual.py",    "DataFlowScene"),
}

ENGINE_ALIASES = {"online": "edge", "offline": "piper"}

NICE_VOICES = [
    ("en-US-GuyNeural",   "Male  – US, clear & professional (recommended)"),
    ("en-US-TonyNeural",  "Male  – US, deep & energetic (great for gaming)"),
    ("en-GB-RyanNeural",  "Male  – UK, calm & authoritative"),
    ("en-US-JennyNeural", "Female – US, friendly & clear"),
    ("en-US-AriaNeural",  "Female – US, expressive"),
    ("en-GB-SoniaNeural", "Female – UK, professional"),
]


# ── list / voices ─────────────────────────────────────────────────────────────
def cmd_list(args):
    tag = getattr(args, "tag", None)
    rows = [(n, i) for n, i in REGISTRY.items() if not tag or tag in i["tags"]]
    bar = "─" * 64
    print(f"\n  Shorts/Reels Generator  –  Scenes & Templates")
    print(f"  {bar}")
    print(f"  {'NAME':<20}  {'DUR':<6}  {'TAGS':<20}  DESCRIPTION")
    print(f"  {bar}")
    for name, info in rows:
        print(f"  {name:<20}  {info['dur']:<6}  "
              f"{' '.join(info['tags']):<20}  {info['desc']}")
    print(f"  {bar}")
    print("\n  Tip: python generate.py script script_example.json\n")


def cmd_voices(_args):
    print("\n  edge-tts voices (free, no key, needs internet):\n")
    for v, d in NICE_VOICES:
        print(f"    {v:<28}  {d}")
    print("\n  Offline: --engine piper (run 'setup' to download a voice).\n")


# ── manim helpers ─────────────────────────────────────────────────────────────
def _build_manim_cmd(scene_file, scene_cls, fmt, quality, out_dir):
    fmt_cfg = FORMATS.get(fmt, FORMATS[DEFAULT_FORMAT])
    q_flag = QUALITY.get(quality, QUALITY["draft"])
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["manim", "render", str(SCENES_DIR / scene_file), scene_cls, q_flag,
           "--media_dir", str(out_dir), "--disable_caching"]
    if fmt in ("shorts", "instagram"):
        cmd += ["--resolution",
                f"{fmt_cfg['pixel_width']},{fmt_cfg['pixel_height']}"]
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


def _find_mp4(media_dir: Path, cls_name: str):
    hits = list(media_dir.rglob(f"{cls_name}.mp4"))
    if not hits:
        hits = list(media_dir.rglob("*.mp4"))
    return max(hits, key=lambda p: p.stat().st_mtime) if hits else None


# ── render command ──────────────────────────────────────────────────────────────
def _render_one(name, fmt, quality, output_dir) -> bool:
    if name not in REGISTRY:
        print(f"  ERROR: unknown scene '{name}'. Run 'list'.")
        return False
    info = REGISTRY[name]
    out_dir = Path(output_dir) / fmt
    cmd = _build_manim_cmd(info["file"], info["class"], fmt, quality, out_dir)
    print(f"\n  ▶  {name}  |  {FORMATS.get(fmt, FORMATS[DEFAULT_FORMAT])['label']}"
          f"  |  {quality}")
    ok = _run_manim(cmd)
    print(f"  {'✓' if ok else '✗'}  {name}")
    return ok


def cmd_render(args):
    fmt, quality, outdir = args.format, args.quality, args.output
    tag = getattr(args, "tag", None)
    if args.scene == "all":
        scenes = [n for n, i in REGISTRY.items() if not tag or tag in i["tags"]]
        ok = 0
        fail = []
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


# ── setup command ─────────────────────────────────────────────────────────────
def cmd_setup(args):
    try:
        import assets_setup
    except ImportError as exc:
        print(f"  ERROR: cannot import assets_setup ({exc})")
        sys.exit(1)
    assets_setup.run(check_only=getattr(args, "check", False),
                     skip_music=getattr(args, "no_music", False))


# ── script command ──────────────────────────────────────────────────────────────
def _safe_name(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_ " else "_"
                   for c in s).strip().replace(" ", "_") or "video"


def _resolve_caption_style(script, args):
    cap = script.get("captions")
    enabled = DEFAULTS["captions"]
    style_name = DEFAULT_CAPTION_STYLE
    overrides = {}
    if cap is False:
        enabled = False
    elif isinstance(cap, dict):
        enabled = cap.get("enabled", True)
        style_name = cap.get("style", DEFAULT_CAPTION_STYLE)
        overrides = {k: cap[k] for k in
                     ("font_size_px", "max_chars_per_line", "max_lines",
                      "karaoke", "margin_v") if k in cap}
    if getattr(args, "no_captions", False):
        enabled = False
    style = dict(CAPTION_STYLE.get(style_name, CAPTION_STYLE[DEFAULT_CAPTION_STYLE]))
    style.update(overrides)
    return enabled, style


def _resolve_music(script, args):
    """Return (track_path, volume_db, duck) or (None, …) if disabled/unavailable."""
    import music as music_mod
    mcfg = script.get("music") or {}
    enabled = (not getattr(args, "no_music", False)
               and mcfg.get("enabled", DEFAULTS["music"]))
    if not enabled and not getattr(args, "music", None):
        return None, DEFAULTS["music_volume_db"], DEFAULTS["duck"]

    vol = mcfg.get("volume_db", DEFAULTS["music_volume_db"])
    duck = mcfg.get("duck", DEFAULTS["duck"])

    track = getattr(args, "music", None) or mcfg.get("track")
    if track:
        tp = Path(track)
        if not tp.is_absolute() and not tp.exists():
            tp = Path(MUSIC_DIR) / track
        if tp.exists():
            return str(tp), vol, duck
        print(f"  [music] track not found: {track} — trying library by genre")

    picked = music_mod.pick_track(genre=mcfg.get("genre"))
    if not picked:
        print("  [music] no tracks in assets/music/ — continuing without music.")
        print("          Add your own .mp3s or run: python generate.py setup")
        return None, vol, duck
    return picked, vol, duck


def cmd_script(args):
    script_path = Path(args.script_file)
    if not script_path.exists():
        print(f"  ERROR: script file not found: {script_path}")
        sys.exit(1)
    script = json.loads(script_path.read_text())

    fmt = args.format or DEFAULT_FORMAT
    fmt_cfg = FORMATS.get(fmt, FORMATS[DEFAULT_FORMAT])
    pw, ph, fps = (fmt_cfg["pixel_width"], fmt_cfg["pixel_height"],
                   fmt_cfg["frame_rate"])
    quality = args.quality or script.get("quality") or "draft"
    outdir = Path(args.output)

    engine = (args.engine or script.get("voice_engine")
              or script.get("engine") or DEFAULTS["engine"])
    engine = ENGINE_ALIASES.get(engine, engine)
    voice = args.voice or script.get("voice") or DEFAULTS["voice"]
    if engine in ("piper", "kokoro") and voice and "Neural" in voice:
        voice = None   # edge voice name doesn't apply to offline engines

    length_target = (args.length or script.get("length_target")
                     or DEFAULTS["length_target"])
    length_target = max(DEFAULTS["length_min"],
                        min(DEFAULTS["length_max"], int(length_target)))

    loop = args.loop or script.get("loop", DEFAULTS["loop"])
    auto_hook = (False if getattr(args, "no_hook", False)
                 else script.get("auto_hook", DEFAULTS["auto_hook"]))

    channel = script.get("channel", "@YourChannel")
    vid_title = script.get("title", "My Shorts Video")
    scenes = list(script.get("scenes", []))

    captions_enabled, cap_style = _resolve_caption_style(script, args)

    # ── deps ──────────────────────────────────────────────────────────────────
    try:
        import narrator as _narrator
        import composer as _composer
        import captions as _captions
        import metadata as _metadata
    except ImportError as exc:
        print(f"  ERROR: missing module ({exc}). Run: pip install -r requirements.txt")
        sys.exit(1)

    caps = _composer.ffmpeg_capabilities()
    if not caps.get("ffmpeg"):
        print("  ERROR: ffmpeg not found. Install FFmpeg (with libass).")
        sys.exit(1)
    if captions_enabled and not caps.get("subtitles"):
        print("  [warning] FFmpeg lacks the subtitles filter (libass) — captions "
              "disabled. Reinstall FFmpeg with libass. See: generate.py setup --check")
        captions_enabled = False

    # ── auto-hook ──────────────────────────────────────────────────────────────
    if auto_hook and scenes and scenes[0].get("template") != "hook" \
            and not scenes[0].get("hook"):
        scenes.insert(0, {
            "template": "hook",
            "hook_text": vid_title,
            "accent": scenes[0].get("accent", "cyan"),
            "duration": 2.5,
            "narration": "",          # visual punch; no VO
        })

    # ── music (one bed for the whole video) ────────────────────────────────────
    music_track, music_db, music_duck = _resolve_music(script, args)

    # ── per-scene duration plan ────────────────────────────────────────────────
    n = len(scenes)
    assigned = sum(float(s["duration"]) for s in scenes if s.get("duration"))
    missing = [s for s in scenes if not s.get("duration")]
    auto_dur = (max(0.0, length_target - assigned) / len(missing)) if missing else 0.0

    print(f"\n  Script : {script_path.name}")
    print(f"  Title  : {vid_title}")
    print(f"  Format : {fmt_cfg['label']}   Quality: {quality}")
    print(f"  Voice  : {engine}" + (f" / {voice}" if voice else ""))
    print(f"  Captions: {'on' if captions_enabled else 'off'}   "
          f"Music: {Path(music_track).name if music_track else 'none'}   "
          f"Loop: {loop}")
    print(f"  Scenes : {n}   Target ~{length_target}s\n")

    tmp_dir = outdir / "_tmp"
    final_dir = outdir / "final"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)

    final_clips = []
    for idx, sc in enumerate(scenes):
        template = sc.get("template", "title_card")
        narration = sc.get("narration", "")
        audio_file = sc.get("audio_file")
        duration = float(sc["duration"]) if sc.get("duration") else max(3.0, auto_dur)
        scene_caps = captions_enabled and sc.get("captions", True)

        print(f"  [{idx+1}/{n}] {template}  ({duration:.1f}s)")

        if template not in TEMPLATES:
            print(f"     unknown template '{template}', skipping.")
            continue

        # active config for the Manim scene (carry caption flag for layout)
        ACTIVE_CFG.write_text(json.dumps(
            {**sc, "channel": channel, "captions": scene_caps},
            ensure_ascii=False))

        scene_file, scene_cls = TEMPLATES[template]
        render_dir = tmp_dir / f"scene_{idx:02d}"
        if not _run_manim(_build_manim_cmd(scene_file, scene_cls, fmt,
                                           quality, render_dir)):
            print("     ✗ render failed, skipping.")
            continue
        mp4 = _find_mp4(render_dir, scene_cls)
        if not mp4:
            print("     ✗ no mp4 produced, skipping.")
            continue

        # exact duration
        sized = tmp_dir / f"clip_{idx:02d}_sized.mp4"
        if _composer.set_duration(str(mp4), str(sized), duration):
            mp4 = sized

        # voice + timings
        voice_path, word_timings = None, []
        if audio_file:
            res = _narrator.generate(narration or " ",
                                     str(tmp_dir / f"voice_{idx:02d}.wav"),
                                     engine="recorded", audio_file=audio_file)
            voice_path = res.audio_path if res.ok else None
            word_timings = res.word_timings
        elif narration.strip():
            res = _narrator.generate(narration,
                                     str(tmp_dir / f"voice_{idx:02d}.mp3"),
                                     engine=engine, voice=voice)
            voice_path = res.audio_path if res.ok else None
            word_timings = res.word_timings

        # captions
        ass_path = None
        if scene_caps and word_timings:
            ass_path = _captions.build_ass(
                word_timings, str(tmp_dir / f"cap_{idx:02d}.ass"),
                video_w=pw, video_h=ph, style=cap_style)

        # finalize: mix (ducked music under voice) + burn captions in one pass
        final_i = tmp_dir / f"clip_{idx:02d}_final.mp4"
        if _composer.finalize_clip(
                str(mp4), str(final_i), voice=voice_path, music=music_track,
                ass=ass_path, music_db=music_db, duck=music_duck):
            final_clips.append(str(final_i))
            tags = []
            if voice_path: tags.append("voice")
            if music_track: tags.append("music")
            if ass_path: tags.append("captions")
            print(f"     ✓ {'+'.join(tags) or 'video'}")
        else:
            final_clips.append(str(mp4))
            print("     ~ finalize failed, using sized clip")

    ACTIVE_CFG.unlink(missing_ok=True)

    if not final_clips:
        print("\n  ERROR: no clips were rendered.")
        return

    # concat (re-encode for uniform params)
    out_mp4 = final_dir / f"{_safe_name(vid_title)}.mp4"
    if not _composer.concatenate_reencode(final_clips, str(out_mp4), pw, ph, fps):
        print(f"\n  ✗ concatenation failed; clips are in {tmp_dir}")
        return

    # optional loop polish
    if loop:
        looped = final_dir / f"{_safe_name(vid_title)}_loop.mp4"
        if _composer.make_loopable(str(out_mp4), str(looped)):
            out_mp4 = looped

    # metadata sidecar
    meta_path = final_dir / f"{_safe_name(vid_title)}.txt"
    _metadata.build(script, str(meta_path))

    dur = _composer.get_duration(str(out_mp4))
    print(f"\n  ✅  Final video : {out_mp4}  ({dur:.1f}s)")
    print(f"      Metadata    : {meta_path}")
    print(f"      Upload to YouTube Shorts / Instagram Reels → done!\n")


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="End-to-end Shorts/Reels generator (Manim+FFmpeg, local)",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="List scenes & templates")
    p.add_argument("--tag")

    sub.add_parser("voices", help="List TTS voices")

    p = sub.add_parser("setup", help="Download voice + music; check FFmpeg")
    p.add_argument("--check", action="store_true", help="Only run capability checks")
    p.add_argument("--no-music", action="store_true", help="Skip music download")

    p = sub.add_parser("render", help="Render one built-in scene")
    p.add_argument("scene")
    p.add_argument("--format", "-f", choices=list(FORMATS), default=DEFAULT_FORMAT)
    p.add_argument("--quality", "-q", choices=list(QUALITY), default="draft")
    p.add_argument("--output", "-o", default="./output")
    p.add_argument("--tag", "-t")

    p = sub.add_parser("script", help="Build a full video from your script JSON")
    p.add_argument("script_file")
    p.add_argument("--format", "-f", choices=list(FORMATS), default=DEFAULT_FORMAT)
    p.add_argument("--quality", "-q", choices=list(QUALITY), default=None)
    p.add_argument("--output", "-o", default="./output")
    p.add_argument("--engine", choices=["edge", "piper", "kokoro", "pyttsx3",
                                        "online", "offline"], default=None)
    p.add_argument("--voice", default=None)
    p.add_argument("--length", type=int, default=None, help="target seconds")
    p.add_argument("--music", default=None, help="music file (overrides script)")
    p.add_argument("--no-music", action="store_true")
    p.add_argument("--no-captions", action="store_true")
    p.add_argument("--no-hook", action="store_true")
    p.add_argument("--loop", action="store_true")

    args = parser.parse_args()
    {"list": cmd_list, "voices": cmd_voices, "setup": cmd_setup,
     "render": cmd_render, "script": cmd_script}[args.command](args)


if __name__ == "__main__":
    main()
