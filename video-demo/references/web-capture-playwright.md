# Capturing a web app demo with Playwright

## Contents
- [Why Playwright](#why-playwright)
- [Setup](#setup)
- [Recording config](#recording-config)
- [Logging real cue timestamps](#logging-real-cue-timestamps)
- [Worked example](#worked-example)
- [Common pitfalls](#common-pitfalls)

## Why Playwright

For anything running in a browser, Playwright drives the actual UI (clicks, typing,
navigation) and records the session as video. Unlike the VHS path, timestamps here don't
need to be hand-computed — the script logs the real wall-clock offset of each action as it
happens, which is both easier and more accurate for UI flows with variable-latency steps
(page loads, animations, network requests).

Use this path for any project whose demo-worthy behavior runs in a browser. For terminal/CLI
tools, use [cli-capture-vhs.md](cli-capture-vhs.md) instead.

## Setup

Check availability first with `scripts/preflight_check.sh`. If the browser binary is missing:

```bash
npx --yes playwright install chromium
```

## Recording config

Set the recording viewport to match (or exceed) your intended final resolution — e.g. 1280×720
— so `mux_audio.py`'s scale step never has to upscale:

```js
const context = await browser.newContext({
  viewport: { width: 1280, height: 720 },
  recordVideo: { dir: 'out/', size: { width: 1280, height: 720 } },
});
```

The video file is only finalized once the **context** closes — `await context.close()` must
run before the `.webm` file is readable. Playwright names the file with a random hash; get
the real path from `page.video().path()` before closing, not by guessing the filename.

`mux_audio.py` reads video via `ffprobe`/`ffmpeg`, so the input can stay as `.webm` — no need
to pre-convert to mp4 before muxing.

## Logging real cue timestamps

Track a start time once, then compute each beat's offset relative to it as you perform the
action — don't estimate, measure:

```js
const cues = [];
const started = Date.now();
const cue = (sfx) => cues.push({ sfx, t: (Date.now() - started) / 1000 });

await page.click('#search-button');
cue('click');
await page.waitForSelector('.results-panel');
cue('pop');
// ... more actions ...

fs.writeFileSync('cues.json', JSON.stringify(cues, null, 2));
```

Place the `cue(...)` call right after the action or wait it corresponds to, so the timestamp
reflects when that beat is visually complete, not when it started.

## Worked example

```js
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: { dir: 'out/', size: { width: 1280, height: 720 } },
  });
  const page = await context.newPage();
  const cues = [];
  const started = Date.now();
  const cue = (sfx) => cues.push({ sfx, t: (Date.now() - started) / 1000 });

  await page.goto('http://localhost:3000');
  await page.waitForTimeout(600); // let the initial paint settle before anything happens
  await page.click('#search-button');
  cue('click');
  await page.fill('#search-input', 'cats');
  await page.waitForSelector('.results-panel', { state: 'visible' });
  cue('pop');
  await page.waitForTimeout(1500); // hold on the result so it reads on screen

  const videoPath = await page.video().path();
  await context.close();
  await browser.close();

  fs.writeFileSync('cues.json', JSON.stringify(cues, null, 2));
  fs.renameSync(videoPath, 'demo.webm');
})();
```

## Common pitfalls

- **Leading blank frame.** `recordVideo` starts capturing before the first paint, so the
  first ~0.5-1s is often a blank frame. Architect the shot list so nothing important happens
  before ~1.2s (the `waitForTimeout(600)` above is deliberate), rather than fighting it with
  post-hoc trimming.
- **Closing the context too early.** The video file isn't flushed to disk until
  `context.close()` resolves — grab `page.video().path()` before closing, but don't try to
  read the file until after.
- **Viewport/recordVideo size mismatch.** If `viewport` and `recordVideo.size` differ, the
  page gets scaled and captured at the wrong dimensions. Keep them identical.
