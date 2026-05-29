"""
assets_setup.py – one-time setup for the generator.

  python generate.py setup            # download voice + music, run checks
  python generate.py setup --check    # only verify FFmpeg / deps

Downloads (idempotent — skips files already present):
  - a default offline Piper voice (so --engine piper works with no internet)
  - a small CC0 background-music starter set into assets/music/

Also verifies FFmpeg has the filters we depend on (esp. libass for captions).
Everything here is free + no API key. Network failures are non-fatal: the script
prints where to get assets manually and continues.
"""

import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as appcfg

# CC0 starter music (public domain, safe for monetized content).
# Add your own files to assets/music/ at any time — they're picked up automatically.
MUSIC_SOURCES = [
    # (url, filename)  – FreePD.com is CC0. Filenames embed a loose "genre".
    ("https://freepd.com/music/Wholesome.mp3",   "calm_wholesome.mp3"),
    ("https://freepd.com/music/Beauty Flow.mp3", "calm_beautyflow.mp3"),
    ("https://freepd.com/music/Energy.mp3",      "energetic_energy.mp3"),
    ("https://freepd.com/music/Rge.mp3",         "energetic_rge.mp3"),
]

_UA = {"User-Agent": "Mozilla/5.0 (video_generator setup)"}


def _download(url, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"    ✓ already present: {dest.name}")
        return True
    try:
        print(f"    ↓ {url}")
        req = urllib.request.Request(url, headers=_UA)
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
            f.write(r.read())
        ok = dest.exists() and dest.stat().st_size > 0
        print(f"    {'✓' if ok else '✗'} {dest.name}")
        return ok
    except Exception as exc:
        print(f"    ✗ failed ({exc})")
        if dest.exists():
            dest.unlink(missing_ok=True)
        return False


# ── Piper voice ──────────────────────────────────────────────────────────────
def download_piper_voice():
    print("\n  Piper offline voice")
    pdir = Path(appcfg.PIPER_DIR)
    pdir.mkdir(parents=True, exist_ok=True)
    name = appcfg.PIPER_DEFAULT_VOICE
    base = appcfg.PIPER_VOICE_BASE_URL
    onnx_ok = _download(base + f"{name}.onnx", pdir / f"{name}.onnx")
    json_ok = _download(base + f"{name}.onnx.json", pdir / f"{name}.onnx.json")
    if not (onnx_ok and json_ok):
        print("    Manual: download the .onnx + .onnx.json from")
        print("            https://huggingface.co/rhasspy/piper-voices  →  "
              f"{appcfg.PIPER_DIR}/")
    return onnx_ok and json_ok


# ── music ─────────────────────────────────────────────────────────────────────
def download_music():
    print("\n  CC0 background-music starter pack")
    mdir = Path(appcfg.MUSIC_DIR)
    mdir.mkdir(parents=True, exist_ok=True)
    got = 0
    for url, fname in MUSIC_SOURCES:
        if _download(url, mdir / fname):
            got += 1
    print(f"    {got}/{len(MUSIC_SOURCES)} tracks ready in {mdir}")
    if got == 0:
        print("    Add your own royalty-free / CC0 .mp3s here. Good free sources:")
        print("      • YouTube Studio Audio Library   • pixabay.com/music")
        print("      • freepd.com (CC0)               • incompetech.com (credit)")
    return got


# ── checks ──────────────────────────────────────────────────────────────────
def check_ffmpeg():
    print("\n  FFmpeg capability check")
    try:
        import composer
        caps = composer.ffmpeg_capabilities()
    except Exception as exc:
        print(f"    ✗ could not run check ({exc})")
        return False

    def mark(ok):
        return "✓" if ok else "✗"

    print(f"    {mark(caps.get('ffmpeg'))} ffmpeg")
    print(f"    {mark(caps.get('ffprobe'))} ffprobe")
    print(f"    {mark(caps.get('subtitles'))} subtitles filter (libass) "
          f"— needed for burned-in captions")
    for f in ("sidechaincompress", "amix", "apad", "atrim", "tpad"):
        print(f"    {mark(caps.get(f))} {f}")
    if not caps.get("subtitles"):
        print("    → Captions need FFmpeg built with libass. On Debian/Ubuntu the"
              " default 'ffmpeg' package includes it; or use a static build from"
              " johnvansickle.com / ffmpeg.org.")
    return bool(caps.get("ffmpeg") and caps.get("subtitles"))


def check_python_deps():
    print("\n  Python dependencies")
    for mod, note in [("manim", "animation"), ("edge_tts", "online voice"),
                      ("numpy", "math"), ("PIL", "images")]:
        try:
            __import__(mod)
            print(f"    ✓ {mod} ({note})")
        except ImportError:
            print(f"    ✗ {mod} ({note}) — pip install -r requirements.txt")
    for mod in ("piper", "kokoro", "pyttsx3"):
        try:
            __import__(mod)
            print(f"    ✓ {mod} (optional)")
        except ImportError:
            print(f"    · {mod} not installed (optional)")


# ── entry point ────────────────────────────────────────────────────────────────
def run(check_only=False, skip_music=False):
    print("=" * 58)
    print("  Shorts/Reels Generator — setup")
    print("=" * 58)

    check_python_deps()
    ff_ok = check_ffmpeg()

    if not check_only:
        download_piper_voice()
        if not skip_music:
            download_music()

    print("\n" + "=" * 58)
    if ff_ok:
        print("  Ready. Try:  python generate.py script script_example.json -q preview")
    else:
        print("  FFmpeg/libass issue above — fix it before burning captions.")
    print("=" * 58 + "\n")


if __name__ == "__main__":
    run(check_only=("--check" in sys.argv), skip_music=("--no-music" in sys.argv))
