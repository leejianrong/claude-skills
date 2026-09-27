# Capturing a CLI/terminal demo with VHS

## Contents
- [Why VHS](#why-vhs)
- [Setup](#setup)
- [Tape file essentials](#tape-file-essentials)
- [Computing cue timestamps from the tape](#computing-cue-timestamps-from-the-tape)
- [Worked example](#worked-example)
- [Rendering](#rendering)
- [Common pitfalls](#common-pitfalls)

## Why VHS

[VHS](https://github.com/charmbracelet/vhs) renders a `.tape` script — a plain-text list of
keystrokes, waits, and settings — into a video deterministically. That determinism is what
makes precise audio sync possible without instrumenting anything at runtime: every action's
timing is authored by you in the tape file, so the cue timestamps for `mux_audio.py`'s
`--cues` JSON are computable directly from the script you just wrote, not measured after the
fact.

Use this path for any project whose demo-worthy behavior lives in a terminal (a CLI tool, a
TUI, a REPL). For anything running in a browser, use
[web-capture-playwright.md](web-capture-playwright.md) instead.

## Setup

Check availability first with `scripts/preflight_check.sh`. If `vhs` is missing:

```bash
go install github.com/charmbracelet/[email protected]   # if Go is available
# or
brew install vhs                                       # macOS
```

## Tape file essentials

A tape is a sequence of commands, executed top to bottom. The ones that matter for a short
showcase clip:

| Command | Effect |
|---|---|
| `Output demo.mp4` | Render target. Use `.mp4` directly — no GIF intermediate needed. |
| `Set Width 1280` / `Set Height 720` | Match (or exceed) the final output size; `mux_audio.py` will scale down if needed, never up. |
| `Set FontSize 20` | Keep terminal text readable at 720p; smaller looks cramped in a README. |
| `Set TypingSpeed 50ms` | Default per-character typing delay — needed to compute cue timing (see below). |
| `Set Theme "..."` | Pick a theme with good contrast; avoid pure white-on-black if the project's own branding uses something else. |
| `Type "command here"` | Simulates keystrokes at `TypingSpeed`. |
| `Enter` | Submits the typed line. Takes effectively 0s. |
| `Sleep 500ms` | Explicit pause. Use generously between beats — it's what makes the timeline predictable. |
| `Hide` / `Show` | Hide setup/cleanup commands from the recording, show only the demo-relevant parts. |

## Computing cue timestamps from the tape

Track cumulative elapsed time as you write the tape, in the same order the commands execute:

- `Type "text"` costs `len("text") * typing_speed_seconds`
- `Enter` costs ~0s (negligible, ignore it)
- `Sleep Xms` costs `X / 1000` seconds

Sum these in order; the running total at the moment a beat completes (e.g. right after the
`Enter` that submits a command, or right after the `Sleep` that follows it) is that beat's
cue timestamp. Write both the tape and a matching `cues.json` together, beat by beat, rather
than trying to reconstruct timestamps after the fact.

**After rendering**, verify with `ffprobe`: if the actual video duration differs from your
hand-summed total (it usually will, slightly — VHS adds small fixed overhead per keystroke),
scale every cue timestamp by `actual_duration / expected_duration` before passing `cues.json`
to `mux_audio.py`. This keeps sync tight without needing frame-accurate hand tuning.

## Worked example

`demo.tape`:
```
Output demo.mp4
Set Width 1280
Set Height 720
Set FontSize 22
Set TypingSpeed 50ms
Set Theme "Dracula"

Hide
Type "clear"
Enter
Show

Sleep 500ms
Type "myapp search --query cats"
Sleep 800ms
Enter
Sleep 2000ms
Type "myapp search --query cats --format table"
Sleep 800ms
Enter
Sleep 3000ms
```

Cumulative time, beat by beat (`TypingSpeed` = 0.05s/char):
- `Sleep 500ms` → running total 0.5s
- `Type "myapp search --query cats"` (28 chars × 0.05s = 1.4s) → 1.9s
- `Sleep 800ms` → 2.7s
- `Enter` (submits first command — **cue beat 1**) → 2.7s
- `Sleep 2000ms` → 4.7s
- `Type "..." --format table"` (39 chars × 0.05s = 1.95s) → 6.65s
- `Sleep 800ms` → 7.45s
- `Enter` (submits second command — **cue beat 2**) → 7.45s
- `Sleep 3000ms` → 10.45s (end)

`cues.json`:
```json
[
  {"sfx": "click", "t": 2.7},
  {"sfx": "success-chime", "t": 7.45}
]
```

## Rendering

```bash
vhs demo.tape
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 demo.mp4
```

If the probed duration isn't ~10.45s, rescale the cues in `cues.json` by the ratio before
running `mux_audio.py`.

## Common pitfalls

- **Typing too fast to read.** 50ms/char is a reasonable floor for a showcase clip; slower
  (80-100ms) reads better on screen but eats into your 10-30s budget faster.
- **No `Sleep` after the last command.** The recording cuts off mid-beat. Always end with a
  `Sleep` long enough to let the final output register before the clip ends.
- **Forgetting `Hide`/`Show`.** Setup noise (clearing the screen, `cd`-ing into a directory)
  showing up in the final clip wastes seconds of a very short budget.
