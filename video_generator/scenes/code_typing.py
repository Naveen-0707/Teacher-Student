"""
Code/tech scenes for YouTube Shorts (9:16 vertical).
Scenes: CodeTypingScene, MatrixRainScene
"""

import random
from manim import *

BG      = "#0a0a0f"
GREEN_C = "#00ff41"
CYAN_C  = "#00f5ff"
MUTED_C = "#888899"
WHITE_C = "#ffffff"
DIM_C   = "#333344"

# Python AI snippet shown in CodeTypingScene
CODE_LINES = [
    ("import ", "#888899"),
    ("import ", "#888899"),
    ("", ""),
    ("class ", "#9b00ff"),
    ("    def ", "#9b00ff"),
    ("        self", "#00f5ff"),
    ("        self", "#00f5ff"),
    ("        self", "#00f5ff"),
    ("", ""),
    ("    def ", "#9b00ff"),
    ("        x ", "#ffffff"),
    ("        x ", "#ffffff"),
    ("        return ", "#9b00ff"),
]

CODE_STRINGS = [
    ("import torch", "#00f5ff"),
    ("import torch.nn as nn", "#00f5ff"),
    ("", "#ffffff"),
    ("class NeuralNet(nn.Module):", "#ffcc00"),
    ("    def __init__(self):", "#00ff41"),
    ("        self.fc1 = nn.Linear(784, 256)", "#ffffff"),
    ("        self.fc2 = nn.Linear(256, 128)", "#ffffff"),
    ("        self.out = nn.Linear(128, 10)", "#ffffff"),
    ("", "#ffffff"),
    ("    def forward(self, x):", "#00ff41"),
    ("        x = torch.relu(self.fc1(x))", "#ffffff"),
    ("        x = torch.relu(self.fc2(x))", "#ffffff"),
    ("        return self.out(x)", "#00f5ff"),
]


# ─────────────────────────────────────────────────────────────────────────────
class CodeTypingScene(Scene):
    """
    Dark terminal showing PyTorch code typed out line-by-line.
    Each line reveals with an AddTextLetterByLetter animation.
    Perfect vertical layout for Shorts.
    """

    LINE_FS   = 24   # font size
    LINE_GAP  = 0.42 # vertical spacing between lines

    def construct(self):
        self.camera.background_color = BG

        # ── Header ────────────────────────────────────────────────────────────
        title = Text("AI Code", font_size=52, color=WHITE_C, weight=BOLD)
        subtitle = Text("Building a Neural Net", font_size=24, color=MUTED_C)
        title.to_edge(UP, buff=0.5)
        subtitle.next_to(title, DOWN, buff=0.15)

        self.play(Write(title), FadeIn(subtitle), run_time=1.0)
        self.wait(0.3)

        # ── Terminal window ───────────────────────────────────────────────────
        box = RoundedRectangle(
            corner_radius=0.2,
            width=8.2, height=7.5,
            color=DIM_C,
            fill_color="#0d0d1a",
            fill_opacity=1,
            stroke_width=1.5,
        )
        box.move_to(DOWN * 1.0)

        # Top bar of terminal
        bar = Rectangle(
            width=8.2, height=0.4,
            fill_color="#1e1e30",
            fill_opacity=1,
            stroke_width=0,
        )
        bar.next_to(box, UP, buff=0)
        bar.shift(DOWN * 0.2)

        dots = VGroup()
        for i, col in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
            d = Circle(radius=0.07, fill_color=col, fill_opacity=1, stroke_width=0)
            d.move_to(bar.get_left() + RIGHT * (0.25 + i * 0.22))
            dots.add(d)

        filename = Text("neural_net.py", font_size=13, color=MUTED_C)
        filename.move_to(bar)

        terminal = VGroup(box, bar, dots, filename)
        self.play(FadeIn(terminal), run_time=0.5)

        # ── Type code lines ───────────────────────────────────────────────────
        start_y = box.get_top()[1] - 0.55
        start_x = box.get_left()[0] + 0.35

        line_mobs = []
        for i, (text, color) in enumerate(CODE_STRINGS):
            y = start_y - i * self.LINE_GAP
            if y < box.get_bottom()[1] + 0.3:
                break   # don't overflow box
            if text == "":
                continue

            mob = Text(text, font_size=self.LINE_FS, color=color,
                       font="Courier New")
            mob.move_to([start_x + mob.width / 2, y, 0])
            line_mobs.append(mob)

        # Reveal cursor
        cursor = Rectangle(width=0.015, height=self.LINE_FS * 0.012 + 0.15,
                           fill_color=GREEN_C, fill_opacity=1, stroke_width=0)

        for mob in line_mobs:
            cursor.next_to(mob, RIGHT, buff=0.04)
            self.play(
                AddTextLetterByLetter(mob, time_per_char=0.04),
                run_time=len(mob.original_text) * 0.045,
            )
            self.add(cursor)

        self.play(FadeOut(cursor))
        self.wait(1.5)


# ─────────────────────────────────────────────────────────────────────────────
class MatrixRainScene(Scene):
    """
    Vertical matrix-rain cascade on a black background.
    Characters stream downward in neon green columns.
    """

    N_COLS   = 14
    TRAIL    = 14
    CHAR_FS  = 18
    DURATION = 9.0

    def construct(self):
        self.camera.background_color = "#000000"

        # Frame: 9 units wide, 16 units tall for Shorts
        fw = config.frame_width   # ~9
        fh = config.frame_height  # ~16

        col_w = fw / self.N_COLS

        # Pre-generate column streams
        random.seed(42)
        streams = []
        stream_group = VGroup()

        for i in range(self.N_COLS):
            x = -fw / 2 + (i + 0.5) * col_w
            chars_in_col = []
            y_start = fh / 2 + random.uniform(0, fh)   # staggered start above frame

            for j in range(self.TRAIL):
                brightness = 1.0 if j == 0 else max(0, 0.85 - j * 0.065)
                color = interpolate_color("#002200", "#00ff41", brightness)
                ch = Text(
                    random.choice("01アイウエオカ01"),
                    font_size=self.CHAR_FS,
                    color=color,
                )
                ch.set_opacity(max(0.05, brightness))
                ch.move_to([x, y_start - j * (fh / self.TRAIL * 0.8), 0])
                chars_in_col.append(ch)
                stream_group.add(ch)

            streams.append((chars_in_col, x, y_start))

        self.add(stream_group)

        # Animate all columns falling at slightly different speeds
        fall_anims = []
        for chars, x, y_start in streams:
            speed = random.uniform(0.85, 1.4)
            dist  = fh + self.TRAIL * (fh / self.TRAIL * 0.8) + 2
            grp   = VGroup(*chars)
            fall_anims.append(grp.animate.shift(DOWN * dist * speed))

        # Overlay title
        title = Text("< AI SYSTEMS >", font_size=44, color=GREEN_C, weight=BOLD)
        title.set_z_index(10)
        title.move_to(ORIGIN)

        glow = title.copy()
        glow.set_opacity(0.25)
        glow.scale(1.03)

        tag = Text("#AIShorts", font_size=22, color=MUTED_C)
        tag.next_to(title, DOWN, buff=0.3)

        self.play(
            *fall_anims,
            FadeIn(VGroup(glow, title)),
            run_time=self.DURATION,
            rate_func=linear,
        )
        self.play(FadeIn(tag, shift=UP * 0.15))
        self.wait(0.8)
