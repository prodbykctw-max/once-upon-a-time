# LIVING BACKDROPS — ✅ SHIPPED (`95718dc`)

**Client, 2026-08-10:** *"Can the background of each stage come to life? Like
become more immersive? Now it just looks like a picture. A beautiful picture but
still a flat photo. Can we bring the exact image to life?"*

Scope: **ACTION RPG only.** Royal Runner is a 3D world and is untouched.
**No new art** — `web/` is unchanged, all 55 references still match disk.

---

## Why it read flat

Two independent reasons, both structural:

1. **One plane, one speed.** The whole painting scrolled at `cam*0.045`. Sky,
   mountains, mid-ground trees and foreground grass all moved together. That is
   the literal definition of a photograph on a conveyor belt — there is no
   parallax, so there is no depth.
2. **Nothing moved inside it.** No wind, no water, no changing light. A still
   image can be beautiful and still read as a backdrop rather than a place.

The fix animates **the existing paintings**, rather than covering them with
effects or replacing them with new art.

---

## 1 · Row warp — the painting moves

Each painting is composited into a padded offscreen and blitted back **as
horizontal rows, each with its own x-offset.**

**Water ripple.** Mirror Lake and Her Encore already have their reflections
*painted in*. Rippling those rows is therefore free realism — the reflection was
always there, it just never moved. Amplitude grows toward the bottom of the band,
because nearer water has bigger waves.

**Canopy breeze.** Strongest at the treetops, tapering to **zero** where the
trunks meet the ground — which is what wind actually does to a treeline. A
uniform offset would read as a heat haze.

Bands are **fractions of the image**, read off the actual art, so they stay
correct at any `GROUNDF`, any zoom, any orientation:

| stage | water | canopy sway | notes |
|---|---|---|---|
| 0 ONCE UPON A PAGE | — | — | indoors: no wind, no water |
| 1 FIRST LIGHT MEADOW | — | 0.58–0.98 | foreground grass only — the distant hills must not wobble |
| 2 THE PETAL MILE | — | 0.00–0.56 | the whole top is canopy; strongest breeze in the game |
| 3 THE ROSE WALTZ | — | 0.28–0.72 | hedges behind the colonnade. **The stone must not move** |
| 4 THE MIRROR LAKE | **0.645–1.00** | 0.08–0.60 | waterline read off the art; willows above, lake below |
| 5 THE WISHING GLADE | — | 0.00–1.00 | soft, whole-frame breathing |
| 6 THE GOLDEN HOUR | — | 0.50–0.90 | the sunflower field nods |
| 7 THE SKY GARDENS | — | — | nothing to sway; the cloud sea carries the motion |
| 8 HER ENCORE | **0.70–0.90** | — | the river with the sunset on it |

## 2 · Near band — the second depth plane

A thin slice of the painting's **own base**, redrawn at **3.5× the parallax** and
crushed to a silhouette. Two planes at different speeds is what actually creates
depth.

It is crushed **on purpose**: at full brightness you read it as the same tree
twice, which is worse than no parallax at all.

## 3 · God rays

Anchored to each painting's **real** light source — Golden Hour's sun genuinely
is at x=0.29, the library's windows genuinely are up top — with dust motes
drifting inside them.

## 4 · Life at three depths

Petals · fireflies · pollen · motes · embers · cloud · birds. Each tier has its
own parallax rate, size, alpha and drift speed.

**The difference in speed *is* the depth cue.** One layer of petals reads as
stickers stuck to the glass; three layers reads as air.

Positions are deterministic per index (`_uh`) — `Math.random()` would strobe at
60fps.

---

## Three bugs found while building it

**The row-batching loop never flushed its final run.** Runs are flushed when the
offset *changes*; the run that reaches the bottom edge never sees a change. On a
canopy-only stage that meant **two thirds of the painting was never drawn** —
raw sky gradient with the aerial wash over it. Caught by rendering against the
deployed build side by side, not by reading the code. The final flush is
mandatory, and the comment in the source says so.

**`_amb` was declared below the code that reads it.** The reduce-motion flag
lived next to the sparkle loop, ~160 lines *below* the new pass. `var` hoists the
binding but **not** the assignment, so it was `undefined` there and every
animated term silently evaluated false. Moved to the top of `drawMansionBG`.
*A motion flag that fails closed is exactly the bug that ships as "it just didn't
work on my phone."*

**The near band drew the full painting and clipped 86% of it away** — three
full-size image draws per frame for a strip the height of a hedge. `_lbTileSlice`
now blits only the source slice.

---

## Performance

Measured over 300 frames at 390×844, against the deployed build:

| stage | median | p95 | worst |
|---|---|---|---|
| 2 (heaviest: wide canopy + near band) | 16.7 → **16.7** | 17.9 → **18.4** | 29.7 → **31.6** |
| 6 | 16.7 → **16.7** | 17.9 → **18.1** | 22.8 → **20.5** |
| 4 | 16.7 → **16.6** | 17.4 → **18.5** | 19.5 → **25.0** |

Median is vsync-locked and unchanged everywhere; p95 costs ~0.5ms. Row height is
5px on mobile vs 4px on desktop, and unchanged rows are batched into single
draws, so a stage with one narrow band costs a handful of extra calls rather than
one per screen row.

## Reduce motion

Every animated term is multiplied by `amb` (0 under reduce-motion), so the whole
system degrades to a **still painting** rather than a broken or absent one.

## Tuning

All of it is the `LIVEBG[]` table — one row per stage, `{wat, swy, ray, amb,
near, bre}`. Amplitudes, band fractions, ray counts and life density can all be
moved without touching the draw code.

## Verification

Syntax clean · all 9 stages × both orientations with zero page errors ·
reduce-motion renders (`body.rm` true, no errors) · Royal Runner unchanged ·
boss arena holds · death plane still fires at 854 · glyph gate clean · `web/`
references match disk exactly, **no new assets**.
