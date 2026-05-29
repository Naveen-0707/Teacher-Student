"""
captions.py – build burned-in-ready ASS subtitles from word/phrase timings.

Captions are effectively mandatory for Shorts/Reels (≈85% watch muted; large
retention boost). This module turns a list of (word, start, end) timings into a
styled .ass file: bold, high-contrast, positioned in the safe band, with optional
karaoke word-by-word highlighting. The file is later burned in with FFmpeg+libass
(see composer.burn_subtitles).
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as appcfg


# ── time formatting ──────────────────────────────────────────────────────────
def _format_ts(sec: float) -> str:
    """Seconds → ASS timestamp  H:MM:SS.cs  (centiseconds)."""
    if sec < 0:
        sec = 0.0
    cs = int(round(sec * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


# ── grouping words into 1–2 line events ──────────────────────────────────────
def _group_events(word_timings, max_chars, max_lines):
    """Greedy-wrap words into events; each event is up to `max_lines` lines."""
    events = []
    cur = [[]]

    def line_len(line):
        return sum(len(w[0]) + 1 for w in line)

    for wt in word_timings:
        word = wt[0]
        if cur[-1] and line_len(cur[-1]) + len(word) + 1 > max_chars:
            if len(cur) >= max_lines:
                events.append(cur)
                cur = [[]]
            else:
                cur.append([])
        cur[-1].append(wt)

    if any(line for line in cur):
        events.append(cur)
    return events


def _event_text(lines, karaoke):
    """Return (text, start, end) for one event. `lines` = list of word-lists."""
    flat = [w for line in lines for w in line]
    if not flat:
        return "", 0.0, 0.0
    start = flat[0][1]
    end = flat[-1][2]

    if not karaoke:
        text = r"\N".join(
            " ".join(w[0] for w in line) for line in lines if line
        )
        return text, start, end

    # Karaoke: one continuous \k timeline across both lines.
    parts, cursor, first_line = [], 0.0, True
    for line in lines:
        if not line:
            continue
        if not first_line:
            parts.append(r"\N")
        first_line = False
        for (w, s, e) in line:
            rel_s, rel_e = s - start, e - start
            gap = rel_s - cursor
            if gap > 0.03:
                parts.append(r"{\k%d}" % round(gap * 100))
                cursor = rel_s
            dur = max(0.0, rel_e - cursor)
            parts.append(r"{\k%d}%s " % (round(dur * 100), w))
            cursor = rel_e
    return "".join(parts).strip(), start, end


# ── ASS file header ──────────────────────────────────────────────────────────
def _ass_header(style, video_w, video_h, karaoke):
    # In karaoke, PrimaryColour is the "sung" fill, SecondaryColour the unsung.
    if karaoke:
        primary = style["highlight"]      # word turns this colour when spoken
        secondary = style["primary"]      # upcoming words show this
    else:
        primary = style["primary"]
        secondary = style["primary"]

    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_w}
PlayResY: {video_h}
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style['font']},{style['font_size_px']},{primary},{secondary},{style['outline']},&H64000000,{style['bold']},0,0,0,100,100,0,0,1,{style['outline_w']},{style['shadow']},{style['alignment']},{style['margin_l']},{style['margin_r']},{style['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


# ── public API ───────────────────────────────────────────────────────────────
def build_ass(word_timings, out_path, *, video_w=1080, video_h=1920,
              style=None, karaoke=None):
    """
    Write an .ass caption file. Returns the path, or None if there is nothing
    to render (so the caller can skip burning).
    """
    if not word_timings:
        return None

    style = dict(style or appcfg.CAPTION_STYLE[appcfg.DEFAULT_CAPTION_STYLE])
    if karaoke is None:
        karaoke = style.get("karaoke", True)

    max_chars = int(style.get("max_chars_per_line", 22))
    max_lines = int(style.get("max_lines", 2))

    events = _group_events(word_timings, max_chars, max_lines)
    if not events:
        return None

    lines_out = [_ass_header(style, video_w, video_h, karaoke)]
    for ev in events:
        text, start, end = _event_text(ev, karaoke)
        if not text or end <= start:
            continue
        lines_out.append(
            f"Dialogue: 0,{_format_ts(start)},{_format_ts(end)},"
            f"Default,,0,0,0,,{text}"
        )

    Path(out_path).write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    return str(out_path)


# ── CLI smoke test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo = [
        ("Here", 0.0, 0.35), ("are", 0.35, 0.55), ("five", 0.55, 0.9),
        ("AI", 0.9, 1.2), ("facts", 1.2, 1.7), ("that", 1.7, 1.95),
        ("will", 1.95, 2.2), ("blow", 2.2, 2.6), ("your", 2.6, 2.85),
        ("mind", 2.85, 3.4),
    ]
    p = build_ass(demo, "demo_caption.ass")
    print("Wrote:", p)
    print(Path(p).read_text())
