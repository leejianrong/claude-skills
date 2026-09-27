# Muxing music, SFX, and captions with `mux_audio.py`

## Contents
- [What the script does](#what-the-script-does)
- [Cue sheet schema](#cue-sheet-schema)
- [Captions schema](#captions-schema)
- [Bundled music moods](#bundled-music-moods)
- [Bundled SFX](#bundled-sfx)
- [Running it](#running-it)
- [Size budget math](#size-budget-math)
- [QA after muxing](#qa-after-muxing)

## What the script does

`scripts/mux_audio.py` takes a silent captured video (from either capture path) plus a music
mood, an optional cue sheet, and optional captions, and produces a single finished mp4:
scales video to the target width, burns in any captions, builds a background music bed
(trimmed to the video's exact length with a fade-out), layers SFX at their cued timestamps,
normalizes the final audio loudness, and encodes at a bitrate computed to land under a size
budget. Run it directly — don't reimplement this pipeline by hand; the bitrate math and
retry-on-oversize logic are already handled.

## Cue sheet schema

A JSON list of `{"sfx": "<name>", "t": <seconds>}`, one entry per SFX hit:

```json
[
  {"sfx": "click", "t": 1.2},
  {"sfx": "pop", "t": 4.8},
  {"sfx": "success-chime", "t": 11.0}
]
```

`t` is seconds from the start of the video. `sfx` must match one of the
[bundled SFX](#bundled-sfx) names. Omit `--cues` entirely for a music-only clip.

## Captions schema

A JSON list of `{"text": "...", "start": <seconds>, "end": <seconds>}`:

```json
[
  {"text": "Instant search", "start": 1.0, "end": 3.0},
  {"text": "Cmd+K anywhere", "start": 4.5, "end": 6.5}
]
```

Keep each `text` short — under ~28 characters — so it fits on one line at the default 42pt
size; the script does not auto-wrap. Leave a gap between one caption's `end` and the next
`start` so they don't visually overlap.

## Bundled music moods

| Mood | Vibe | Good fit for |
|---|---|---|
| `upbeat-tech` | Driving, modern, synth-forward | Dev tools, CLIs, technical products |
| `minimal-clean` | Sparse, understated, low-key rhythm | Anything where the UI should carry the attention |
| `playful` | Bouncy, light, game-like | Consumer apps, creative tools, anything fun-first |
| `corporate-energetic` | Polished, confident, upbeat-but-safe | B2B / enterprise-facing projects |

Each track is a pre-trimmed ~35s loop with a built-in fade-out at the tail; `mux_audio.py`
trims it further to match your video's exact duration. See `assets/LICENSE-audio.md` for
sourcing and license terms.

## Bundled SFX

| Name | Use for |
|---|---|
| `click` | A button press, keystroke, or other discrete UI action |
| `pop` | An element appearing (a modal, a toast, a result card) |
| `whoosh` | A fast transition or swipe |
| `success-chime` | A task completing, a highlight-worthy result |
| `transition` | A scene or section change (longer, ~4s) |

## Running it

```bash
python3 scripts/mux_audio.py \
  --video demo.mp4 \
  --music upbeat-tech \
  --cues cues.json \
  --captions captions.json \
  --out final.mp4
```

Useful flags: `--width` (default 1280), `--max-size-mb` (default 8.0), `--music-volume`
(default 0.5, relative gain on the music bed), `--font-file` (override caption font if
auto-detection picks the wrong one on your machine).

## Size budget math

The script targets `--max-size-mb` (default 8.0, comfortably under GitHub's 10MB free-tier
cap for repo-hosted video) by computing a video bitrate directly from the clip's duration and
a fixed 160kbps audio track, rather than iterating blindly:

```
video_kbps = (max_size_mb * 8192 * 0.92) / duration_seconds - 160
```

If the resulting output still comes in over budget (container overhead varies slightly), it
re-encodes at 80% of the bitrate, up to 3 attempts, and prints a warning if it still can't hit
the target — at that point, shorten the clip or raise `--max-size-mb` rather than trusting
the retry loop indefinitely.

## QA after muxing

- `ffprobe -show_entries format=duration,size:stream=width,height final.mp4` — confirm
  duration matches your shot list and size is within budget (the script prints this too).
- Extract a frame during each caption window and inspect it — confirm text isn't clipped,
  overlapping important UI, or overlapping another caption:
  ```bash
  ffmpeg -y -ss <t> -i final.mp4 -frames:v 1 check.png
  ```
- Cross-check cue timestamps against the shot list you got approved — a cue a beat early or
  late reads as sloppy in a 10-30s clip where every second is noticeable.
