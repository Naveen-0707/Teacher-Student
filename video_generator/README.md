# Shorts / Reels Generator

Turn a JSON script into a complete, upload-ready vertical video (1080×1920) for
**YouTube Shorts** and **Instagram Reels** — animation + natural voice + synced
burned-in captions + ducked background music + metadata. Runs **locally and free**
(no paid API, no keys).

```
script.json ─▶ Manim render ─▶ exact duration ─▶ TTS voice (+word timings)
            ─▶ karaoke captions (ASS) ─▶ music ducked under voice ─▶ burn captions
            ─▶ concatenate ─▶ final .mp4 + metadata.txt
```

## Why it's built this way (research-backed)

The defaults encode what actually drives reach on Shorts/Reels:

| Decision | Reason |
|---|---|
| **Auto "hook" scene** in the first ~2s | Completion / "viewed-vs-swiped" is the #1 ranking signal; viewers decide in 1–2s. |
| **Burned-in captions on by default** | ~85% watch muted; captions lift retention ~40%. |
| **~35–50s default length** | Best completion-rate band; full 60s gets more impressions but lower completion. |
| **Safe-zone-aware layout** | Keeps text/visuals clear of the status bar, caption bar, and right action buttons. |
| **Original voice + ducked royalty-free music** | Best mix of reach and monetization; music drops under narration automatically. |
| **Metadata sidecar** | Title <60 chars, 3–5 hashtags incl. `#Shorts`, value-first description. |

## Setup

```bash
pip install -r requirements.txt           # manim, edge-tts, …
# FFmpeg (with libass) must be on PATH:
#   Ubuntu/Debian: sudo apt install ffmpeg     (includes libass)
#   macOS:         brew install ffmpeg
#   Windows:       a static build from ffmpeg.org

python generate.py setup                   # downloads offline voice + CC0 music, runs checks
python generate.py setup --check           # just verify FFmpeg/libass + deps
```

## Quick start

```bash
cp script_example.json my_script.json      # then edit it
python generate.py script my_script.json -q preview   # fast check
python generate.py script my_script.json -q high      # final upload
# → output/final/<Title>.mp4  +  <Title>.txt
```

## Voice options

All free. edge-tts is the default and gives the best quality + free word-level
caption timing.

| Engine | Flag | Notes |
|---|---|---|
| **edge-tts** (default) | `--engine edge` | Microsoft neural voices, no key, needs internet. Word-synced captions. |
| **Piper** (offline) | `--engine piper` | Open-source, runs fully local. `generate.py setup` downloads a voice. |
| **Kokoro** (offline) | `--engine kokoro` | Alternative offline voice (`pip install kokoro soundfile`). |
| **Your own voice** | per-scene `"audio_file"` | Drop a `.wav`/`.mp3`; truly human. Captions sync to it. |

`python generate.py voices` lists edge voices. If edge can't reach the network it
auto-falls back to Piper, then pyttsx3.

## Script JSON

Top-level keys (all optional except `title`/`scenes`):

```jsonc
{
  "title": "5 AI Facts You Need to Know",
  "channel": "@YourChannel",
  "voice_engine": "edge",            // edge | piper | kokoro | pyttsx3
  "voice": "en-US-GuyNeural",
  "quality": "high",                 // preview | draft | high
  "length_target": 42,               // seconds (band 35–50)
  "auto_hook": true,                 // prepend a 2s hook from the title
  "loop": false,                     // add fade so it loops smoothly
  "captions": { "enabled": true, "style": "tiktok", "karaoke": true },
  "music":    { "enabled": true, "genre": "energetic", "volume_db": -18, "duck": true },
  "metadata": { "description": "…", "hashtags": ["#Shorts", "#AI"] },
  "scenes": [ … ]
}
```

Per-scene keys:

```jsonc
{
  "template": "title_card",          // see templates below
  "duration": 8,                     // seconds (else auto from length_target)
  "narration": "Spoken line → drives the captions.",
  "accent": "cyan",                  // cyan|purple|green|gold|pink|orange
  "captions": true,                  // per-scene override
  "audio_file": "vo.wav"             // optional: use a recorded voice instead of TTS
  // + template-specific keys (title/subtitle, heading/body, bullets, labels/values, hook_text)
}
```

### Templates

| Template | Key fields |
|---|---|
| `hook` | `hook_text`, `subtext` |
| `title_card` | `title`, `subtitle` |
| `text_reveal` | `heading`, `body` |
| `bullet_points` | `title`, `bullets[]` |
| `stats_chart` | `chart_title`, `labels[]`, `values[]` |
| `neural_network`, `neural_training`, `matrix_rain`, `code_typing`, `gaming_intro`, `xp_bar`, `achievement`, `data_flow` | reused animated scenes (visual only) |

## Commands

```bash
python generate.py list                 # scenes & templates
python generate.py voices               # TTS voices
python generate.py setup [--check]      # assets + capability check
python generate.py render <scene> -q preview     # render one scene
python generate.py script <file.json> [flags]    # full video
```

Script flags: `-f/--format shorts|instagram|youtube`, `-q/--quality`,
`--engine`, `--voice`, `--length`, `--music FILE`, `--no-music`,
`--no-captions`, `--no-hook`, `--loop`, `-o/--output`.

## Notes

- Background music must be royalty-free / CC0 for monetized videos. `setup`
  fetches a small CC0 starter pack; add your own files to `assets/music/`
  (filenames containing a genre word, e.g. `energetic_*.mp3`, are matched by `genre`).
- `assets/` and `output/` are git-ignored.
- Captions require FFmpeg built with **libass** — verify via `setup --check`.
