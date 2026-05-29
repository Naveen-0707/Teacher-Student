"""
Script-driven Manim scenes for vertical Shorts/Reels (9:16).
generate.py writes _active_scene.json before each render; scenes read it here.

All scenes subclass ShortsScene (base_scene.py), which fixes the 9:16 frame width
and provides safe-zone helpers so text/visuals never hide behind platform UI or
the burned-in caption band.

Templates:
  ScriptHookScene       – 1–2s pattern-interrupt hook (first thing viewers see)
  ScriptTitleScene      – customisable neon title card
  ScriptTextRevealScene – heading + auto-wrapped body text
  ScriptBulletScene     – title + animated bullet list
  ScriptStatsScene      – bar chart from your data
"""

import json
import os
import random
import sys
from pathlib import Path

from manim import *

# Make sibling modules importable when Manim loads this file directly.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base_scene import ShortsScene   # noqa: E402

# ── shared config loader ──────────────────────────────────────────────────────
_CFG_FILE = Path(__file__).parent.parent / "_active_scene.json"


def _cfg() -> dict:
    try:
        return json.loads(_CFG_FILE.read_text())
    except Exception:
        return {}


# ── palette ───────────────────────────────────────────────────────────────────
BG = "#0a0a0f"
DIM_C = "#1a1a2e"
WHITE_C = "#ffffff"
MUTED_C = "#888899"

ACCENTS = {
    "cyan": "#00f5ff", "purple": "#9b00ff", "green": "#00ff41",
    "gold": "#ffaa00", "pink": "#ff0090", "orange": "#ff6b00",
}


def _accent(cfg: dict) -> str:
    return ACCENTS.get(cfg.get("accent", "cyan"), "#00f5ff")


def _wrap_strings(text, font_size, max_w):
    """Greedy word-wrap into a list of line strings that each fit max_w."""
    words = text.split()
    lines, cur = [], []
    for w in words:
        cur.append(w)
        if Text(" ".join(cur), font_size=font_size).width > max_w:
            cur.pop()
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines or [text]


# ─────────────────────────────────────────────────────────────────────────────
class ScriptHookScene(ShortsScene):
    """1–2s pattern-interrupt hook. Keys: hook_text, subtext, accent."""

    def construct(self):
        cfg = _cfg()
        self.camera.background_color = self.BG
        acc = _accent(cfg)
        rect = self.content_rect()
        captions_on = cfg.get("captions", True)

        hook_txt = cfg.get("hook_text") or cfg.get("title") or "Wait for it…"
        subtext = cfg.get("subtext", "")

        # Pattern-interrupt flash (grabs attention in frame 1)
        flash = Rectangle(width=config.frame_width, height=config.frame_height,
                          fill_color=acc, fill_opacity=1, stroke_width=0)
        self.add(flash)
        self.wait(0.08)
        self.remove(flash)

        hook = self.fit_text(hook_txt, max_w=rect["width"],
                             sizes=[84, 68, 54, 44], color=WHITE_C, weight=BOLD)
        self.place_in_content(hook, captions_on=captions_on)
        self.play(GrowFromCenter(hook), run_time=0.3)

        # RGB glitch beats
        for _ in range(2):
            r = hook.copy().set_color(acc).shift(RIGHT * 0.08)
            b = hook.copy().set_color(BLUE).shift(LEFT * 0.08)
            self.add(r, b); self.wait(0.04); self.remove(r, b); self.wait(0.04)

        # quick scale pulses (fast-cut feel)
        self.play(hook.animate.scale(1.08), rate_func=there_and_back, run_time=0.16)
        self.play(hook.animate.scale(1.08), rate_func=there_and_back, run_time=0.16)

        if subtext:
            sub = self.fit_text(subtext, max_w=rect["width"], sizes=[30, 24],
                                color=acc)
            sub.next_to(hook, DOWN, buff=0.4)
            self.play(FadeIn(sub, shift=UP * 0.15), run_time=0.3)

        self.wait(0.5)


# ─────────────────────────────────────────────────────────────────────────────
class ScriptTitleScene(ShortsScene):
    """Neon title card. Keys: title, subtitle, channel, accent."""

    def construct(self):
        cfg = _cfg()
        self.camera.background_color = self.BG
        acc = _accent(cfg)
        rect = self.content_rect()
        cx = rect["center_x"]
        captions_on = cfg.get("captions", True)
        lower = self.caption_anchor()[1] if captions_on else rect["bottom"]

        title_txt = cfg.get("title", "My Video")
        subtitle_txt = cfg.get("subtitle", "")
        channel_txt = cfg.get("channel", "@YourChannel")

        self.play(Create(self._traces(acc)), run_time=0.8)

        # accent sidebar
        bar = Rectangle(width=0.12, height=min(4.0, rect["top"] - lower),
                        fill_color=acc, fill_opacity=1, stroke_width=0)
        bar.move_to([rect["left"] + 0.1, (rect["top"] + lower) / 2, 0])
        self.play(GrowFromEdge(bar, DOWN), run_time=0.4)

        # title
        title = self.fit_text(title_txt, max_w=rect["width"] - 0.4,
                             sizes=[64, 52, 42, 34], color=WHITE_C, weight=BOLD)
        title.move_to([cx, rect["top"] - title.height / 2 - 0.5, 0])
        self.play(FadeIn(title, shift=RIGHT * 0.05), run_time=0.45)
        for _ in range(2):
            r = title.copy().set_color(RED).shift(RIGHT * 0.07)
            b = title.copy().set_color(BLUE).shift(LEFT * 0.07)
            self.add(r, b); self.wait(0.05); self.remove(r, b); self.wait(0.05)

        last = title
        if subtitle_txt:
            sub = self.fit_text(subtitle_txt, max_w=rect["width"] - 0.4,
                                sizes=[28, 24, 20], color=MUTED_C)
            sub.next_to(title, DOWN, buff=0.4)
            self.play(Write(sub), run_time=0.6)
            last = sub

        div = Line(LEFT * 2.6, RIGHT * 2.6, color=acc, stroke_width=1.5)
        div.next_to(last, DOWN, buff=0.45).set_x(cx)
        self.play(Create(div), run_time=0.3)

        channel = Text(channel_txt, font_size=26, color=acc)
        channel.move_to([cx, lower + 0.4, 0])
        self.play(FadeIn(channel))
        self.wait(1.5)

    @staticmethod
    def _traces(acc):
        random.seed(9)
        g = VGroup()
        for _ in range(16):
            x1 = random.uniform(-4.0, 4.0)
            y1 = random.uniform(-7.0, 7.0)
            xm = x1 + random.uniform(-1.4, 1.4)
            y2 = y1 + random.uniform(-2, 2)
            g.add(
                Line([x1, y1, 0], [xm, y1, 0], color=DIM_C, stroke_width=0.9),
                Line([xm, y1, 0], [xm, y2, 0], color=DIM_C, stroke_width=0.9),
                Dot([xm, y1, 0], radius=0.04, color=acc, fill_opacity=0.4),
            )
        return g


# ─────────────────────────────────────────────────────────────────────────────
class ScriptTextRevealScene(ShortsScene):
    """Heading + auto-wrapped body. Keys: heading, body, accent."""

    def construct(self):
        cfg = _cfg()
        self.camera.background_color = self.BG
        acc = _accent(cfg)
        rect = self.content_rect()
        cx = rect["center_x"]
        captions_on = cfg.get("captions", True)
        lower = self.caption_anchor()[1] if captions_on else rect["bottom"]

        heading_txt = cfg.get("heading", "")
        body_txt = cfg.get("body", "")

        stripe = Rectangle(width=config.frame_width, height=0.1,
                           fill_color=acc, fill_opacity=1, stroke_width=0)
        stripe.move_to([0, rect["top"] + 0.3, 0])
        self.add(stripe)

        body_top = rect["top"]
        if heading_txt:
            h = self.fit_text(heading_txt, max_w=rect["width"],
                             sizes=[56, 44, 36], color=acc, weight=BOLD)
            h.move_to([cx, rect["top"] - h.height / 2 - 0.2, 0])
            self.play(Write(h), run_time=0.6)
            div = Line(LEFT * 2.6, RIGHT * 2.6, color=acc,
                       stroke_width=1.2, stroke_opacity=0.6)
            div.next_to(h, DOWN, buff=0.3).set_x(cx)
            self.play(Create(div), run_time=0.25)
            body_top = div.get_bottom()[1] - 0.3

        if body_txt:
            strs = _wrap_strings(body_txt, font_size=34, max_w=rect["width"])
            lines = VGroup(*[Text(s, font_size=34, color=WHITE_C) for s in strs])
            lines.arrange(DOWN, buff=0.32, aligned_edge=LEFT)
            lines.move_to([cx, (body_top + lower) / 2, 0])
            max_h = max(1.0, body_top - lower)
            if lines.height > max_h:
                lines.scale(max_h / lines.height)
            for lm, s in zip(lines, strs):
                self.play(Write(lm), run_time=max(0.4, len(s) * 0.022))
                self.wait(0.08)
        self.wait(1.2)


# ─────────────────────────────────────────────────────────────────────────────
class ScriptBulletScene(ShortsScene):
    """Title + animated bullets. Keys: title, bullets[], accent."""

    def construct(self):
        cfg = _cfg()
        self.camera.background_color = self.BG
        acc = _accent(cfg)
        rect = self.content_rect()
        cx = rect["center_x"]
        captions_on = cfg.get("captions", True)
        lower = self.caption_anchor()[1] if captions_on else rect["bottom"]

        title_txt = cfg.get("title", "Key Points")
        bullets = cfg.get("bullets", [])[:6]

        title = self.fit_text(title_txt, max_w=rect["width"],
                             sizes=[50, 40, 32], color=WHITE_C, weight=BOLD)
        title.move_to([cx, rect["top"] - title.height / 2 - 0.2, 0])
        div = Line(LEFT * 2.8, RIGHT * 2.8, color=acc, stroke_width=1.5)
        div.next_to(title, DOWN, buff=0.25).set_x(cx)
        self.play(Write(title), run_time=0.5)
        self.play(Create(div), run_time=0.3)

        colors = list(ACCENTS.values())
        rows = VGroup()
        for i, t in enumerate(bullets):
            col = colors[i % len(colors)]
            marker = Text("▶", font_size=24, color=col)
            label = self.fit_text(t, max_w=rect["width"] - 0.7,
                                  sizes=[30, 26, 22], color=WHITE_C)
            label.next_to(marker, RIGHT, buff=0.22)
            rows.add(VGroup(marker, label))
        rows.arrange(DOWN, buff=0.4, aligned_edge=LEFT)

        top_b = div.get_bottom()[1] - 0.3
        rows.move_to([cx, (top_b + lower) / 2, 0])
        max_h = max(1.0, top_b - lower)
        if rows.height > max_h:
            rows.scale(max_h / rows.height)

        for row in rows:
            self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.4)
            self.wait(0.15)
        self.wait(1.2)


# ─────────────────────────────────────────────────────────────────────────────
class ScriptStatsScene(ShortsScene):
    """Animated bar chart. Keys: chart_title, labels[], values[], accent."""

    def construct(self):
        cfg = _cfg()
        self.camera.background_color = self.BG
        acc = _accent(cfg)
        rect = self.content_rect()
        cx = rect["center_x"]
        captions_on = cfg.get("captions", True)
        lower = self.caption_anchor()[1] if captions_on else rect["bottom"]

        chart_title = cfg.get("chart_title", "Stats")
        labels = cfg.get("labels", ["A", "B", "C", "D"])
        values = cfg.get("values", [70, 85, 60, 90])

        title = self.fit_text(chart_title, max_w=rect["width"],
                             sizes=[44, 36, 30], color=WHITE_C, weight=BOLD)
        title.move_to([cx, rect["top"] - title.height / 2 - 0.2, 0])
        self.play(Write(title), run_time=0.7)

        base_y = lower + 0.6                       # room for x-axis labels
        chart_top = title.get_bottom()[1] - 0.5
        max_h = max(1.0, chart_top - base_y - 0.5)  # room for score labels

        n = max(1, len(labels))
        avail_w = rect["width"] - 0.4
        bar_w = min(0.9, avail_w / (n * 1.4))
        gap = bar_w * 0.4
        total_w = n * (bar_w + gap) - gap
        x0 = cx - total_w / 2
        maxv = max(values) if values else 1
        heights = [(v / maxv) * max_h for v in values]

        baseline = Line([x0 - 0.25, base_y, 0],
                        [x0 + total_w + 0.25, base_y, 0],
                        color=MUTED_C, stroke_width=1.5)
        self.play(Create(baseline), run_time=0.3)

        colors = list(ACCENTS.values())
        bars, name_mobs = [], VGroup()
        for i, (lbl, val, h) in enumerate(zip(labels, values, heights)):
            x = x0 + i * (bar_w + gap) + bar_w / 2
            col = colors[i % len(colors)]
            bar = Rectangle(width=bar_w, height=0.02, fill_color=col,
                            fill_opacity=0.85, stroke_width=0)
            bar.move_to([x, base_y, 0], aligned_edge=DOWN)
            name = Text(str(lbl), font_size=17, color=WHITE_C)
            name.move_to([x, base_y - 0.32, 0])
            score = Text(str(val), font_size=19, color=col, weight=BOLD)
            score.move_to([x, base_y + h + 0.25, 0]).set_opacity(0)
            bars.append((bar, h, score))
            name_mobs.add(name)

        self.play(FadeIn(name_mobs), run_time=0.4)
        self.add(*[b for b, _, _ in bars])

        grow = []
        for bar, h, _ in bars:
            target = bar.copy()
            target.stretch_to_fit_height(max(0.02, h))
            target.move_to([bar.get_x(), base_y, 0], aligned_edge=DOWN)
            grow.append(Transform(bar, target))
        self.play(*grow, run_time=2.0, rate_func=ease_out_cubic)

        self.play(*[s.animate.set_opacity(1) for _, _, s in bars], run_time=0.4)
        self.add(*[s for _, _, s in bars])

        top_i = heights.index(max(heights))
        top_x = x0 + top_i * (bar_w + gap) + bar_w / 2
        crown = Text("👑", font_size=28)
        crown.move_to([top_x, base_y + heights[top_i] + 0.62, 0])
        self.play(FadeIn(crown, shift=DOWN * 0.2))
        self.wait(1.2)
