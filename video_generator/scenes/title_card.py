"""
Title-card scenes for YouTube Shorts (9:16 vertical).
Scenes: TechTitleScene, GamingTitleScene
"""

import os
import random
import sys

from manim import *

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base_scene import ShortsScene   # noqa: E402

BG       = "#0a0a0f"
CYAN_C   = "#00f5ff"
PURPLE_C = "#9b00ff"
GREEN_C  = "#00ff41"
GOLD_C   = "#ffaa00"
WHITE_C  = "#ffffff"
MUTED_C  = "#888899"
DIM_C    = "#1a1a2e"


def _glitch_flash(scene, mob):
    """Quick RGB-split glitch on any Text mob."""
    r = mob.copy().set_color(RED).shift(RIGHT * 0.07 + UP * 0.04)
    b = mob.copy().set_color(BLUE).shift(LEFT * 0.07 + DOWN * 0.04)
    scene.add(r, b)
    scene.wait(0.05)
    scene.remove(r, b)
    scene.wait(0.05)


# ─────────────────────────────────────────────────────────────────────────────
class TechTitleScene(ShortsScene):
    """
    Neon glitch title card for tech/AI Shorts.
    Circuit traces animate in, then the title glitches into view.
    """

    TITLE_TEXT    = "AI DECODED"
    SUBTITLE_TEXT = "Breaking Down Artificial Intelligence"
    CHANNEL_TAG   = "@YourChannel"

    def construct(self):
        self.camera.background_color = BG

        # ── Circuit-board background traces ───────────────────────────────────
        traces = self._circuit_traces()
        self.play(Create(traces), run_time=1.2)

        # ── Accent bar ────────────────────────────────────────────────────────
        bar = Rectangle(
            width=0.12, height=3.0,
            fill_color=CYAN_C,
            fill_opacity=1,
            stroke_width=0,
        )
        bar.to_edge(LEFT, buff=0.55)
        bar.move_to([bar.get_x(), 0, 0])
        self.play(GrowFromEdge(bar, DOWN), run_time=0.5)

        # ── Main title ────────────────────────────────────────────────────────
        title = Text(self.TITLE_TEXT, font_size=66, color=WHITE_C, weight=BOLD)
        title.move_to(UP * 1.0)

        # Glitch-in effect
        self.play(FadeIn(title, shift=RIGHT * 0.06), run_time=0.4)
        _glitch_flash(self, title)
        _glitch_flash(self, title)

        # Cyan outline shadow
        shadow = title.copy().set_color(CYAN_C).set_opacity(0.2).shift(RIGHT * 0.05 + DOWN * 0.05)
        self.add_foreground_mobject(title)
        self.add(shadow)

        # ── Subtitle ──────────────────────────────────────────────────────────
        subtitle = Text(self.SUBTITLE_TEXT, font_size=22, color=MUTED_C)
        subtitle.next_to(title, DOWN, buff=0.4)
        # Word-wrap: if too wide, stack
        if subtitle.width > 7.5:
            words = self.SUBTITLE_TEXT.split()
            mid = len(words) // 2
            line1 = Text(" ".join(words[:mid]), font_size=22, color=MUTED_C)
            line2 = Text(" ".join(words[mid:]),  font_size=22, color=MUTED_C)
            subtitle = VGroup(line1, line2).arrange(DOWN, buff=0.12)
            subtitle.next_to(title, DOWN, buff=0.4)

        self.play(Write(subtitle), run_time=0.8)

        # ── Divider ────────────────────────────────────────────────────────────
        div = Line(LEFT * 3, RIGHT * 3, color=CYAN_C, stroke_width=1.5)
        div.next_to(subtitle, DOWN, buff=0.4)
        self.play(Create(div), run_time=0.4)

        # ── Stats / tags row ──────────────────────────────────────────────────
        tags = ["#AI", "#Tech", "#Shorts", "#ML"]
        tag_mobs = VGroup(*[
            Text(t, font_size=20, color=CYAN_C) for t in tags
        ]).arrange(RIGHT, buff=0.4)
        tag_mobs.next_to(div, DOWN, buff=0.4)
        self.play(FadeIn(tag_mobs, shift=UP * 0.15), run_time=0.5)

        # ── Channel name ──────────────────────────────────────────────────────
        channel = Text(self.CHANNEL_TAG, font_size=26, color=PURPLE_C)
        channel.to_edge(DOWN, buff=0.9)
        self.play(FadeIn(channel), run_time=0.4)

        self.wait(1.5)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _circuit_traces(self):
        """L-shaped PCB-style trace lines in the background."""
        random.seed(7)
        group = VGroup()
        fh = config.frame_height
        fw = config.frame_width

        for _ in range(18):
            x1 = random.uniform(-fw / 2, fw / 2)
            y1 = random.uniform(-fh / 2, fh / 2)
            # L-turn
            x_mid = x1 + random.uniform(-1.2, 1.2)
            y2    = y1 + random.uniform(-1.5, 1.5)

            h = Line([x1, y1, 0], [x_mid, y1, 0],
                     color=DIM_C, stroke_width=1.0, stroke_opacity=0.7)
            v = Line([x_mid, y1, 0], [x_mid, y2, 0],
                     color=DIM_C, stroke_width=1.0, stroke_opacity=0.7)
            dot = Dot([x_mid, y1, 0], radius=0.04, color=CYAN_C, fill_opacity=0.5)
            group.add(h, v, dot)

        return group


# ─────────────────────────────────────────────────────────────────────────────
class GamingTitleScene(ShortsScene):
    """
    Pixel-pop gaming title card for gaming Shorts.
    Grid background, pixel-border box, score-counter effect.
    """

    TITLE_TEXT    = "GAME ON"
    SUBTITLE_TEXT = "Top Gaming Moments"
    CHANNEL_TAG   = "@YourChannel"

    def construct(self):
        self.camera.background_color = "#1a0a2e"

        # ── Pixel grid background ────────────────────────────────────────────
        grid = NumberPlane(
            x_range=[-5, 5, 0.5],
            y_range=[-9, 9, 0.5],
            background_line_style={"stroke_color": "#2a1a4e", "stroke_width": 0.8},
            axis_config={"stroke_width": 0},
            faded_line_ratio=0,
        )
        self.add(grid)

        # ── Score counter ─────────────────────────────────────────────────────
        score_tracker = ValueTracker(0)
        score_disp = always_redraw(
            lambda: Text(
                f"SCORE  {int(score_tracker.get_value()):06d}",
                font_size=22,
                color=GREEN_C,
            ).to_edge(UP, buff=0.45)
        )
        self.add(score_disp)
        self.play(score_tracker.animate.set_value(999999), run_time=1.0,
                  rate_func=linear)

        # ── Pixel-border box ──────────────────────────────────────────────────
        box = Rectangle(
            width=7.8, height=5.5,
            color=GREEN_C,
            fill_color="#0d001a",
            fill_opacity=0.95,
            stroke_width=3,
        )
        box.move_to(DOWN * 0.8)

        # Corner pixel accents
        corners = VGroup()
        for cx, cy in [(-3.9, 1.95), (3.9, 1.95), (-3.9, -3.55), (3.9, -3.55)]:
            sq = Square(side_length=0.25, color=GOLD_C,
                        fill_color=GOLD_C, fill_opacity=1, stroke_width=0)
            sq.move_to([cx, cy, 0])
            corners.add(sq)

        self.play(Create(box), FadeIn(corners), run_time=0.6)

        # ── Title text ────────────────────────────────────────────────────────
        title = Text(self.TITLE_TEXT, font_size=72, color=GREEN_C, weight=BOLD)
        title.move_to(box.get_center() + UP * 1.1)

        self.play(GrowFromCenter(title), run_time=0.5)

        # Pixel-blink
        for _ in range(2):
            self.play(title.animate.set_opacity(0), run_time=0.08)
            self.play(title.animate.set_opacity(1), run_time=0.08)

        # ── Subtitle ──────────────────────────────────────────────────────────
        subtitle = Text(self.SUBTITLE_TEXT, font_size=26, color=GOLD_C)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(subtitle), run_time=0.6)

        # ── Lives / stars row ────────────────────────────────────────────────
        lives = Text("❤  ❤  ❤", font_size=30, color=RED_C)
        lives.next_to(subtitle, DOWN, buff=0.45)
        self.play(FadeIn(lives), run_time=0.4)

        # ── Tags ─────────────────────────────────────────────────────────────
        tag_row = Text("#Gaming  #GamingShorts  #GameOn", font_size=19, color=MUTED_C)
        tag_row.next_to(lives, DOWN, buff=0.45)
        self.play(FadeIn(tag_row), run_time=0.4)

        # ── Channel ───────────────────────────────────────────────────────────
        channel = Text(self.CHANNEL_TAG, font_size=24, color=CYAN_C)
        channel.to_edge(DOWN, buff=0.85)
        self.play(FadeIn(channel))

        self.wait(1.5)
