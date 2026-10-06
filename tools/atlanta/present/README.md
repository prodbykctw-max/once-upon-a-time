# Presentation renders

Client-facing stills and flyover videos of each Atlanta location, for showing
Jandé and Frédéric. Everything here is **generated** — the scripts are the
source of truth, the output is a convenience.

```bash
python3 -m http.server 8000          # from the repo root
node tools/atlanta/present/stills.js   # 18 stills  -> presentation/stills/
node tools/atlanta/present/flyover.js  # 6 videos   -> presentation/video/
```

## What they produce

**`stills.js`** — three framings per location at 1600×900: an establishing
hero shot, a street-level look, and the runner's own eye (the view the game is
actually played from). ~2 min for all six locations.

**`flyover.js`** — a 15-second 360° descent per location at 960×540, 24 fps:
one full revolution while the camera drops from overhead to street level and
closes in. Frames are captured deterministically (camera stepped, screenshot,
repeat) rather than screen-recorded, so the result is smooth no matter how slow
the render is. Encoded to H.264 with the ffmpeg that ships with Playwright.

## Why it takes so long

**~2.3 seconds per frame.** This container has no GPU, so WebGL runs through
SwiftShader on the CPU. 360 frames is ~14 minutes per location, ~80 minutes for
all six. Measured, not estimated — budget for it, and run it in the background.

Both scripts hide the dev chrome (`#hud`, `#pick`, `#bar`, the control pad)
before shooting. These are for a client, not a debug session.
