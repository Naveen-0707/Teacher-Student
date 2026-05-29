"""
metadata.py – write an upload-ready metadata sidecar (<title>.txt).

Research notes encoded here:
- Title < 60 chars, keyword-first.
- 3–5 hashtags, always include #Shorts for YouTube.
- A short value-first description.
The .txt sits next to the final video so you can copy-paste at upload time.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as appcfg


def _truncate_title(s: str, limit: int = 60) -> str:
    s = " ".join(s.split())
    if len(s) <= limit:
        return s
    cut = s[:limit].rsplit(" ", 1)[0]
    return cut or s[:limit]


def _auto_hashtags(script: dict) -> list:
    meta = script.get("metadata") or {}
    tags = list(meta.get("hashtags") or [])

    if not tags:
        # derive from scene tags / title keywords
        seed = ["#Shorts"]
        title_words = [w.strip("#").capitalize()
                       for w in script.get("title", "").split()
                       if len(w) > 3][:2]
        seed += [f"#{w}" for w in title_words]
        seed += ["#AI", "#Tech"]
        tags = seed

    # normalise: ensure leading '#', dedupe (case-insensitive), ensure #Shorts
    seen, out = set(), []
    for t in tags:
        t = t if t.startswith("#") else f"#{t}"
        key = t.lower()
        if key not in seen:
            seen.add(key)
            out.append(t)
    if "#shorts" not in seen:
        out.insert(0, "#Shorts")
    return out[:5]                      # platform-friendly cap


def _auto_description(script: dict) -> str:
    meta = script.get("metadata") or {}
    if meta.get("description"):
        return meta["description"].strip()
    # Build from the narration of the scenes.
    bits = []
    for sc in script.get("scenes", []):
        n = (sc.get("narration") or "").strip()
        if n:
            bits.append(n)
    desc = " ".join(bits)
    desc = " ".join(desc.split())
    return desc[:300]


def build(script: dict, out_path: str) -> str:
    """Write the metadata sidecar. Returns the path."""
    title = _truncate_title(script.get("title", "Untitled"))
    desc = _auto_description(script)
    tags = _auto_hashtags(script)
    channel = script.get("channel", "")

    lines = [
        "TITLE (<60 chars):",
        f"  {title}",
        "",
        "DESCRIPTION:",
        f"  {desc}",
        "",
        "HASHTAGS:",
        f"  {' '.join(tags)}",
    ]
    if channel:
        lines += ["", "CHANNEL:", f"  {channel}"]

    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(out_path)


if __name__ == "__main__":
    import json
    demo = {
        "title": "5 AI Facts You Need to Know Right Now Today",
        "channel": "@YourChannel",
        "metadata": {"hashtags": ["AI", "MachineLearning", "tech"]},
        "scenes": [{"narration": "Here are five facts."},
                   {"narration": "AI is changing everything."}],
    }
    print(build(demo, "demo_meta.txt"))
    print(Path("demo_meta.txt").read_text())
