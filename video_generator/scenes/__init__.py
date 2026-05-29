"""
Scene registry – maps short names to (file, class, description, tags).
All scenes are designed for 9:16 vertical (YouTube Shorts / Instagram Reels).
"""

REGISTRY = {
    # ── AI / Machine-learning ────────────────────────────────────────────────
    "neural_network": {
        "file":  "neural_network.py",
        "class": "NeuralNetworkScene",
        "desc":  "Neural-net forward-pass animation – glowing nodes & pulses",
        "tags":  ["ai", "ml"],
        "dur":   "~15s",
    },
    "neural_training": {
        "file":  "neural_network.py",
        "class": "NeuralTrainingScene",
        "desc":  "Training loop animation with falling loss curve",
        "tags":  ["ai", "ml"],
        "dur":   "~18s",
    },

    # ── Tech / Code ──────────────────────────────────────────────────────────
    "code_typing": {
        "file":  "code_typing.py",
        "class": "CodeTypingScene",
        "desc":  "Python AI code typed out line-by-line in a dark terminal",
        "tags":  ["tech", "code"],
        "dur":   "~14s",
    },
    "matrix_rain": {
        "file":  "code_typing.py",
        "class": "MatrixRainScene",
        "desc":  "Matrix-style digital rain cascade – cyberpunk aesthetic",
        "tags":  ["tech", "aesthetic"],
        "dur":   "~10s",
    },

    # ── Gaming ───────────────────────────────────────────────────────────────
    "gaming_intro": {
        "file":  "gaming_intro.py",
        "class": "GamingIntroScene",
        "desc":  "Retro arcade boot-up, loading bar & PLAYER 1 READY",
        "tags":  ["gaming", "retro"],
        "dur":   "~16s",
    },
    "xp_bar": {
        "file":  "gaming_intro.py",
        "class": "XPBarScene",
        "desc":  "XP bar filling + LEVEL UP burst",
        "tags":  ["gaming"],
        "dur":   "~8s",
    },
    "achievement": {
        "file":  "gaming_intro.py",
        "class": "AchievementScene",
        "desc":  "Achievement Unlocked popup toast",
        "tags":  ["gaming"],
        "dur":   "~6s",
    },

    # ── Title cards / Outros ─────────────────────────────────────────────────
    "tech_title": {
        "file":  "title_card.py",
        "class": "TechTitleScene",
        "desc":  "Glitchy neon tech title-card reveal",
        "tags":  ["title", "tech"],
        "dur":   "~8s",
    },
    "gaming_title": {
        "file":  "title_card.py",
        "class": "GamingTitleScene",
        "desc":  "Pixel-pop gaming title-card reveal",
        "tags":  ["title", "gaming"],
        "dur":   "~8s",
    },

    # ── Data / Stats ─────────────────────────────────────────────────────────
    "data_flow": {
        "file":  "data_visual.py",
        "class": "DataFlowScene",
        "desc":  "Data packets streaming through an AI pipeline",
        "tags":  ["ai", "data"],
        "dur":   "~12s",
    },
    "stats_chart": {
        "file":  "data_visual.py",
        "class": "StatsChartScene",
        "desc":  "Animated bar-chart – e.g. AI model benchmark scores",
        "tags":  ["data", "stats"],
        "dur":   "~10s",
    },
}
