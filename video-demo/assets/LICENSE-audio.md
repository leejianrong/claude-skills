# Bundled audio: sources and license

All music and SFX in `music/` and `sfx/` were downloaded from [Mixkit](https://mixkit.co) on
2026-09-28, under Mixkit's Free License (separate license text for Stock Music and Sound
Effects, both linked from https://mixkit.co/license/). Summary of the terms as published by
Mixkit at the time of download:

- Free for commercial and personal use (this includes embedding in a video, e.g. a README
  demo clip — explicitly the kind of use case this skill produces).
- No attribution required.
- May not be resold or redistributed as a standalone, unmodified asset (i.e. don't publish
  `assets/music/upbeat-tech.mp3` itself as a downloadable stock asset — using it *inside* a
  produced video is fine).
- Music specifically: may not be remixed and re-registered/claimed as your own composition,
  and may not be used on physical media (CDs/DVDs), in video games, or in TV/radio broadcast.
- Full current terms: https://mixkit.co/license/ (view the "Stock Music Free License" and
  "Sound Effects Free License" cards).

Every file below was re-encoded (trimmed, loudness-normalized, faded, re-encoded to 128kbps
mp3) from the original download — none are redistributed byte-for-byte.

## Music (`music/`)

| File | Source URL | Mixkit category |
|---|---|---|
| `upbeat-tech.mp3` | https://assets.mixkit.co/music/110/110.mp3 | electronica |
| `minimal-clean.mp3` | https://assets.mixkit.co/music/506/506.mp3 | minimalism |
| `playful.mp3` | https://assets.mixkit.co/music/62/62.mp3 | chiptune |
| `corporate-energetic.mp3` | https://assets.mixkit.co/music/1002/1002.mp3 | corporate-music |

## SFX (`sfx/`)

| File | Source URL | Mixkit category |
|---|---|---|
| `click.mp3` | https://assets.mixkit.co/active_storage/sfx/1109/1109-preview.mp3 | click |
| `whoosh.mp3` | https://assets.mixkit.co/active_storage/sfx/1485/1485-preview.mp3 | whoosh |
| `pop.mp3` | https://assets.mixkit.co/active_storage/sfx/2354/2354-preview.mp3 | pop |
| `success-chime.mp3` | https://assets.mixkit.co/active_storage/sfx/2870/2870-preview.mp3 | correct |
| `transition.mp3` | https://assets.mixkit.co/active_storage/sfx/1168/1168-preview.mp3 | transition |

## Adding or replacing a track

Pick a category page under `mixkit.co/free-sound-effects/<category>/` or
`mixkit.co/free-stock-music/<category>/`, grab a direct `assets.mixkit.co` link from the
page source, then normalize it to match the rest of the library:

```bash
# music (trim to 35s, fade in/out, normalize loudness)
ffmpeg -i in.mp3 -t 35 \
  -af "loudnorm=I=-18:TP=-2:LRA=11,afade=t=in:st=0:d=0.5,afade=t=out:st=33.5:d=1.5" \
  -codec:a libmp3lame -b:a 128k -ar 44100 -ac 2 assets/music/<mood>.mp3

# sfx (normalize loudness only)
ffmpeg -i in.mp3 -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -codec:a libmp3lame -b:a 128k -ar 44100 -ac 2 assets/sfx/<name>.mp3
```

Add the new file's source URL to the tables above.
