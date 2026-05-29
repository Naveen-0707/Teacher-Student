"""
Script-driven Manim scenes for YouTube Shorts (9:16 vertical).
generate.py writes _active_scene.json before each render; scenes read it here.

Templates:
  ScriptTitleScene      – customisable neon title card
  ScriptTextRevealScene – heading + body text with word-by-word reveal
  ScriptBulletScene     – title + animated bullet-point list
  ScriptStatsScene      – bar chart with labels/values from script
"""

import json
import random
from pathlib import Path
from manim import *

# ── shared config loader ──────────────────────────────────────────────────────
_CFG_FILE = Path(__file__).parent.parent / "_active_scene.json"

def _cfg() -> dict:
    try:
        return json.loads(_CFG_FILE.read_text())
    except Exception:
        return {}

# ── palette ───────────────────────────────────────────────────────────────────
BG      = "#0a0a0f"
DIM_C   = "#1a1a2e"
WHITE_C = "#ffffff"
MUTED_C = "#888899"

ACCENTS = {
    "cyan":   "#00f5ff",
    "purple": "#9b00ff",
    "green":  "#00ff41",
    "gold":   "#ffaa00",
    "pink":   "#ff0090",
    "orange": "#ff6b00",
}


def _accent(cfg: dict) -> str:
    return ACCENTS.get(cfg.get("accent", "cyan"), "#00f5ff")


# ─────────────────────────────────────────────────────────────────────────────
class ScriptTitleScene(Scene):
    """
    Fully customisable neon title card.
    Script keys: title, subtitle, channel, accent
    """

    def construct(self):
        cfg  = _cfg()
        self.camera.background_color = BG
        acc  = _accent(cfg)

        title_txt    = cfg.get("title",   "My Video")
        subtitle_txt = cfg.get("subtitle", "")
        channel_txt  = cfg.get("channel",  "@YourChannel")

        # ── Circuit-trace background ──────────────────────────────────────────
        self.play(Create(self._traces(acc)), run_time=0.8)

        # ── Accent sidebar bar ────────────────────────────────────────────────
        bar = Rectangle(width=0.12, height=4.5,
                        fill_color=acc, fill_opacity=1, stroke_width=0)
        bar.to_edge(LEFT, buff=0.5)
        self.play(GrowFromEdge(bar, DOWN), run_time=0.4)

        # ── Title ─────────────────────────────────────────────────────────────
        title = self._fit_text(title_txt, max_w=7.6, sizes=[62, 50, 40],
                               color=WHITE_C, weight=BOLD)
        title.move_to(UP * 1.3)

        self.play(FadeIn(title, shift=RIGHT * 0.05), run_time=0.45)

        # Glitch flash (2×)
        for _ in range(2):
            r = title.copy().set_color(RED).shift(RIGHT * 0.07)
            b = title.copy().set_color(BLUE).shift(LEFT * 0.07)
            self.add(r, b);  self.wait(0.05);  self.remove(r, b);  self.wait(0.05)

        # ── Subtitle ──────────────────────────────────────────────────────────
        if subtitle_txt:
            sub = self._fit_text(subtitle_txt, max_w=7.6, sizes=[26, 22, 18],
                                  color=MUTED_C)
            sub.next_to(title, DOWN, buff=0.45)
            self.play(Write(sub), run_time=0.6)

        # ── Divider ───────────────────────────────────────────────────────────
        div = Line(LEFT * 3.2, RIGHT * 3.2, color=acc, stroke_width=1.5)
        div.move_to(DOWN * 0.9)
        self.play(Create(div), run_time=0.3)

        # ── Channel tag ───────────────────────────────────────────────────────
        channel = Text(channel_txt, font_size=26, color=acc)
        channel.to_edge(DOWN, buff=0.9)
        self.play(FadeIn(channel))

        self.wait(1.5)

    # ── helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _fit_text(s, max_w, sizes, **kwargs):
        for fs in sizes:
            t = Text(s, font_size=fs, **kwargs)
            if t.width <= max_w:
                return t
        return Text(s, font_size=sizes[-1], **kwargs)

    @staticmethod
    def _traces(acc):
        random.seed(9)
        g = VGroup()
        for _ in range(18):
            x1 = random.uniform(-4.5, 4.5)
            y1 = random.uniform(-8.5, 8.5)
            xm = x1 + random.uniform(-1.5, 1.5)
            y2 = y1 + random.uniform(-2,   2)
            g.add(
                Line([x1,y1,0],[xm,y1,0], color=DIM_C, stroke_width=0.9),
                Line([xm,y1,0],[xm,y2,0], color=DIM_C, stroke_width=0.9),
                Dot( [xm,y1,0], radius=0.04, color=acc, fill_opacity=0.4),
            )
        return g


# ─────────────────────────────────────────────────────────────────────────────
class ScriptTextRevealScene(Scene):
    """
    Large heading + auto-wrapped body text revealed word-by-word.
    Script keys: heading, body, accent
    """

    def construct(self):
        cfg  = _cfg()
        self.camera.background_color = BG
        acc  = _accent(cfg)

        heading_txt = cfg.get("heading", "")
        body_txt    = cfg.get("body",    "")

        # Top accent stripe
        stripe = Rectangle(
            width=config.frame_width, height=0.1,
            fill_color=acc, fill_opacity=1, stroke_width=0,
        )
        stripe.to_edge(UP, buff=0)
        self.add(stripe)

        y_cursor = UP * 4.5

        # ── Heading ───────────────────────────────────────────────────────────
        if heading_txt:
            h = Text(heading_txt, font_size=56, color=acc, weight=BOLD)
            if h.width > 7.5:
                h = Text(heading_txt, font_size=42, color=acc, weight=BOLD)
            h.move_to(y_cursor)
            self.play(Write(h), run_time=0.6)
            y_cursor = h.get_bottom() + DOWN * 0.5

            div = Line(LEFT * 3.2, RIGHT * 3.2, color=acc,
                       stroke_width=1.2, stroke_opacity=0.6)
            div.move_to(y_cursor + DOWN * 0.1)
            self.play(Create(div), run_time=0.25)
            y_cursor = div.get_bottom() + DOWN * 0.4

        # ── Body: auto-wrap to 7.5 units wide ────────────────────────────────
        if body_txt:
            line_mobs = VGroup(*self._wrap(body_txt, font_size=32, max_w=7.5))
            line_mobs.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
            line_mobs.move_to(ORIGIN)
            if heading_txt:
                line_mobs.next_to(div, DOWN, buff=0.55)

            for lm in line_mobs:
                self.play(Write(lm), run_time=max(0.4, len(lm.original_text) * 0.025))
                self.wait(0.1)

        # ── Tag ───────────────────────────────────────────────────────────────
        tag = Text("#Shorts  #AI  #Tech", font_size=20, color=MUTED_C)
        tag.to_edge(DOWN, buff=0.8)
        self.play(FadeIn(tag))
        self.wait(1.5)

    @staticmethod
    def _wrap(text, font_size, max_w):
        words = text.split()
        lines, cur = [], []
        for w in words:
            cur.append(w)
            if Text(" ".join(cur), font_size=font_size).width > max_w:
                cur.pop()
                lines.append(" ".join(cur))
                cur = [w]
        if cur:
            lines.append(" ".join(cur))
        return [Text(l, font_size=font_size, color=WHITE_C) for l in lines]


# ─────────────────────────────────────────────────────────────────────────────
class ScriptBulletScene(Scene):
    """
    Title + animated bullet-point list (up to 6 items).
    Script keys: title, bullets (list of strings), accent
    """

    def construct(self):
        cfg  = _cfg()
        self.camera.background_color = BG
        acc  = _accent(cfg)

        title_txt = cfg.get("title",   "Key Points")
        bullets   = cfg.get("bullets", [])[:6]   # cap at 6

        # ── Title ─────────────────────────────────────────────────────────────
        title = Text(title_txt, font_size=50, color=WHITE_C, weight=BOLD)
        title.to_edge(UP, buff=0.65)

        div = Line(LEFT * 3.5, RIGHT * 3.5, color=acc, stroke_width=1.5)
        div.next_to(title, DOWN, buff=0.28)

        self.play(Write(title), run_time=0.5)
        self.play(Create(div),  run_time=0.3)

        # ── Bullets ───────────────────────────────────────────────────────────
        color_cycle = list(ACCENTS.values())
        rows = VGroup()

        for i, text in enumerate(bullets):
            col    = color_cycle[i % len(color_cycle)]
            marker = Text("▶", font_size=22, color=col)
            label  = Text(text, font_size=28, color=WHITE_C)
            if label.width > 6.8:
                label = Text(text, font_size=22, color=WHITE_C)
            label.next_to(marker, RIGHT, buff=0.22)
            rows.add(VGroup(marker, label))

        rows.arrange(DOWN, buff=0.48, aligned_edge=LEFT)

        # Center bullets in remaining vertical space
        space_top = div.get_bottom()[1]
        space_bot = -7.5
        rows.move_to([0, (space_top + space_bot) / 2, 0])

        for row in rows:
            self.play(FadeIn(row, shift=RIGHT * 0.35), run_time=0.4)
            self.wait(0.18)

        self.wait(1.5)


# ─────────────────────────────────────────────────────────────────────────────
class ScriptStatsScene(Scene):
    """
    Animated bar chart with your own data.
    Script keys: chart_title, labels (list), values (list), accent
    """

    BAR_W   = 0.75
    BAR_GAP = 0.3
    MAX_H   = 4.5

    def construct(self):
        cfg  = _cfg()
        self.camera.background_color = BG
        acc  = _accent(cfg)

        chart_title = cfg.get("chart_title", "Stats")
        labels      = cfg.get("labels",      ["A","B","C","D"])
        values      = cfg.get("values",      [70, 85, 60, 90])

        # Normalise: max value → MAX_H
        max_v   = max(values) if values else 1
        heights = [(v / max_v) * self.MAX_H for v in values]

        n      = len(labels)
        total_w = n * (self.BAR_W + self.BAR_GAP) - self.BAR_GAP
        x0     = -total_w / 2
        base_y = -4.0

        # ── Title ─────────────────────────────────────────────────────────────
        title = Text(chart_title, font_size=44, color=WHITE_C, weight=BOLD)
        title.to_edge(UP, buff=0.55)
        self.play(Write(title), run_time=0.7)

        # ── Baseline ──────────────────────────────────────────────────────────
        baseline = Line(
            [x0 - 0.3, base_y, 0],
            [x0 + total_w + 0.3, base_y, 0],
            color=MUTED_C, stroke_width=1.5,
        )
        self.play(Create(baseline), run_time=0.3)

        # ── Build bars ────────────────────────────────────────────────────────
        bar_colors = list(ACCENTS.values())
        bars, score_mobs, name_mobs = [], VGroup(), VGroup()

        for i, (lbl, val, h) in enumerate(zip(labels, values, heights)):
            x   = x0 + i * (self.BAR_W + self.BAR_GAP) + self.BAR_W / 2
            col = bar_colors[i % len(bar_colors)]

            bar = Rectangle(
                width=self.BAR_W, height=0.02,
                fill_color=col, fill_opacity=0.85, stroke_width=0,
            )
            bar.align_to([0, base_y, 0], DOWN)
            bar.move_to([x, base_y, 0], aligned_edge=DOWN)

            name = Text(str(lbl), font_size=17, color=WHITE_C)
            name.move_to([x, base_y - 0.42, 0])

            score = Text(str(val), font_size=19, color=col, weight=BOLD)
            score.move_to([x, base_y + h + 0.28, 0])
            score.set_opacity(0)

            bars.append((bar, h, score))
            name_mobs.add(name)

        self.play(FadeIn(name_mobs), run_time=0.4)
        self.add(*[b for b,_,_ in bars])

        # Grow bars
        grow = []
        for bar, h, _ in bars:
            target = bar.copy()
            target.stretch_to_fit_height(h)
            target.align_to([0, base_y, 0], DOWN)
            grow.append(Transform(bar, target))

        self.play(*grow, run_time=2.0, rate_func=ease_out_cubic)

        # Reveal scores
        self.play(*[s.animate.set_opacity(1) for _,_,s in bars], run_time=0.4)
        self.add(*[s for _,_,s in bars])

        # Crown on top bar
        top_i  = heights.index(max(heights))
        top_x  = x0 + top_i * (self.BAR_W + self.BAR_GAP) + self.BAR_W / 2
        crown  = Text("👑", font_size=28)
        crown.move_to([top_x, base_y + heights[top_i] + 0.72, 0])
        self.play(FadeIn(crown, shift=DOWN * 0.2))

        self.wait(1.5)
