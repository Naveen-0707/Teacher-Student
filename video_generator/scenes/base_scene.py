"""
base_scene.py – ShortsScene: the safe-zone-aware base for vertical (9:16) scenes.

WHY THIS EXISTS
---------------
Manim keeps `frame_height` fixed (default 8.0) and derives
`frame_width = frame_height * pixel_width / pixel_height`. At 1080×1920 that is
only 4.5 units wide, so every scene whose layout assumes ~8 units of width spills
off-screen. ShortsScene sets the frame so the working WIDTH is 8.0 units for
portrait renders, and exposes helpers that keep titles/visuals inside the
platform-UI "safe zone" (so nothing hides behind the caption bar, action buttons,
or status bar).

Usage in a subclass:
    class MyScene(ShortsScene):
        def construct(self):
            self.camera.background_color = self.BG
            rect = self.content_rect()
            t = self.fit_text("Hello", max_w=rect["width"], sizes=[64, 52, 40])
            self.place_in_content(t)      # clamp into the safe area
            self.play(Write(t))
"""

import os
import sys

import numpy as np
from manim import Scene, Text, config as mcfg

# Import the PROJECT config (not Manim's) under an alias to avoid the name clash.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
import config as appcfg   # noqa: E402  (project-level config.py)

# Make sibling scene modules importable when Manim loads a file directly.
_SCENES = os.path.dirname(os.path.abspath(__file__))
if _SCENES not in sys.path:
    sys.path.insert(0, _SCENES)


class ShortsScene(Scene):
    """Vertical-aware Scene base with safe-zone helpers."""

    BG = appcfg.COLORS["bg"]

    def __init__(self, **kwargs):
        # Frame dims depend on the pixel resolution, which the CLI (--resolution)
        # has already applied to `mcfg` before the Scene is instantiated.
        self._apply_frame()
        super().__init__(**kwargs)

    # ── frame setup ───────────────────────────────────────────────────────────
    @staticmethod
    def _apply_frame():
        """For portrait renders, widen the unit frame so width == 8.0 units."""
        pw, ph = mcfg.pixel_width, mcfg.pixel_height
        if ph >= pw:  # portrait / square (9:16, 1:1)
            mcfg.frame_height = appcfg.FRAME_HEIGHT_UNITS
            mcfg.frame_width = appcfg.FRAME_WIDTH_UNITS
        # landscape (16:9 youtube): keep Manim defaults (14.222 × 8.0)

    # ── geometry helpers ──────────────────────────────────────────────────────
    @staticmethod
    def _units_per_px() -> float:
        return mcfg.frame_height / mcfg.pixel_height

    def content_rect(self) -> dict:
        """The UI-safe box, in Manim units."""
        upp = self._units_per_px()
        fw, fh = mcfg.frame_width, mcfg.frame_height
        sz = appcfg.SAFE_ZONES
        top = fh / 2 - sz["top_px"] * upp
        bottom = -fh / 2 + sz["bottom_px"] * upp
        left = -fw / 2 + sz["left_px"] * upp
        right = fw / 2 - sz["right_px"] * upp
        return {
            "top": top,
            "bottom": bottom,
            "left": left,
            "right": right,
            "center_x": (left + right) / 2,
            "center_y": (top + bottom) / 2,
            "width": right - left,
            "height": top - bottom,
        }

    def caption_anchor(self) -> np.ndarray:
        """Y-line (≈30% up from the bottom) that on-canvas text must stay ABOVE
        when burned-in captions are enabled (captions occupy the band below)."""
        upp = self._units_per_px()
        fh = mcfg.frame_height
        y = -fh / 2 + appcfg.SAFE_ZONES["caption_keepout_from_bottom_px"] * upp
        return np.array([0.0, y, 0.0])

    # ── placement helpers ─────────────────────────────────────────────────────
    def place_top(self, mob, buff: float = 0.0):
        """Anchor a mobject just under the top safe line, horizontally centred
        in the content rect."""
        rect = self.content_rect()
        mob.move_to([rect["center_x"], rect["top"] - mob.height / 2 - buff, 0])
        return mob

    def place_in_content(self, mob, captions_on: bool = True):
        """Centre a mobject in the usable area and scale it down if it overflows."""
        rect = self.content_rect()
        upper = rect["top"]
        lower = self.caption_anchor()[1] if captions_on else rect["bottom"]
        cy = (upper + lower) / 2
        max_w = rect["width"]
        max_h = max(0.1, upper - lower)
        if mob.width > max_w:
            mob.scale(max_w / mob.width)
        if mob.height > max_h:
            mob.scale(max_h / mob.height)
        mob.move_to([rect["center_x"], cy, 0])
        return mob

    # ── text helpers ──────────────────────────────────────────────────────────
    @staticmethod
    def fit_text(s, max_w, sizes, **kwargs):
        """Return a Text rendered at the largest size in `sizes` that fits max_w."""
        for fs in sizes:
            t = Text(s, font_size=fs, **kwargs)
            if t.width <= max_w:
                return t
        return Text(s, font_size=sizes[-1], **kwargs)
