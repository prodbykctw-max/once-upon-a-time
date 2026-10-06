# Presentation renders

Client-facing stills and flyover videos of each Atlanta location, for showing
Jandé and Frédéric. Everything here is **generated** — the scripts are the
source of truth, the output is a convenience.

```bash
python3 -m http.server 8000          # from the repo root
node tools/atlanta/present/stills.cjs   # 18 stills  -> presentation/stills/
node tools/atlanta/present/flyover.cjs  # 6 videos   -> presentation/video/
```

## What they produce

**`stills.cjs`** — three framings per location at 1600×900: an establishing
hero shot, a street-level look, and the runner's own eye (the view the game is
actually played from). ~2 min for all six locations.

**`flyover.cjs`** — a 15-second 360° descent per location at 960×540, 24 fps:
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


## Two traps these scripts exist to not re-learn

**`.cjs`, not `.js`.** The repo's `package.json` carries `"type": "module"`, so
a `.js` file here is an ES module and `require` is undefined. These scripts are
CommonJS. They ran fine in a scratch directory — which has no `package.json` —
and failed the moment they moved into the repo.

**Not Playwright's ffmpeg.** `/opt/pw-browsers/ffmpeg-*/ffmpeg-linux` is a
minimal build for Playwright's own WebM recordings: it ships `png` and `libvpx`
and nothing else, so `-c:v libx264` fails, and it cannot open an image sequence
at all. The error it gives for a directory full of frames is **"No such file or
directory"**, which sends you hunting for missing files that are all present.
Use `imageio-ffmpeg` (`pip install imageio-ffmpeg`), which carries a full build
with libx264.

The flyover job is **resumable** — a location whose `.mp4` already exists is
skipped — because at ~14 minutes each, something will interrupt a six-location
run.
