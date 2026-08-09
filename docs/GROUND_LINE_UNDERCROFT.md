# GROUND LINE + UNDERCROFT — ✅ SHIPPED (`dabe9e2`)

**Client, 2026-08-09:** *"Let's discuss the height of the ground that she's
walking on. It should be more mid-level… her body and stuff should be right
along the same level as the title is of each stage. She's too far at the bottom,
it's not like Mario — Mario is kind of like center screen. Can we adjust that,
and let's discuss what's gonna be beneath, you know, underneath all of that."*

**These are one task, not two.** Raising the floor is precisely what exposes the
space under it: 18% of the screen became 28%. Whatever fills that space had to
ship with the framing change or the framing change would read as a bug.

Scope: **ACTION RPG only.** Royal Runner is untouched.

---

## 1 — The framing

### What was controlling it

The ground surface was pinned at **82% of the viewport** — as a hard-coded
`0.82` in **three independent places**:

| site | what it did |
|---|---|
| camera, portrait branch | `GS.camY += ((FLOOR_R*T - VH*0.82) - GS.camY)*0.14` |
| camera, landscape clamp | `_cyMax = min(GS.LH*T-VH, FLOOR_R*T - VH*0.82)` |
| `drawMansionBG` | `var floorY = H*0.82` |

They agreed **by coincidence, not by construction** — the third is a raw screen
fraction that doesn't track the camera at all. It only ever landed on the tiles
because the camera happened to use the same number.

### What shipped

- **One constant, `GROUNDF = 0.72`**, read by both camera branches.
- **`floorY` now derives from `groundY`** (the true scaled world floor), so the
  painted earth band cannot tear away from the tiles at *any* anchor, in *any*
  orientation. The third hard-coded fraction is gone.

Measured on a 390×844 phone:

| | before (0.82) | after (0.72) |
|---|---|---|
| ground line | 75% | 72% |
| her head | 69% | 63% |
| space below floor | 18% | 28% |

Reference points: Mario 1-1 ground ≈72–75%; Hollow Knight ≈70%.

### The landscape discovery

At `LH=18` the landscape camera clamps to the **world's own bottom edge**, not
to the anchor — so it sat at **0.744 and could not go higher**. Measured proof:
identical `camY` of 76 at both 0.72 and 0.65.

**`LH` 18 → 20** gives the camera two more rows to look at, and landscape now
reaches 0.72 (`camY` 87 → ground at 0.722·H). Deeper pits are a welcome side
effect. Everything keyed off `LH` was re-checked: the death plane
(`p.y > LH*T+150`, now 790), foe cleanup, the map overview scale, `groundCol`,
and the parked `buildLevel` (kept in step).

### `SLAB_R` — drawn depth vs collision depth

Tiles are opaque, so the six new ground rows simply **buried the undercroft they
were added to expose.** `SLAB_R = 2` caps how many rows are *drawn*; collision
is completely untouched (the tiles still exist in `GS.solid`, `pit()` still
carves them). The deepest drawn row gets a **cut face** — `isBtm` is false there,
so the platform front-face branch never fires and the column would otherwise stop
dead in mid-air.

Why 2 and not 3: measured, the touch cluster starts at **y=672** and the ground
line lands at **608**, so the band the player can actually see is ~64px. A 3-row
slab (56px) left 8px of it.

---

## 2 — The undercroft

`drawUndercroft` + `drawUCLayer`. Shared substrate (stage-tinted gradient,
sagging strata, embedded grit) plus **one themed layer per stage**, parallaxed at
0.6–0.9× the ground so it recedes behind her instead of competing.

| stage | beneath |
|---|---|
| 0 · ONCE UPON A PAGE | the library's lower stacks — shelf ends, reading-lamp pools |
| 1 · FIRST LIGHT MEADOW | topsoil, root threads, a buried drystone wall |
| 2 · THE PETAL MILE | cobble bed with petals settled into it |
| 3 · THE ROSE WALTZ | the fountain's cistern — arches over still water |
| 4 · THE MIRROR LAKE | **under the water** — light shafts, caustics, swan shadows from below, bubbles |
| 5 · THE WISHING GLADE | mycelium threads and the glade's lights, underground |
| 6 · THE GOLDEN HOUR | sunflower taproots in warm soil |
| 7 · THE SKY GARDENS | **nothing.** Open sky and cloud decks far below — the vertigo is the stage |
| 8 · HER ENCORE | palace foundations, piers, a lit undercroft window |

### Rules this layer follows

- **It is not decoration.** Pits drop her through this band before the death
  plane, so it must read at speed and stay darker than she is.
- **Layers lay out against 0.66 of the band**, not the full height. Detail placed
  at mid-band lands behind the D-pad and is drawn for nobody.
- **Scatter is deterministic** (`_uh`, a sin-hash). `Math.random()` here would
  strobe at 60fps.
- **Positive modulo** (`_uw`). The parallax offset is negative and a raw `%`
  keeps the sign, which sends every wrapped element off-screen left forever.
- **Tiling period is `n*sp`** where `n = ceil(W/sp)+2`, so the wrap lands on an
  exact multiple of the spacing — otherwise a seam scrolls across, exactly the
  way the backdrop tiles used to.
- **`amb` is 0 under reduce-motion.** Every animated term is multiplied by it, so
  the band goes *still* rather than disappearing.

---

## 3 — Two bugs found on the way

**The "abyss below the track" gradient was dead code.** Its `gy2` was
`GS.LH*T - GS.camY` — **world units compared against screen `H`** after
`FX.restore()`. On a portrait phone that's 1167 vs 844, so the test never passed
and nothing ever drew. This is the **sixth instance** of the project's recurring
bug class: *a quantity that should scale with the world pinned to (or compared
against) a raw screen dimension.* It was **deleted rather than repaired** —
`drawUndercroft` owns that band alone now, and two owners of the same band is how
they drifted apart to begin with.

**`drawLyric` was another fixed `H-92`.** At 0.82 it sat on bare wash; at 0.72 it
landed across the tile band and her feet. Reseated into the gap between the slab
and the controls, with `maxWidth` so long lines condense instead of running under
the action buttons. **Side mode only** — `drawLyric` is shared with ROYAL RUNNER,
which has no world floor and no `camY`; the runner keeps `H-92` exactly as it was.

---

## Verification

- Inline-script syntax clean (`node --check` on extracted `<script>` blocks).
- **All 9 stages rendered in portrait AND landscape, zero page errors.**
- Landscape reaches 0.72 (`camY` 87) where it was pinned at 0.744.
- Death plane fires at `LH*T+150` = 790, undercroft rendering during the fall.
- Boss arena anchor holds (`camY` -591 during a live boss encounter).
- Reduce-motion renders still — `body.rm` true, no errors.
- Royal Runner unchanged.
- `tools/glyph_gate.py` clean; `web/` references still exactly match disk.

## Tuning knobs

`GROUNDF` (0.72) · `SLAB_R` (2) · the `bh*0.66` content window · `UCROFT[]`
palettes. All named constants near the top of the game state block — a play-test
pass can move any of them without touching layout code.
