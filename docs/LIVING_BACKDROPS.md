# LIVING BACKDROPS — ✅ SHIPPED · MULTIPLANE on 8 of 9 stages

> **The library is deliberately NOT carded — see "The one plate that must stay
> flat" below.** It is a decision, not a gap.

> **Update 2026-08-11 — the backdrop stopped being one flat image.**
> Stages **1, 2, 3, 4 and 8** are now an inpainted base plate plus 5–8 cut
> **cards**, each scrolling at its own rate. Cut by `tools/depth` (SAM), wired by
> `drawCards`. Method and rate model are **prodbyKCTW's**, from his Techniques
> doc for *Will Hill: Player One*. Stages 0, 5, 6, 7 remain on the flat path
> until their cuts land.

## The one plate that must stay flat — ONCE UPON A PAGE

The library cut *ran*, cleanly: 91.0% coverage (up from 62.9% in dense mode),
recompose 0.000%, four tidy bands. It was thrown away anyway.

Its bands are the building's three **floors**, stacked vertically. They are not
depth planes — they are all at roughly the same distance. Give them different
rates and the columns that run through all three floors shear apart. That is
approach #1 on the doc's own "does not work" list: *horizontal bands slice
straight through objects.*

It is also the plate that already reads as a space, because that painting has
real perspective built into it — receding shelves, arched windows at an angle,
cast shadows. It is the one the client singled out as working. Carding it by
floor band would have actively broken the best backdrop in the game.

**Coverage is not the goal; usable cards are.** A plate can cut perfectly and
still be the wrong thing to cut.

## Dense plates need sub-crops, not a bigger grid

Four plates came in far below the rest — library 62.9%, glade 61.8%, golden hour
71.9%, sky gardens 74.1%. The doc is explicit that raising `points_per_side` does
not find small detail, and that held. What worked was `crop_n_layers=1`, which
re-runs SAM on sub-CROPS so each region is seen at higher *effective resolution*,
paired with the area floor and confidence dropped further (`pred_iou` 0.62,
`stability` 0.74, `min_region` 25):

| plate | before | after |
|---|---|---|
| library | 62.9% | **91.0%** |
| sky gardens | 74.1% | **80.9%** |
| golden hour | 71.9% | 76.4% |
| glade | 61.8% | 68.3% |

**Unclaimed pixels are not holes.** They simply stay on the base plate, so low
coverage means less of the image parallaxes — degraded, never broken.

## Character scale — the zoom, and why both constants had to move

**Client:** *"Can we zoom in on the characters a bit more? Jandé and the enemies
definitely deserve to be seen clearly."* Then: across the board.

`ZOOM = min(BASE, W/VIEW_W*BASE, H/VIEW_H*BASE)`. **Portrait is width-bound**
(the `W/VIEW_W` term wins on a narrow screen); **landscape is cap-bound** (`BASE`
wins). Move one constant and only one orientation changes. Both moved:
`BASE` 0.78 → **0.92**, `VIEW_W` 520 → **440**.

That asymmetry is also why the same character was **6.0%** of the screen in
portrait and **17.2%** in landscape — nearly three times the size sideways.

| | ZOOM | hero | foe (44×48 world) |
|---|---|---|---|
| portrait | 0.585 → **0.815** | 50 → **70px** | 26×28 → **36×39px** |
| landscape | 0.780 → **0.920** | 67 → **79px** | — |

**Where to stop is read-ahead, not taste.** She now sees **9.3 tiles ahead** in
portrait. The NES showed 16 tiles with Mario at ~40% across — **~9.6 ahead** — so
this lands *on* the reference. The next notch (BASE 0.98 / VIEW_W 400) makes her
82px but drops read-ahead to 7.9 tiles, below anything the genre does. Reaction
time is not worth trading for size.

Nothing else moves: the ground line is `GROUNDF*H` **by construction**, so it is
unchanged; the backdrop is screen-space and sized off `H`, so the cards and their
rates are untouched.

## The rate spread

```
rate = BASE + (depth − 0.5) × SPREAD        BASE 0.045, SPREAD 0.010
separation from the base plate clamped to ±80px
```

A wide spread does **not** read as depth — it reads as the set falling over.
Cards slide off each other, the empty plate shows through, and because each card
wraps on its own phase a fast card migrates a whole plate width across a level.
The target is the **lenticular** effect: small enough that nothing distorts, with
depth coming from *relative* rates.

**Measured on Mirror Lake**, camX 47 → 10047, via the exact `_devCards` hook:

| card | separation from base |
|---|---|
| sky | **+45px** |
| mountains | +25px |
| midhills | +5px |
| willows | −26px |
| water | −42px |
| shore (ground strip) | −300px, at its clamp |

87px of total spread across a 10,047px stage = **0.87%**, against his measured
77px/7680px = 1.0%. Same regime.

**Image correlation cannot verify this honestly** — cards overlap on screen and
the static HUD sits over the top rows. Two attempts confidently reported +0px for
cards that were plainly moving. `_devCards` reports the computed offsets directly.

## The ground-strip exception, and where it does NOT apply

A verge/shore/path gets a **real** rate (2.2×) and a loose clamp. The clamp
exists to stop a *discrete object* migrating, and that failure needs a landmark
to be visible on; a featureless full-width band has none. All you see is that it
outruns the scenery, which is the cue that it is nearer.

**The water is deliberately excluded.** Mirror Lake's reflections are painted in,
and they *are* a landmark — let the water outrun the willows and the reflections
stop lining up with the trees casting them.

## Wind and ripple belong to cards now

A willow card shears about **its own base** — for a cut willow that is exactly
where the trunk meets the shore — and is subdivided into 4 *within* the card, so
sections of one crown drift out of step instead of the cutout leaning like a
board. The water card ripples in rows. Mirrored tiles mirror their cards' x
positions, or the cards detach from the plate they were cut from.

## Retired on card stages

The **near band** (3.5×) and the **foreground plane** (1.7×) were stand-ins for
depth planes that did not exist, at rates far outside the spread that reads as
parallax. Both return early where a real cut exists. Stages still flat keep them
— half a depth cue beats none — and the two systems never run on the same stage.

## Cost

42 assets across 8 stages, **888 KB**. `web/` 5.26 → 6.13 MB. Median frame
time unchanged at 16.7ms.

---

*Everything below is the flat-plate era. It still governs stages 0, 5, 6 and 7.*

---

# LIVING BACKDROPS — flat-plate era (`95718dc`, real wind in `83f71df`)

> **Update 2026-08-10 — client:** *"On the Mirror Lake, the trees should be
> blowing in the wind. Those actual trees should be blowing… I need it to be
> animated… we're delivering a production grade game, I want the background to be
> production grade."* And: *"I don't think it will be butterflies inside the
> library."*

## Why the first pass wasn't wind

Row displacement moves an entire horizontal band **together**, so every tree at a
given height slides in lockstep. That reads as heat haze or water. It never reads
as wind.

Real wind bends each tree **about its own trunk**, and arrives in **gusts** that
roll along the treeline, leaving neighbours out of phase.

## Per-column shear

The canopy is drawn as vertical spans, each with a shear transform: zero
displacement at the pivot row (where trunks meet the ground), full swing at the
crown.

```
x' = x + k·(pivotY − y)/bandH   →   transform(1, 0, −k/bandH, 1, k·pivotY/bandH, 0)
```

`k` is a travelling wave **plus a slower travelling gust envelope** — without the
gust it is metronomic and reads as a mechanism.

Pivots and amplitudes are read off the art:

| stage | band (image fractions) | swing | why |
|---|---|---|---|
| 0 library | — | — | interior; no wind indoors |
| 1 meadow | 0.55–0.99 | 6px | foreground trees and hedgerow; distant hills stay solid |
| 2 petal mile | 0.00–0.60 | **14px** | the canopy *is* the stage |
| 3 rose waltz | 0.20–0.50 | 5.5px | **the marble colonnade is excluded** |
| 4 mirror lake | 0.04–0.645 | 11px | willows pivot exactly at the waterline |
| 5 glade | 0.00–0.92 | 4px | dusk, still air |
| 6 golden hour | 0.46–0.93 | 9.5px | sunflower heads pivot at the soil line |
| 7 sky gardens | 0.00–0.95 | 3.5px | island foliage stirs |
| 8 her encore | 0.88–1.00 | 6px | foreground trees only — **the castle is stone** |

## frq — why spatial frequency is per stage

**Client:** *"Shouldn't the sunflowers be blowing in the breeze too… they could
just be kind of moving back and forth."*

They already were. Measured before changing anything: the heads swung up to
**9px**, the base was pinned at **0**. The shear was working exactly as designed.

Sampling the left / middle / right thirds separately showed the real problem:

```
left  mid  right
   4    6      9
   8    8     10
  -6   -4     -1
```

**Every part of the field moved the same direction by the same amount.** A
uniform slide across near-identical flowers has no landmark to be read against,
so it looks like nothing at all. The willows read fine at the same setting only
because a big distinct trunk *is* a landmark.

So the fix is **frequency, not amplitude.**

The low frequency had been forced on every stage by the seam rule — but a seam is
only visible against **smooth** pixels. A band that is wall-to-wall texture hides
a 2px step completely. The sunflower band starts at 0.46 and contains **no sky**,
so it carries the highest `frq` in the game; Mirror Lake and Sky Gardens have open
sky inside their bands and stay at 1.0.

| stage | frq | why |
|---|---|---|
| 4 mirror lake · 7 sky gardens | **1.0** | open sky inside the band — seams would show |
| 1 meadow | 2.2 | some smooth grass |
| 3 rose waltz | 2.4 | greenery above the colonnade |
| 5 glade | 2.8 | dense fungal cover |
| 2 petal mile | 3.0 | dense blossom |
| 8 her encore | 3.2 | dark foreground treeline |
| **6 golden hour** | **4.2** | pure flower texture, no sky at all |

After: `12/8/3`, `15/10/5`, then `13/5/-2` and `-2/0/6` — neighbouring clumps rock
in **opposite** directions, which is what a breeze crossing a field looks like.
Costs nothing; the span count is untouched.

**Also fixed here:** a pale sliver down the left edge on strong gusts. `LB_PAD`
was 11 while a peak lean plus the span overlap could ask for ~17px, so the shear
sampled past the offscreen edge into nothing. Padding is now 28 with the clamp
(`LB_KMAX`) held at 20, strictly inside it.

## Two constraints, both measured

**Seams.** Adjacent spans lean by different amounts and the step shows as a
vertical line wherever the art is smooth — sky is the worst case. The step is
`amp × dPhase × spanWidth`. 14px spans at `x*0.0100` gave ~1.5px and were plainly
visible in the lake's sky. Dropping the spatial frequency to `x*0.0013` puts it
sub-pixel; verified by rendering the smooth half of the sky at 2× zoom.

**Frame rate.** A shear matrix takes canvas **off** its fast axis-aligned blit
path, so each span is a filtered textured quad and the **count** is what costs.
Isolated by probe on the heaviest stage:

| spans | median frame |
|---|---|
| 0 (no wind) | 16.7ms |
| 12 | **16.7ms** |
| 24 | **16.7ms** |
| ~30 (variable, merge-threshold) | 17.2ms |
| 49 (fixed 8px) | **20.0ms** — out of 60fps |

So `LB_SPANS` is **pinned at 16** rather than derived from a merge threshold, and
the wave frequency is chosen to keep seams sub-pixel at that width. Some phase
spread is traded for 60fps, deliberately. Median is back to 16.6–16.7ms on every
stage; p95 costs ~1.5ms.

## Butterflies and sparkles are outdoor-only

The winged sprites, floating cross-sparkles and birds were drawn on **every**
stage, including the library interior. `LIVEBG[ai].in` marks an interior and
gates all three. The library keeps what the client liked — the window shafts,
now stronger (6 rays at 0.20, was 5 at 0.13) — plus its dust motes.

---

*Original brief below, from the first pass. The row-warp section is superseded
for canopies (it still governs water); everything else stands.*

---

# LIVING BACKDROPS — original brief (`95718dc`)

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
