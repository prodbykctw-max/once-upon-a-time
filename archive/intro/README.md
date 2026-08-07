# Archived intro animation

Retired on 2026-07-21 at the client's request — the old cutscene no longer
fits the game's direction. A new intro will be produced later.

## Files
- `intro.mp4` — the original ~153KB embedded cutscene, decoded from the
  base64 data-URI that used to live in `index.html`.
- `introScreen.html` — the exact `#introScreen` markup block (video + skip
  button) as it was embedded in the game.
- `intro.js` — the `playIntro()` / `endIntro()` functions that drove it.

## How it was wired (for whoever rebuilds it)
- `#tPress` (the title-screen "BEGIN") called `playIntro()`.
- `playIntro()` showed `#introScreen`, played `#introVid`, and fell back to a
  tap-to-play prompt if autoplay was blocked; a 6s safety timer + the video's
  `ended` event both called `endIntro()`.
- `endIntro()` hid the screen and called `show('loginScreen')`.

## To restore / replace
1. Base64-encode the new video: `base64 -w0 new_intro.mp4`.
2. Paste `introScreen.html` back into `index.html` just before `#titleScreen`
   (or wherever the new flow wants it) and swap the `<source src>` data-URI.
3. Paste `intro.js` back and re-point `#tPress`'s onclick from the current
   `show('loginScreen')` back to `playIntro()`.
