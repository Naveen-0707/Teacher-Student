"""
narrator.py – Text-to-Speech engine for video narration.

Two modes:
  offline  pyttsx3  – no internet needed, basic voice quality
  online   edge-tts – needs internet, high-quality Microsoft neural voices

Good voices for content creators:
  Male   : en-US-GuyNeural, en-GB-RyanNeural, en-US-TonyNeural (deep/energetic)
  Female : en-US-JennyNeural, en-GB-SoniaNeural, en-US-AriaNeural
"""

from pathlib import Path


# ── offline (pyttsx3) ─────────────────────────────────────────────────────────

def _speak_offline(text: str, out: str, rate: int = 155) -> bool:
    try:
        import pyttsx3
    except ImportError:
        print("  [narrator] pyttsx3 not installed → pip install pyttsx3")
        return False

    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", 1.0)

    # Pick the best available English voice
    for v in engine.getProperty("voices"):
        name = v.name.lower()
        if any(k in name for k in ("english", "david", "zira", "mark")):
            engine.setProperty("voice", v.id)
            break

    engine.save_to_file(text, str(out))
    engine.runAndWait()
    return Path(out).exists()


# ── online (edge-tts) ─────────────────────────────────────────────────────────

def _speak_online(text: str, out: str, voice: str = "en-US-GuyNeural") -> bool:
    try:
        import asyncio
        import edge_tts
    except ImportError:
        print("  [narrator] edge-tts not installed → pip install edge-tts")
        return False

    async def _run():
        tts = edge_tts.Communicate(text, voice)
        await tts.save(str(out))

    import asyncio
    asyncio.run(_run())
    return Path(out).exists()


# ── public API ────────────────────────────────────────────────────────────────

def generate(text: str, output_path: str,
             engine: str = "offline",
             voice: str = "en-US-GuyNeural") -> bool:
    """
    Generate a narration audio file from text.

    Args:
        text        – what to say
        output_path – .mp3 / .wav path to write
        engine      – 'offline' (pyttsx3) or 'online' (edge-tts)
        voice       – voice name for edge-tts (ignored for offline)

    Returns True on success.
    """
    if not text.strip():
        return False

    preview = text[:60] + "…" if len(text) > 60 else text
    print(f"  [narrator:{engine}] \"{preview}\"")

    if engine == "online":
        ok = _speak_online(text, output_path, voice)
    else:
        ok = _speak_offline(text, output_path)

    if not ok:
        print(f"  [narrator] WARNING: audio not generated for: {preview}")
    return ok


# ── CLI helper ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python narrator.py 'your text here' output.mp3 [online] [voice]")
        sys.exit(1)

    txt    = sys.argv[1]
    out    = sys.argv[2]
    eng    = sys.argv[3] if len(sys.argv) > 3 else "offline"
    voc    = sys.argv[4] if len(sys.argv) > 4 else "en-US-GuyNeural"

    ok = generate(txt, out, engine=eng, voice=voc)
    print("Done!" if ok else "Failed.")
