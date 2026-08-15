# COLOUR GRADE — ✅ SHIPPED

**Client, 2026-08-13:** *"The lighting of the game is too bright — a sense of
white exposure, like it's too fuzzy. And it's too pastel, the colours aren't
rich like pixel art colour is rich. I want richness like that, that colour
depth. Certain colours gotta be strong."*

## It is not a feeling — it is a milky black floor

Measured before changing anything, on the source plates themselves:

| plate | darkest 1% (luma) | saturation |
|---|---|---|
| 1 · FIRST LIGHT MEADOW | **57.9** | 0.232 |
| 2 · THE PETAL MILE | **81.5** | 0.410 |
| 3 · THE ROSE WALTZ | **67.4** | 0.326 |
| 4 · THE MIRROR LAKE | **62.9** | 0.373 |
| 6 · THE GOLDEN HOUR | 63.0 | 0.898 |
| 8 · HER ENCORE | 46.4 | 0.487 |

**Nothing in these paintings is darker than luma 58/255, and the Petal Mile's
darkest 1% is 81.** That is the whole complaint in one number. Pixel art reads
rich because its palette runs to a true black and holds high chroma against it;
these plates never leave the upper two thirds of the range, so there is no depth
for a colour to *have*. Four of six also sit at 0.23–0.41 saturation.

The runner was worse. Rendered frames:

| | luma mean | darkest 1% | saturation | pixels > 200 |
|---|---|---|---|---|
| Sky Gardens | **225.4** | 118.8 | **0.183** | **84.6%** |
| Mirror Lake | 161.1 | 67.5 | 0.268 | 25.5% |

Five sixths of the Sky Gardens frame was above luma 200. That is the white
exposure, literally.

## Three fixes, one per measured cause

### 1 · The global grade

`brightness(0.93) contrast(1.20) saturate(1.34)` — exposure down, contrast to put
a real black back under the picture, saturation for the richness.

Applied to the **whole frame**, so painted backdrops, her sprite sheets, foes,
particles and the runner's GL world all move together and nothing drifts out of
step with anything else. **No art file is touched** — which matters here, because
her original side-view sheets are not to be modified. The HUD is DOM and
deliberately outside the grade, so the brand pink and gold stay exactly as
designed.

One knob: `--grade`.

### 2 · The runner's fog was the white-out

Distance blends toward `LOOK[].fog`, and four stages were fading everything to
paper:

| stage | fog was | luma | → fog now | luma |
|---|---|---|---|---|
| 2 · Petal Mile | `0.99, 0.90, 0.92` | 0.93 | `0.73, 0.70, 0.79` | 0.72 |
| 3 · Rose Waltz | `0.88, 0.95, 0.99` | 0.93 | `0.60, 0.72, 0.85` | 0.70 |
| 6 · Golden Hour | `0.99, 0.95, 0.78` | 0.94 | `0.79, 0.75, 0.57` | 0.74 |
| 7 · Sky Gardens | `0.94, 0.96, 1.00` | **0.96** | `0.62, 0.69, 0.83` | 0.69 |

Rebalanced hue-preserving: luminance capped at 0.74, channel spread widened
1.35×, **and the stage's own sky hue blended in ONLY where the fog had none of
its own.** That condition is not decoration — blending unconditionally
neutralised Golden Hour, whose haze is warm while its `skyTop` is blue, and
turned the one thing that made it golden into grey. Chroma now holds or rises on
every stage.

The fog *range* was left alone on purpose: the corner-turn skirt relies on far
terrain being fully fogged (see `docs/CORNER_TURN.md`), and a darker fog hides it
just as well as a white one.

### 3 · Ground exposure, per stage

Only one stage actually needed it. Ground texture brightness × its tint:

```
library 128   meadow 150   petal 144   rose 71   lake 116
glade 137     golden 106   skygardens 214 (!)    encore 141
```

Sky Gardens' ground was rendering at 214 against everyone else's 71–150, so its
`tint` alone was pulled to bring it in line. Nothing that was already fine got
touched. The sun's broad glare term also came down `0.12 → 0.10`.

## Where the grade lives is a PERFORMANCE decision

Measured, not assumed:

- Filtering the **2D canvas** costs **nothing** — 39.9ms vs 39.9ms, pure noise.
  It is one compositor pass over one layer.
- Filtering the **GL canvas** added **~10ms** under software rasterisation.

So `#glC` is graded **in the fragment shaders** instead — a handful of ALU ops
per fragment, no compositor pass — using the same numbers in the same order
(brightness, contrast, saturate). It lands within noise of the CSS result:
runner lake saturation 0.409 in-shader against 0.408 via CSS. `#fxC` keeps the
CSS filter, where it is free.

A phone GPU is where this has to hold, and a per-fragment multiply-add cannot be
the thing that breaks it.

## Result

| frame | saturation | black point | pixels > 200 |
|---|---|---|---|
| RPG meadow | 0.316 → **0.573** | 39 → **18** | 3.8% → 1.8% |
| RPG lake | 0.404 → **0.615** | 52 → **35** | 3.3% → 3.1% |
| Runner lake | 0.268 → **0.409** | 68 → **46** | 25.5% → **11.3%** |
| Runner Sky Gardens | 0.183 → **0.336** | — | **84.6% → 14.5%** |

No black or white clipping introduced. All nine runner stages compile and run
with zero page errors.

## Tuning

`--grade` in the CSS block (2D) and `GRADE` in the GLSL (runner) — **keep the two
in step or the hero will not match the world she is standing in.** Then
`LOOK[].fog` and `LOOK[].tint` per stage.

If it ever wants to go further, the honest next step is grading the plates
offline rather than raising these numbers: contrast past ~1.3 starts clipping the
Sky Gardens' clouds, and that is detail you cannot get back.
