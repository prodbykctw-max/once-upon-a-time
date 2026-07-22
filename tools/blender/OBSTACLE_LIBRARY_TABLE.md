# Handoff — Library runner obstacle → reading table

**For the laptop / Blender session.** The cloud session has no Blender (`bpy`)
and can't match the render quality, so this is a spec, not a code change.

## Problem
In ROYAL RUNNER, the library stage's **full-blocker** obstacle reads as a
"random wooden board with book-spines on top and horizontal lines." It's the
`wall` obstacle, cell 0. In-engine it flattens (the camera + fill light wash out
the bookcase depth), so it doesn't say "library object" — it says "abstract
hurdle." The client wants it to be a clear **library reading table**.

(The other two library obstacles are fine and should stay:
`low_0` = stacked books on a plinth you jump; `gate_0` = the draped table you
slide under. Only `wall_0` needs the re-theme.)

## Where
`tools/blender/obstacles3d.py` → `def wall(i)` → the `if i == 0:` branch
(currently the bookcase: a big cube + 4 shelves + 44 book-spine cubes).
Replace that branch's body with a reading table built from the SAME helpers the
file already defines: `cube(center, size, mat, rot=)`, `cyl(center, r, h, mat,
verts=)`, `wood_mat(name,(r,g,b),rough=,grain_scale=)`, `fabric_mat(...)`,
`MARB()`, `rose(x,y,z)`. Keep it a FULL-height blocker (fills the lane) — the
gameplay is "switch lanes to dodge," so the silhouette must occupy the cell
(~2.0 wide, reach ~1.2–1.5 tall). A short café table would be too low to read as
a blocker; make it a tall library study table with objects stacked on top.

## Starting point (adapt to the real framework)
```python
def wall(i):
    if i == 0:      # library: long reading table (full-lane blocker)
        wood = wood_mat('Tbl', (0.33, 0.19, 0.09), rough=0.5)
        legm = wood_mat('Leg', (0.28, 0.16, 0.08), rough=0.55)
        cube((0, 0, 1.02), (2.02, 0.62, 0.12), wood)                       # thick tabletop slab
        cube((0, 0, 0.93), (1.9, 0.5, 0.10), legm)                         # apron under the top
        for lx in (-0.86, 0.86):                                           # four turned legs
            for ly in (-0.22, 0.22):
                cyl((lx, ly, 0.46), 0.055, 0.92, legm, verts=12)
        cube((0, 0, 1.10), (1.4, 0.44, 0.02),                              # green baize runner
             fabric_mat('Baize', (0.10, 0.30, 0.17), rough=0.85))
        cols = [(0.5,0.10,0.12), (0.12,0.24,0.44), (0.32,0.26,0.10)]       # a book stack on top
        for k in range(3):
            cube((-0.5, 0.02, 1.15 + k*0.055), (0.34, 0.24, 0.05),
                 fabric_mat(f'Bk{k}', cols[k], rough=0.55),
                 rot=(0, 0, random.uniform(-0.05, 0.05)))
        cyl((0.55, 0, 1.20), 0.03, 0.18, MARB(), verts=10)                 # brass candlestick
        cube((0.55, 0, 1.31), (0.05, 0.05, 0.06),
             fabric_mat('Flame', (1.0, 0.8, 0.3), rough=0.3))
        # optional: an open book leaning up, a quill, a small globe — echoes the
        # shoulder décor so the table reads unmistakably "library."
```
Tune sizes so the content fills the 256×224 frame (the embed step bottom-anchors
+ crops to bbox, so leave a little headroom but don't render it tiny).

## Render + ship (existing pipeline, no game-code change)
1. Open `obstacles3d.py` in Blender and run it (it renders all kinds × 9 stages
   to `assets/renders/obstacles/{kind}_{i}.png`). To iterate on just this one,
   render `wall_0.png`.
2. From the repo root: `python tools/embed_obstacles.py` — it repacks the
   `low/gate/wall` sheets to WebP and rewrites the `oblow/obgate/obwall`
   data-URIs in `index.html` (idempotent; drops the old keys first).
3. Commit `index.html` (+ the new `assets/renders/obstacles/wall_0.png`) and
   deploy. The game already themes obstacle sprites per stage from cell `i`
   (`GameScene` draws `ai*256` from each sheet), so nothing else changes.

## Verify
Play ROYAL RUNNER, library stage: the full-blocker should now clearly read as a
reading table with books/candlestick, not an abstract board — while still
occupying the lane as a dodge-by-lane-switch blocker.
