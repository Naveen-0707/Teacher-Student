"""
Data-visualization scenes for YouTube Shorts (9:16 vertical).
Scenes: DataFlowScene, StatsChartScene
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


# ─────────────────────────────────────────────────────────────────────────────
class DataFlowScene(ShortsScene):
    """
    Data packets travel through a vertical AI pipeline:
      Raw Data → Pre-process → Model → Output
    Each stage lights up as packets pass through.
    """

    STAGES = [
        ("Raw Data",    CYAN_C),
        ("Pre-process", PURPLE_C),
        ("AI Model",    GREEN_C),
        ("Prediction",  GOLD_C),
    ]

    def construct(self):
        self.camera.background_color = BG

        # ── Title ─────────────────────────────────────────────────────────────
        title = Text("AI Pipeline", font_size=52, color=WHITE_C, weight=BOLD)
        subtitle = Text("Data → Intelligence", font_size=24, color=MUTED_C)
        title.to_edge(UP, buff=0.5)
        subtitle.next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(subtitle), run_time=1.0)

        # ── Pipeline boxes ────────────────────────────────────────────────────
        boxes, labels = self._build_pipeline()

        self.play(
            *[FadeIn(b, shift=RIGHT * 0.2) for b in boxes],
            *[Write(l) for l in labels],
            run_time=1.0,
        )
        self.wait(0.4)

        # ── Connectors ────────────────────────────────────────────────────────
        arrows = self._build_arrows(boxes)
        self.play(*[Create(a) for a in arrows], run_time=0.6)

        # ── Animate data packets ──────────────────────────────────────────────
        for _ in range(2):
            self._send_packet(boxes)

        self.wait(1.2)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _build_pipeline(self):
        n = len(self.STAGES)
        total_h = (n - 1) * 2.8
        boxes, labels = [], VGroup()

        for i, (name, color) in enumerate(self.STAGES):
            y = total_h / 2 - i * 2.8

            box = RoundedRectangle(
                corner_radius=0.2,
                width=6.0, height=0.9,
                fill_color=DIM_C,
                fill_opacity=1,
                color=color,
                stroke_width=2,
            )
            box.move_to([0, y, 0])

            lbl = Text(name, font_size=26, color=color)
            lbl.move_to(box.get_center())

            boxes.append(box)
            labels.add(lbl)

        return boxes, labels

    def _build_arrows(self, boxes):
        arrows = []
        for i in range(len(boxes) - 1):
            a = Arrow(
                boxes[i].get_bottom(),
                boxes[i + 1].get_top(),
                buff=0.08,
                color=MUTED_C,
                stroke_width=2,
                max_tip_length_to_length_ratio=0.18,
            )
            arrows.append(a)
        return arrows

    def _send_packet(self, boxes):
        for i, (box, (_, color)) in enumerate(zip(boxes, self.STAGES)):
            # Light up the box
            highlight = box.copy().set_fill(color, opacity=0.25)
            self.add(highlight)

            # Packet dot
            dot = Dot(box.get_center(), radius=0.14, color=WHITE_C)
            self.add(dot)

            if i < len(boxes) - 1:
                self.play(
                    dot.animate.move_to(boxes[i + 1].get_center()),
                    highlight.animate.set_fill(color, opacity=0),
                    run_time=0.45,
                    rate_func=linear,
                )
            else:
                self.play(
                    dot.animate.set_opacity(0).scale(3),
                    highlight.animate.set_fill(color, opacity=0),
                    run_time=0.4,
                )

            self.remove(dot, highlight)


# ─────────────────────────────────────────────────────────────────────────────
class StatsChartScene(ShortsScene):
    """
    Animated vertical bar chart showing AI model comparison scores.
    Bars grow from the bottom with labels – great for 'AI ranked' Shorts.
    """

    MODELS = ["GPT-4", "Gemini", "Claude", "LLaMA", "Mistral"]
    SCORES = [92,      89,       91,       84,       82]
    COLORS_LIST = [CYAN_C, "#ff6b00", PURPLE_C, GREEN_C, GOLD_C]

    MAX_BAR_H = 5.0
    BAR_W     = 0.75
    BAR_GAP   = 0.35

    def construct(self):
        self.camera.background_color = BG

        # ── Title ─────────────────────────────────────────────────────────────
        title = Text("AI Model Scores", font_size=46, color=WHITE_C, weight=BOLD)
        subtitle = Text("Benchmark comparison 2024", font_size=22, color=MUTED_C)
        title.to_edge(UP, buff=0.5)
        subtitle.next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(subtitle), run_time=1.0)

        # ── Axes ─────────────────────────────────────────────────────────────
        n = len(self.MODELS)
        total_w = n * (self.BAR_W + self.BAR_GAP) - self.BAR_GAP
        x_start = -total_w / 2
        baseline_y = -3.5

        baseline = Line(
            [x_start - 0.3, baseline_y, 0],
            [x_start + total_w + 0.3, baseline_y, 0],
            color=MUTED_C, stroke_width=1.5,
        )
        self.play(Create(baseline), run_time=0.4)

        # ── Bars (grow from baseline) ─────────────────────────────────────────
        bars, name_labels, score_labels = [], VGroup(), VGroup()

        for i, (model, score, color) in enumerate(
            zip(self.MODELS, self.SCORES, self.COLORS_LIST)
        ):
            x = x_start + i * (self.BAR_W + self.BAR_GAP) + self.BAR_W / 2
            bar_h = (score / 100) * self.MAX_BAR_H

            bar = Rectangle(
                width=self.BAR_W,
                height=0.02,
                fill_color=color,
                fill_opacity=0.85,
                stroke_width=0,
            )
            bar.align_to([0, baseline_y, 0], DOWN)
            bar.move_to([x, baseline_y, 0], aligned_edge=DOWN)

            # Model name (below bar)
            name = Text(model, font_size=17, color=WHITE_C)
            name.move_to([x, baseline_y - 0.45, 0])

            # Score label (above bar – positioned after animation)
            score_mob = Text(f"{score}", font_size=20, color=color, weight=BOLD)
            score_mob.move_to([x, baseline_y + bar_h + 0.25, 0])
            score_mob.set_opacity(0)

            bars.append((bar, bar_h, color, score_mob))
            name_labels.add(name)
            score_labels.add(score_mob)

        self.play(*[FadeIn(nl) for nl in name_labels], run_time=0.5)
        self.add(*[b for b, _, _, _ in bars])

        # Animate bars growing
        grow_anims = []
        for bar, bar_h, color, _ in bars:
            target = bar.copy()
            target.stretch_to_fit_height(bar_h)
            target.align_to([0, baseline_y, 0], DOWN)
            grow_anims.append(Transform(bar, target))

        self.play(*grow_anims, run_time=2.0, rate_func=ease_out_cubic)

        # Show score labels
        self.play(
            *[sm.animate.set_opacity(1) for _, _, _, sm in bars],
            run_time=0.5,
        )

        # ── Highlight top model ───────────────────────────────────────────────
        top_idx = self.SCORES.index(max(self.SCORES))
        top_bar = bars[top_idx][0]
        crown = Text("👑", font_size=30)
        crown.next_to(top_bar, UP, buff=0.55)
        self.play(FadeIn(crown, shift=DOWN * 0.2))

        self.wait(1.5)
