# CORNER TURN — ✅ SHIPPED (`4cb33bf`)

**Client, 2026-08-13:** *"On the royal runner, when you have to swipe to turn
left or right, the character and stage should actually turn."*

He is describing a real defect, and the reason it existed is worth writing down,
because the old code was not lazy — it was **geometrically the wrong effect**.

---

## Why the old corner could never read as a turn

A corner was `t3.turnFx = ±22` frames driving

```js
tShift = sin(π·t) · dir · 90        // px
FX.translate(tShift, 0)             // the 2D layer
GLW.draw(ai, wz, tShift*DPR)        // uShift, added after the perspective divide
```

— a 90px sideways slide of the whole frame, out and back over 0.37s.

The runner's projection is

```
s  = 300 / (300 + z)
sx = W/2 + wx·s + uShift
```

Work out what a **camera yaw of θ** does to it. Rotating the world about the
camera sends `X → X + θ·Z` to first order, and here `Z = 300 + z`, so the screen
displacement is

```
θ·(300 + z)·s = θ·(300 + z)·300/(300 + z) = 300·θ
```

**The same number of pixels at every depth.** A small yaw in this projection *is*
a uniform pan — they are the same operation. So the old effect was already a
camera yaw (θ = 90/300 ≈ 17°); it just cannot look like one, because near and far
move together and parallax is what the eye reads a rotation from.

That is the whole bug. Making the slide bigger, or slower, or eased differently
would never have fixed it.

## What a turn actually is

**The path bends.** A lateral world offset that grows with depth — the pseudo-3D
road curve every 2.5D racer has used since OutRun:

```
world x  +=  BEND · z²                     (in the shared GLSL PROJ string)
screen   =  BEND · z² · s  =  BEND · z² · 300/(300 + z)
```

Zero at her feet, growing ~linearly on screen with depth. The ground at her boots
sweeps one way while the path ahead swings the other, and *that* difference is
the corner.

The camera then **yaws into the bend** so the corner she is heading for stays
framed instead of sliding off the side — the old `uShift`, kept, but now derived
from the bend rather than being the whole effect:

```js
tShift = -TURN_FOLLOW · bendPx(TURN_FOCUS)
```

### The constants

| | | |
|---|---|---|
| `TURN_LEN` | 30 frames (~0.5s) | was 22 — a corner needs time to arrive |
| `TURN_FAR` | 0.46 | the far plane sweeps this fraction of **W** at the peak |
| `TURN_FOLLOW` | 0.55 | how hard the camera yaws to follow |
| `TURN_FOCUS` | 700 | the depth the camera keeps framed through the corner |

`TURN_FAR` is pinned to a **fraction of W**, not a pixel count, so the corner is
the same corner on every device. This is the project's recurring screen-vs-world
trap read the right way round: the bend genuinely *is* a screen-space quantity,
so it is expressed as one and derived from the world depth, rather than a raw
number that happens to look right on one phone.

### The envelope is asymmetric on purpose

```js
bend = sin(π · u^0.72) · dir          // u = progress 0→1 through the swing
```

`u^0.72` front-loads it: peak at ~37% of the window, then a longer settle. A
symmetric sine reads as a wobble out and back; this reads as a corner taken and a
new heading arrived at.

## What moves

One change to the shared `PROJ` string covers the whole GL world — terrain,
grass, the prop avenue and the library's hall walls and ceiling all curve
together. **All nine runner stages are `out:1`**, so the runner is 100% GL and
the 2D interior corridor in `drawT` is dead code there; the 2D work is the
entity layer (obstacles, gates, walls, pickups, coins — all off one `ex`), the
runway overlay's far edge, the sun and the god rays.

## Jandé banks

- **The pivot is her FEET.** Rotating about the sprite's centre swings her boots
  ~30px sideways and unsticks her from the floor.
- **A horizontal pinch** (to 0.82×) stands in for her shoulders coming round. The
  back-view sheet has no turned frames and none were invented — foreshortening is
  what selling the yaw costs without new art.
- **She stays INSIDE the camera yaw**, and this is a deliberate reversal of the
  first attempt. Drawing her outside it is more "correct" cinematically — the
  world turns around the pivot — but the bend is *zero at her depth*, so nothing
  is lost by keeping her in register with the near ground, and **collision is
  lane-based**: outside the yaw, an obstacle passing her mid-swing sits ~0.6 of a
  lane from where it actually is. Her outward (centrifugal) swing is 0.16·laneW
  for the same reason. The turn she performs is the bank, not a slide.

## The terrain skirt

At the peak the ground swings ~0.78·W sideways at mid depth, and the old mesh
(`|x| ≤ 3.8·corrW`) left the far shoulder inside the screen edge around z≈700. It
now carries a skirt out to ±7.

Two rules came out of that:

- **The original 31 columns keep their exact x.** Hill height is evaluated
  per vertex and interpolated between them, so simply re-spacing a wider mesh
  changes the terrain silhouette *with nothing turning*. The skirt is appended
  outside them, not spread through them.
- **The hill profile is clamped** at its old maximum (`edge ≤ 2.95`, which is
  exactly the value at the old outer column). Without it the new outer rows rear
  up as cliffs. For `|x| ≤ 3.8` the clamp is a no-op by construction.

## Verification

**The control is the point.** A uniform 90px pan of the same frame — the old
corner — measures **−42px in all four depth bands at r = 1.00**. The turn
measures **−25 / −34 / −16 / +28** across those same bands: four different
numbers, crossing sign with depth. A pan cannot do that.

(Band magnitudes are compressed against the model because a screen band mixes
depths — a near tree's canopy sits high in the frame. Same limitation the depth
cards hit; same answer: an exact readout hook rather than correlation.)

- **`_devTurn(bend)`** gives the exact per-depth figures and redraws at that bend
  *without advancing the world*, so two frames can be compared with the turn as
  the only difference between them: `pan −41.9` at her feet, `+6.7` at z=500,
  `+76.7` at z=993, `+137.5` at the far plane.
- **End-to-end:** played to a real corner, swiped it, `bend` ran 0 → 1 → 0 over
  30 frames and the turn scored (`stats.tn` 1).
- Stages **0** (the enclosed library hall — the hardest case, walls and ceiling
  must curve without tearing), **4** and **7** (tallest hills) all render straight
  and at both peaks with **zero page errors** and no terrain gaps.
- Median frame **1.0–1.6ms**, unchanged. The bend is four multiply-adds in a
  vertex shader.

## Tuning knobs

`TURN_LEN` · `TURN_FAR` · `TURN_FOLLOW` · `TURN_FOCUS`, all together at the top
of the projection block. The hero's bank is `0.26` rad and the pinch `0.18` in
`drawT`'s hero section. A play-test pass can move any of them without touching
layout code.

## If you touch this again

- **Do not "simplify" the bend back into `uShift`.** They are not the same thing
  and the whole document above is why.
- Raising `TURN_FAR` past ~0.6 walks the ground off the frame again before the
  fog can hide it — the skirt buys ±7, not infinity.
- `bendPx` clamps z at 0. Behind the camera `z²` is positive and would flip the
  bend's sign.
