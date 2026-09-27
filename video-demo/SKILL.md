---
name: video-demo
description: Record a 10-30 second MP4 showcase video of a software project's CLI or web app for a GitHub README, driven entirely by the agent — no screen-recording software operated by a human. Scripts the capture deterministically (VHS for terminal/CLI apps, Playwright for web apps), then mixes in bundled royalty-free background music and cued sound effects (no voiceover) plus optional short on-screen captions, encoding a final mp4 sized to fit GitHub's upload limits. Use when asked to record, create, or generate a demo video, showcase video, or README video for a project, to turn a CLI or web app into a short promo/demo clip, or to "make a video of the app in action" where an actual produced video — not a manual screen recording — is wanted.
---

# video-demo

Produces one artifact: a finished mp4, ready to drag into GitHub's file editor. It does not
upload or embed the video into the README — that last step stays manual by design.

## Workflow (copy this checklist into your response and check items off)

- [ ] Run `scripts/preflight_check.sh`; install anything missing before proceeding
- [ ] Inspect the target project to understand what it does and its single best demo-worthy flow
- [ ] Draft a shot list (beats, order, chosen music mood, target duration) and get it approved
- [ ] Pick a capture backend and script the capture (tape file or Playwright script)
- [ ] Run the capture, producing a silent video
- [ ] Build a cue sheet (and captions, if used) from the capture
- [ ] Run `scripts/mux_audio.py` to produce the final mp4
- [ ] QA the output (ffprobe + caption frame checks) before handing it back

### 1. Preflight

```bash
scripts/preflight_check.sh
```

Reports what's missing and how to install it (never installs anything itself). `ffmpeg`,
`ffprobe`, and `python3` are always required; `vhs` only for CLI capture, `playwright` only
for web capture.

### 2. Understand the project, then draft a shot list

Read the README, entry point, and package manifest to find the one flow that best proves the
project's value — not a feature tour. Draft a short beat-by-beat storyboard as plain text:

```
Shot list (target: 18s)
Mood: upbeat-tech
1. [0.0-2.5s]  App launches, empty state visible
2. [2.5-6.0s]  User runs `myapp search cats` → results appear (sfx: pop)
3. [6.0-9.0s]  User adds --format table flag → table renders (sfx: success-chime)
4. [9.0-11s]   Hold on final result
Captions: "Instant search" (2.5-4.5s)
```

**Show this to the user and wait for approval before recording.** Redoing a bad take costs
real time; a text checkpoint costs nothing.

### 3. Capture

Pick the backend that matches the project:

- **CLI/terminal app** → [references/cli-capture-vhs.md](references/cli-capture-vhs.md).
  Author a `.tape` file; VHS renders it deterministically. Cue timestamps are computed from
  the tape's own authored timings.
- **Web app** → [references/web-capture-playwright.md](references/web-capture-playwright.md).
  Script a Playwright session; cue timestamps are logged as real wall-clock offsets while the
  script runs.

Either way, the output is a silent video file (mp4 or webm — both are fine as input to the
next step) matching the approved shot list's timing and duration.

### 4. Mux audio and captions

[references/audio-mixing.md](references/audio-mixing.md) has the full cue sheet / captions
JSON schemas, the bundled music moods and SFX names, and the size-budget math. Run the script
directly rather than reimplementing the ffmpeg filter graph by hand:

```bash
python3 scripts/mux_audio.py \
  --video demo.mp4 --music upbeat-tech \
  --cues cues.json --captions captions.json \
  --out final.mp4
```

Defaults: 1280px wide, ≤8MB (comfortably under GitHub's 10MB free-tier cap — raise
`--max-size-mb` if the target repo is on a paid plan with the 100MB cap).

### 5. QA before handing off

- `ffprobe` the output: duration matches the approved shot list, size is within budget.
- If captions were used, extract a frame during each caption window and inspect it for
  clipping or overlap with important UI (see audio-mixing.md for the exact command).
- Report the final path, duration, and size to the user. Embedding it in the README (drag
  the file into GitHub's web editor to get a `githubusercontent.com` URL) is a manual next
  step, not part of this skill.

## Assets bundled here

- `assets/music/` — four ~35s mood loops: `upbeat-tech`, `minimal-clean`, `playful`,
  `corporate-energetic`. Pre-faded; `mux_audio.py` trims to exact video length.
- `assets/sfx/` — five one-shots: `click`, `pop`, `whoosh`, `success-chime`, `transition`.
- `assets/LICENSE-audio.md` — source and license for every bundled file, and how to add more.

## Design decisions worth knowing

- **No voiceover.** Music + cued SFX + optional captions only. Don't add TTS narration.
- **MP4 only**, not GIF — smaller for the same quality, and this skill exists specifically
  because GIF-based demo tooling was the well-covered path already.
- **The agent drives the app** (scripted tape/Playwright), never a human operating a screen
  recorder — that's what makes cue-synced SFX possible without post-hoc audio editing by ear.
