"""
Gaming scenes for YouTube Shorts (9:16 vertical).
Scenes: GamingIntroScene, XPBarScene, AchievementScene
"""

import random
from manim import *

BG      = "#0a0a0f"
GAME_BG = "#1a0a2e"
GREEN_C = "#00ff41"
CYAN_C  = "#00f5ff"
GOLD_C  = "#ffaa00"
RED_C   = "#ff3333"
WHITE_C = "#ffffff"
MUTED_C = "#888899"
PURPLE_C = "#9b00ff"


# ─────────────────────────────────────────────────────────────────────────────
class GamingIntroScene(Scene):
    """
    Retro arcade-style intro for gaming Shorts:
      1. Boot-up scanlines flash
      2. GAME TITLE types onto screen
      3. Loading bar fills to 100%
      4. PLAYER 1 READY!
    """

    def construct(self):
        self.camera.background_color = GAME_BG

        # ── Scanline flash ────────────────────────────────────────────────────
        for _ in range(3):
            flash = Rectangle(
                width=config.frame_width,
                height=config.frame_height,
                fill_color="#00ff41",
                fill_opacity=0.08,
                stroke_width=0,
            )
            self.add(flash)
            self.wait(0.07)
            self.remove(flash)
            self.wait(0.07)

        # ── Insert Coin ───────────────────────────────────────────────────────
        coin = Text("INSERT COIN", font_size=30, color=GOLD_C)
        coin.to_edge(UP, buff=1.2)
        self.play(FadeIn(coin), run_time=0.4)
        self.play(coin.animate.set_opacity(0.2), run_time=0.3)
        self.play(coin.animate.set_opacity(1.0), run_time=0.3)
        self.play(FadeOut(coin), run_time=0.3)

        # ── Game title ────────────────────────────────────────────────────────
        title_top = Text("LEVEL UP", font_size=66, color=GREEN_C, weight=BOLD)
        title_bot = Text("GAMING", font_size=42, color=CYAN_C, weight=BOLD)
        title_top.move_to(UP * 3.5)
        title_bot.next_to(title_top, DOWN, buff=0.3)

        star_line = Text("★  ★  ★  ★  ★", font_size=28, color=GOLD_C)
        star_line.next_to(title_bot, DOWN, buff=0.4)

        self.play(Write(title_top), run_time=0.7)
        self.play(Write(title_bot), run_time=0.5)
        self.play(FadeIn(star_line), run_time=0.4)
        self.wait(0.4)

        # ── Loading bar ───────────────────────────────────────────────────────
        bar_bg = RoundedRectangle(
            corner_radius=0.12,
            width=6.5, height=0.45,
            fill_color="#111122",
            fill_opacity=1,
            color=MUTED_C,
            stroke_width=1.5,
        )
        bar_bg.move_to(DOWN * 0.5)

        bar_fill = RoundedRectangle(
            corner_radius=0.12,
            width=0.01, height=0.45,
            fill_color=GREEN_C,
            fill_opacity=1,
            stroke_width=0,
        )
        bar_fill.align_to(bar_bg, LEFT).shift(RIGHT * 0.0)

        pct_tracker = ValueTracker(0)
        pct_label = always_redraw(
            lambda: Text(
                f"{int(pct_tracker.get_value())}%",
                font_size=22,
                color=WHITE_C,
            ).next_to(bar_bg, DOWN, buff=0.18)
        )

        load_text = Text("LOADING...", font_size=24, color=MUTED_C)
        load_text.next_to(bar_bg, UP, buff=0.22)

        self.play(FadeIn(bar_bg), FadeIn(load_text), run_time=0.4)
        self.add(bar_fill, pct_label)

        def update_bar(mob, alpha):
            pct = alpha * 100
            pct_tracker.set_value(pct)
            new_w = max(0.01, (pct / 100) * 6.5)
            mob.become(
                RoundedRectangle(
                    corner_radius=0.12,
                    width=new_w, height=0.45,
                    fill_color=GREEN_C,
                    fill_opacity=1,
                    stroke_width=0,
                ).align_to(bar_bg, LEFT)
            )

        self.play(
            UpdateFromAlphaFunc(bar_fill, update_bar),
            run_time=2.5,
            rate_func=linear,
        )

        self.play(
            bar_fill.animate.set_fill(GOLD_C),
            run_time=0.3,
        )

        # ── PLAYER 1 READY ────────────────────────────────────────────────────
        self.play(
            FadeOut(bar_bg),
            FadeOut(bar_fill),
            FadeOut(pct_label),
            FadeOut(load_text),
            run_time=0.3,
        )

        ready = Text("PLAYER 1", font_size=54, color=GREEN_C, weight=BOLD)
        ready_sub = Text("READY!", font_size=44, color=GOLD_C, weight=BOLD)
        ready.move_to(DOWN * 0.3)
        ready_sub.next_to(ready, DOWN, buff=0.3)

        self.play(
            GrowFromCenter(ready),
            run_time=0.5,
        )
        self.play(
            GrowFromCenter(ready_sub),
            run_time=0.4,
        )

        # Blink effect
        for _ in range(2):
            self.play(ready.animate.set_opacity(0), ready_sub.animate.set_opacity(0),
                      run_time=0.18)
            self.play(ready.animate.set_opacity(1), ready_sub.animate.set_opacity(1),
                      run_time=0.18)

        self.wait(1.2)


# ─────────────────────────────────────────────────────────────────────────────
class XPBarScene(Scene):
    """
    XP bar that fills up then triggers a LEVEL UP burst.
    Great as an 8-second Shorts clip.
    """

    def construct(self):
        self.camera.background_color = BG

        # ── Labels ────────────────────────────────────────────────────────────
        title = Text("EXPERIENCE", font_size=48, color=WHITE_C, weight=BOLD)
        title.to_edge(UP, buff=0.7)

        level_label = Text("Level  12", font_size=30, color=GOLD_C)
        level_label.next_to(title, DOWN, buff=0.3)

        self.play(FadeIn(title), FadeIn(level_label), run_time=0.7)

        # ── XP bar ───────────────────────────────────────────────────────────
        bar_bg = RoundedRectangle(
            corner_radius=0.18,
            width=7.0, height=0.6,
            fill_color="#111122",
            fill_opacity=1,
            color=MUTED_C,
            stroke_width=1.5,
        )
        bar_bg.move_to(UP * 0.5)

        xp_tracker = ValueTracker(0)

        xp_label = always_redraw(
            lambda: Text(
                f"XP  {int(xp_tracker.get_value() * 1000)} / 1000",
                font_size=22,
                color=GOLD_C,
            ).next_to(bar_bg, DOWN, buff=0.22)
        )

        bar_fill = RoundedRectangle(
            corner_radius=0.18,
            width=0.01, height=0.6,
            fill_color=GOLD_C,
            fill_opacity=1,
            stroke_width=0,
        )
        bar_fill.align_to(bar_bg, LEFT)

        self.play(FadeIn(bar_bg), run_time=0.4)
        self.add(bar_fill, xp_label)

        def upd(mob, alpha):
            xp_tracker.set_value(alpha)
            mob.become(
                RoundedRectangle(
                    corner_radius=0.18,
                    width=max(0.01, alpha * 7.0),
                    height=0.6,
                    fill_color=GOLD_C,
                    fill_opacity=1,
                    stroke_width=0,
                ).align_to(bar_bg, LEFT)
            )

        self.play(
            UpdateFromAlphaFunc(bar_fill, upd),
            run_time=3.0,
            rate_func=linear,
        )

        # ── Level Up burst ────────────────────────────────────────────────────
        self.play(
            bar_fill.animate.set_fill(WHITE_C),
            run_time=0.2,
        )

        lvlup = Text("LEVEL UP!", font_size=72, color=GOLD_C, weight=BOLD)
        lvlup.move_to(DOWN * 1.2)
        new_level = Text("Level  13", font_size=32, color=CYAN_C)
        new_level.next_to(lvlup, DOWN, buff=0.35)

        # Burst particles
        particles = VGroup(*[
            Dot(ORIGIN, radius=0.07, color=random.choice([GOLD_C, WHITE_C, CYAN_C]))
            for _ in range(20)
        ])

        self.play(
            GrowFromCenter(lvlup),
            *[
                p.animate.move_to(
                    [random.uniform(-3, 3), random.uniform(-2, 2), 0]
                ).set_opacity(0)
                for p in particles
            ],
            run_time=0.7,
        )
        self.play(FadeIn(new_level, shift=UP * 0.2))
        self.wait(1.5)


# ─────────────────────────────────────────────────────────────────────────────
class AchievementScene(Scene):
    """
    'Achievement Unlocked' toast that slides in from the top.
    Under 7 seconds – perfect Shorts overlay.
    """

    def construct(self):
        self.camera.background_color = BG

        # Background subtle grid
        grid = NumberPlane(
            x_range=[-5, 5, 1], y_range=[-9, 9, 1],
            background_line_style={"stroke_color": "#1a1a2e", "stroke_width": 1},
            axis_config={"stroke_width": 0},
            faded_line_ratio=0,
        )
        self.add(grid)

        # ── Achievement card ──────────────────────────────────────────────────
        card = RoundedRectangle(
            corner_radius=0.25,
            width=7.5, height=2.2,
            fill_color="#12121f",
            fill_opacity=0.97,
            color=GOLD_C,
            stroke_width=2.5,
        )
        card.move_to(UP * 9)   # starts off-screen top

        trophy = Text("🏆", font_size=52)
        trophy.move_to(card.get_left() + RIGHT * 1.0)

        ach_top = Text("Achievement Unlocked", font_size=20, color=GOLD_C)
        ach_name = Text("First Neural Net!", font_size=28, color=WHITE_C, weight=BOLD)
        ach_top.move_to(card.get_center() + RIGHT * 0.4 + UP * 0.45)
        ach_name.move_to(card.get_center() + RIGHT * 0.4 + DOWN * 0.2)

        card_group = VGroup(card, trophy, ach_top, ach_name)

        # Slide in
        self.add(card_group)
        self.play(
            card_group.animate.move_to(UP * 4.5),
            run_time=0.6,
            rate_func=ease_out_bounce,
        )

        # Gold shimmer
        shimmer = card.copy()
        shimmer.set_fill(GOLD_C, opacity=0.25)
        self.play(
            shimmer.animate.set_fill(GOLD_C, opacity=0),
            run_time=0.5,
        )
        self.remove(shimmer)

        # ── Stat counters (centre of screen) ─────────────────────────────────
        stats = VGroup(
            self._stat("+500 XP",    GOLD_C),
            self._stat("+1 Skill",   CYAN_C),
            self._stat("+Reputation", "#00ff41"),
        )
        stats.arrange(DOWN, buff=0.7)
        stats.move_to(DOWN * 0.5)

        for s in stats:
            self.play(FadeIn(s, shift=RIGHT * 0.3), run_time=0.4)
            self.wait(0.15)

        # ── Channel tag ───────────────────────────────────────────────────────
        tag = Text("#Gaming  #AI  #Tech", font_size=22, color=MUTED_C)
        tag.to_edge(DOWN, buff=0.9)
        self.play(FadeIn(tag))

        self.wait(1.8)

    @staticmethod
    def _stat(text, color):
        t = Text(text, font_size=34, color=color, weight=BOLD)
        return t
