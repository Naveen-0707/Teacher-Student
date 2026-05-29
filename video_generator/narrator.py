"""
narrator.py – pluggable text-to-speech with a common result contract.

Backends
--------
  edge     edge-tts  – Microsoft neural voices, online, free, NO api key.
                       Streams audio + word-boundary timestamps (best captions).
  piper    Piper TTS – offline, open-source, natural. No native word timing →
                       phrase-level fallback.
  kokoro   Kokoro    – offline, open-source (optional dependency).
  pyttsx3  pyttsx3   – offline, robotic, last-resort fallback.
  recorded             – use a user-supplied audio file (truly human voice);
                       timing derived from the script text + measured duration.

Every backend returns a TTSResult so callers never branch on the engine:

    TTSResult(ok, audio_path, word_timings, duration, engine)
      word_timings : list[(word, start_s, end_s)]   ([] if unavailable)
"""

import os
import re
import subprocess
import sys
import wave
from dataclasses import dataclass, field
from pathlib import Path

# Project modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as appcfg


# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class TTSResult:
    ok: bool
    audio_path: str | None = None
    word_timings: list = field(default_factory=list)   # (word, start, end)
    duration: float = 0.0
    engine: str = ""


# ── small ffprobe helper (avoid importing composer at module load) ───────────────
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


# ── text helpers ────────────────────────────────────────────────────────────────
def _split_phrases(text: str) -> list:
    """Split narration into readable phrases for phrase-level timing."""
    parts = re.split(r"(?<=[.!?;:])\s+|\n+", text.strip())
    parts = [p.strip() for p in parts if p.strip()]
    out = []
    for p in parts:
        if len(p) > 90 and "," in p:
            out.extend(s.strip() for s in p.split(",") if s.strip())
        else:
            out.append(p)
    return out or [text.strip()]


def _distribute_words(phrase: str, start: float, end: float) -> list:
    """Spread a phrase's [start,end] across its words by character weight."""
    words = phrase.split()
    if not words:
        return []
    weights = [len(w) + 1 for w in words]
    total = sum(weights)
    span = max(0.0, end - start)
    res, t = [], start
    for w, wt in zip(words, weights):
        d = span * wt / total
        res.append((w, t, t + d))
        t += d
    return res


def _concat_audio(parts: list, out_path: str) -> bool:
    """Concatenate same-codec audio files via the FFmpeg concat demuxer."""
    parts = [p for p in parts if Path(p).exists()]
    if not parts:
        return False
    if len(parts) == 1:
        import shutil
        shutil.copy(parts[0], out_path)
        return True
    listf = Path(out_path).with_suffix(".txt")
    listf.write_text("\n".join(f"file '{Path(p).resolve()}'" for p in parts))
    r = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(out_path)],
        capture_output=True, text=True,
    )
    listf.unlink(missing_ok=True)
    return r.returncode == 0 and Path(out_path).exists()


# ── generic phrase-level pipeline (for engines without word timing) ──────────────
def _phrase_level(text, output_path, synth_one, tmp_prefix):
    """synth_one(phrase, out_wav) -> bool. Builds audio + pseudo-word timings."""
    phrases = _split_phrases(text)
    tmp_dir = Path(output_path).parent
    part_paths, spans, t = [], [], 0.0

    for i, phrase in enumerate(phrases):
        pw = tmp_dir / f"{tmp_prefix}_p{i:02d}.wav"
        if not synth_one(phrase, str(pw)):
            continue
        dur = _duration(str(pw))
        if dur <= 0:
            continue
        spans.append((phrase, t, t + dur))
        t += dur
        part_paths.append(str(pw))

    if not part_paths:
        return False, [], 0.0

    if not _concat_audio(part_paths, output_path):
        return False, [], 0.0

    word_timings = []
    for phrase, s, e in spans:
        word_timings.extend(_distribute_words(phrase, s, e))

    # cleanup phrase parts
    for p in part_paths:
        Path(p).unlink(missing_ok=True)

    return True, word_timings, _duration(output_path)


# ── backend: edge-tts (default) ──────────────────────────────────────────────────
def _tts_edge(text, output_path, voice) -> TTSResult:
    try:
        import asyncio
        import edge_tts
    except ImportError:
        print("  [narrator] edge-tts not installed → pip install edge-tts")
        return TTSResult(False, engine="edge")

    timings = []

    async def _run():
        communicate = edge_tts.Communicate(text, voice)
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    start = chunk["offset"] / 1e7
                    dur = chunk["duration"] / 1e7
                    timings.append((chunk["text"], start, start + dur))

    try:
        asyncio.run(_run())
    except Exception as exc:                       # network / service error
        print(f"  [narrator] edge-tts failed ({exc}); will try offline fallback")
        return TTSResult(False, engine="edge")

    if not Path(output_path).exists():
        return TTSResult(False, engine="edge")
    return TTSResult(True, output_path, timings, _duration(output_path), "edge")


# ── backend: Piper (offline) ─────────────────────────────────────────────────────
def _piper_model_paths(voice):
    name = voice or appcfg.PIPER_DEFAULT_VOICE
    onnx = Path(appcfg.PIPER_DIR) / f"{name}.onnx"
    cfg = Path(appcfg.PIPER_DIR) / f"{name}.onnx.json"
    return onnx, cfg


def _tts_piper(text, output_path, voice) -> TTSResult:
    onnx, cfg = _piper_model_paths(voice)
    if not onnx.exists():
        print(f"  [narrator] Piper voice not found: {onnx}")
        print("            Run:  python generate.py setup")
        return TTSResult(False, engine="piper")

    def synth_one(phrase, out_wav) -> bool:
        # Prefer the console script, fall back to `python -m piper`.
        cmds = [
            ["piper", "--model", str(onnx), "--config", str(cfg),
             "--output_file", out_wav],
            [sys.executable, "-m", "piper", "--model", str(onnx),
             "--config", str(cfg), "--output_file", out_wav],
        ]
        for cmd in cmds:
            try:
                r = subprocess.run(cmd, input=phrase.encode("utf-8"),
                                   capture_output=True)
                if r.returncode == 0 and Path(out_wav).exists():
                    return True
            except FileNotFoundError:
                continue
        return False

    ok, timings, dur = _phrase_level(text, output_path, synth_one, "piper")
    return TTSResult(ok, output_path if ok else None, timings, dur, "piper")


# ── backend: Kokoro (offline, optional) ──────────────────────────────────────────
def _tts_kokoro(text, output_path, voice) -> TTSResult:
    try:
        import soundfile as sf
        from kokoro import KPipeline
    except ImportError:
        print("  [narrator] kokoro not installed → pip install kokoro soundfile")
        return TTSResult(False, engine="kokoro")

    pipeline = KPipeline(lang_code="a")          # 'a' = American English
    kvoice = voice if (voice and voice.startswith("a")) else "af_heart"

    def synth_one(phrase, out_wav) -> bool:
        try:
            chunks = list(pipeline(phrase, voice=kvoice))
            import numpy as np
            audio = np.concatenate([c[2] for c in chunks]) if chunks else None
            if audio is None:
                return False
            sf.write(out_wav, audio, 24000)
            return Path(out_wav).exists()
        except Exception as exc:
            print(f"  [narrator] kokoro error: {exc}")
            return False

    ok, timings, dur = _phrase_level(text, output_path, synth_one, "kokoro")
    return TTSResult(ok, output_path if ok else None, timings, dur, "kokoro")


# ── backend: pyttsx3 (offline, robotic, last resort) ─────────────────────────────
def _tts_pyttsx3(text, output_path, voice) -> TTSResult:
    try:
        import pyttsx3
    except ImportError:
        print("  [narrator] pyttsx3 not installed → pip install pyttsx3")
        return TTSResult(False, engine="pyttsx3")

    def synth_one(phrase, out_wav) -> bool:
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 155)
            engine.save_to_file(phrase, out_wav)
            engine.runAndWait()
            return Path(out_wav).exists()
        except Exception:
            return False

    ok, timings, dur = _phrase_level(text, output_path, synth_one, "pyttsx3")
    return TTSResult(ok, output_path if ok else None, timings, dur, "pyttsx3")


# ── backend: recorded (user-supplied human voice) ────────────────────────────────
def _tts_recorded(text, output_path, audio_file) -> TTSResult:
    src = Path(audio_file) if audio_file else None
    if not src or not src.exists():
        print(f"  [narrator] recorded audio_file not found: {audio_file}")
        return TTSResult(False, engine="recorded")
    import shutil
    shutil.copy(str(src), output_path)
    dur = _duration(output_path)
    # Distribute the whole script across the clip's measured duration.
    timings = []
    phrases = _split_phrases(text)
    if phrases and dur > 0:
        # weight each phrase by its character length
        weights = [len(p) + 1 for p in phrases]
        total = sum(weights)
        t = 0.0
        for p, wt in zip(phrases, weights):
            span = dur * wt / total
            timings.extend(_distribute_words(p, t, t + span))
            t += span
    return TTSResult(True, output_path, timings, dur, "recorded")


# ── public API ───────────────────────────────────────────────────────────────────
_BACKENDS = {
    "edge": _tts_edge,
    "piper": _tts_piper,
    "kokoro": _tts_kokoro,
    "pyttsx3": _tts_pyttsx3,
    # legacy aliases
    "online": _tts_edge,
    "offline": _tts_pyttsx3,
}


def generate(text, output_path, engine="edge", voice=None,
             want_timings=True, audio_file=None) -> TTSResult:
    """
    Generate narration. Returns a TTSResult.

    `engine` : edge | piper | kokoro | pyttsx3 | recorded (+ legacy online/offline)
    `voice`  : edge voice name, or Piper model name; ignored where N/A
    `audio_file` : for engine='recorded', the human voice file to use
    """
    if not text or not text.strip():
        return TTSResult(False, engine=engine)

    preview = (text[:57] + "…") if len(text) > 58 else text
    print(f"  [narrator:{engine}] \"{preview}\"")

    if engine == "recorded":
        return _tts_recorded(text, output_path, audio_file)

    backend = _BACKENDS.get(engine, _tts_edge)
    result = backend(text, output_path, voice)

    # Auto-fallback: edge needs internet; drop to offline Piper, else pyttsx3.
    if not result.ok and engine in ("edge", "online"):
        print("  [narrator] falling back to offline Piper …")
        result = _tts_piper(text, output_path, voice)
        if not result.ok:
            print("  [narrator] falling back to pyttsx3 …")
            result = _tts_pyttsx3(text, output_path, voice)

    if not result.ok:
        print(f"  [narrator] WARNING: no audio generated for: {preview}")
    return result


# ── CLI helper ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python narrator.py 'text' out.mp3 [engine] [voice]")
        sys.exit(1)
    txt = sys.argv[1]
    out = sys.argv[2]
    eng = sys.argv[3] if len(sys.argv) > 3 else "edge"
    voc = sys.argv[4] if len(sys.argv) > 4 else None
    res = generate(txt, out, engine=eng, voice=voc)
    print(f"\nok={res.ok} engine={res.engine} duration={res.duration:.2f}s "
          f"words={len(res.word_timings)}")
    for w, s, e in res.word_timings[:12]:
        print(f"  {s:6.2f}–{e:6.2f}  {w}")
