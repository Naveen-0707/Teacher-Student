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
