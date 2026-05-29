# ── Color palette ──────────────────────────────────────────────────────────────
COLORS = {
    "bg":        "#0a0a0f",
    "bg_panel":  "#12121f",
    "bg_card":   "#1a1a2e",

    "cyan":      "#00f5ff",
    "purple":    "#9b00ff",
    "green":     "#00ff41",
    "orange":    "#ff6b00",
    "pink":      "#ff0090",
    "yellow":    "#ffcc00",

    "white":     "#ffffff",
    "muted":     "#888899",
    "dim":       "#333344",

    "neuron":    "#00f5ff",
    "conn":      "#1a3a5c",

    "hp_red":    "#ff3333",
    "mp_blue":   "#3366ff",
    "xp_gold":   "#ffaa00",
    "game_bg":   "#1a0a2e",
    "game_text": "#00ff41",
}

# ── Default: YouTube Shorts ─────────────────────────────────────────────────────
# All scenes are built for 9:16 vertical layout.
# Manim frame with 9:16 ratio: width=9, height=16 (or scaled equivalents).
# At pixel level: 1080×1920 @ 60fps.

FORMATS = {
    "shorts": {
        "pixel_width":  1080,
        "pixel_height": 1920,
        "frame_rate":   60,
        "label":        "YouTube Shorts 9:16 1080p",
    },
    "instagram": {
        "pixel_width":  1080,
        "pixel_height": 1920,
        "frame_rate":   30,
        "label":        "Instagram Reel 9:16",
    },
    "youtube": {
        "pixel_width":  1920,
        "pixel_height": 1080,
        "frame_rate":   60,
        "label":        "YouTube 16:9 1080p",
    },
}

DEFAULT_FORMAT = "shorts"

# ── Manim quality flags ─────────────────────────────────────────────────────────
QUALITY = {
    "preview": "-ql",   # 480p 15fps  – quick check
    "draft":   "-qm",   # 720p 30fps  – working version
    "high":    "-qh",   # 1080p 60fps – final upload
}

# ── Frame units (vertical fix) ───────────────────────────────────────────────────
# Manim keeps frame_height fixed and derives frame_width from the pixel aspect.
# For a 9:16 frame, the DEFAULT frame_height of 8.0 gives a frame only
# 8.0 * 1080/1920 = 4.5 units wide — far too narrow, and every scene's layout
# math assumes ~8 units of width. We therefore set frame_height for portrait so
# the working WIDTH becomes 8.0 units:
#     frame_width = frame_height * (pixel_width / pixel_height)
#     8.0         = 14.2222...   * (1080 / 1920)
FRAME_HEIGHT_UNITS = 14.2222   # used by ShortsScene for 9:16; 16:9 keeps Manim default
FRAME_WIDTH_UNITS  = 8.0       # resulting working width for 9:16

# ── Safe zones (pixels, for 1080×1920) ───────────────────────────────────────────
# Keep key visuals/text clear of platform UI. Derived from algorithm research.
SAFE_ZONES = {
    "top_px":    288,   # status bar / search
    "bottom_px": 400,   # caption bar + channel/title + music pill
    "left_px":   40,
    "right_px":  192,   # like / comment / share action column
    # On-canvas text should stay ABOVE this line when burned captions are on
    # (≈30% up from the bottom edge):
    "caption_keepout_from_bottom_px": 576,
}

# ── Caption (ASS) style presets ──────────────────────────────────────────────────
# Positions are in real pixels via ASS PlayResX/Y. MarginV is measured from the
# bottom edge (Alignment=2 bottom-center), raised to sit in the safe band.
CAPTION_STYLE = {
    "tiktok": {
        "font":               "DejaVu Sans",   # widely present on Linux; Arial on Win/Mac
        "font_size_px":       72,
        # ASS colours are &HAABBGGRR (alpha, blue, green, red).
        "primary":            "&H00FFFFFF",     # white  – upcoming words
        "highlight":          "&H0000FFFF",     # yellow – word currently spoken (karaoke)
        "outline":            "&H00000000",     # black  – outline for muted-view contrast
        "outline_w":          6,
        "shadow":             3,
        "bold":               1,
        "alignment":          2,                # bottom-centre
        "margin_v":           560,              # raise into safe band
        "margin_l":           60,
        "margin_r":           200,              # clear right action buttons
        "max_chars_per_line": 22,
        "max_lines":          2,
        "karaoke":            True,
    },
}
DEFAULT_CAPTION_STYLE = "tiktok"

# ── Pipeline defaults ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "engine":           "edge",            # edge | piper | kokoro | pyttsx3
    "voice":            "en-US-GuyNeural",
    "length_target":    42,                # seconds (user-chosen band 35–50)
    "length_min":       35,
    "length_max":       50,
    "captions":         True,
    "music":            True,
    "music_volume_db":  -18.0,
    "duck":             True,
    "loop":             False,
    "auto_hook":        True,
}

# ── Asset locations ───────────────────────────────────────────────────────────────
import os as _os
_HERE       = _os.path.dirname(_os.path.abspath(__file__))
ASSETS_DIR  = _os.path.join(_HERE, "assets")
MUSIC_DIR   = _os.path.join(ASSETS_DIR, "music")
PIPER_DIR   = _os.path.join(ASSETS_DIR, "piper")

# Default offline Piper voice (downloaded by `generate.py setup`, no API key)
PIPER_DEFAULT_VOICE = "en_US-amy-medium"
PIPER_VOICE_BASE_URL = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
    "en/en_US/amy/medium/"
)
