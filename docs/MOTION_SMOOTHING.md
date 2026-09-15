# MOTION SMOOTHING — ✅ SHIPPED

**Client:** *"Can we work on smoothing to make sure everybody moves smoothly? It
does seem a bit jerky and dry, like it's not naturally smooth — the character
motions, the jumps and the movements."* Then, narrowing it: *"I'm mainly only
talking about the character movement being jerky."*

## Four candidates, measured before changing anything

"Jerky" has several possible causes and they need different fixes, so each was
measured against a real held-key run rather than guessed at.

| candidate | measured | verdict |
|---|---|---|
| Draw position rounded to whole pixels | `drawHero` uses `p.x+PW/2-drawW/2`, world transform is `scale(ZOOM);translate(-camX,-camY)` — **no rounding anywhere** | not the cause |
| Run cadence vs ground speed (foot-slide) | stride cycle 32 frames × 6.4px = **203 world px**, hero `PH=86` → **2.36 body-heights per cycle** | correct for a run — **left alone** |
| Jump animation rate | 6 poses over 44 frames of airtime, held 7 frames each | real, but **art-limited** — see below |
| **Fixed timestep with no render interpolation** | **6.6% of displayed frames moved her 0px, 7.5% moved her double** | **the cause — fixed** |

## The cause

`loop()` advances physics in whole 16.6ms steps and then drew the **raw
post-step pose**. Everything on screen therefore moved in 60Hz staircases no
matter what the display was doing:

* On a **120Hz phone** every position is shown for two frames — by
  construction, not by accident.
* Any frame the device runs long banks two steps and the next drawn frame jumps
  **double** the distance.

Measured on a real run at a true 60Hz, only **86% of displayed frames were a
clean step**; 6.6% were frozen and 7.5% were doubles — roughly eight hitches a
second.

## The fix

Physics still advance in whole 16.6ms steps — **the fixed timestep is correct
and is not what changed.** What changed is that `draw()` now places everything
*between* the last two steps:

```
_alpha = _acc / 16.6            // fraction of a step already banked
drawn  = prev + (cur - prev) * _alpha
```

`update()` snapshots the pre-step pose (after every early return, so a paused or
hitstopped frame never records a phantom step). `loop()` computes `_alpha`,
calls `_lerpIn()`, draws, and restores in a `finally`.

**Interpolated:** camera, Jandé, foes, boss. **Not** particles (short-lived and
chaotic — no staircase to see) and **not** the runner, which is a separate
renderer.

**`_lerpOut` restores the exact saved numbers, never a recomputed lerp.**
Physics must not inherit a rounding error from a rendering convenience.

**`LERP_SNAP=64`** — a move larger than this is a teleport (respawn, stage
change), and is snapped rather than smeared across the screen for a frame.

## Results

Frozen frames, same run, on a display not locked to the step:

| | frozen frames |
|---|---|
| physics pose (what used to be drawn) | **22.9%** |
| drawn pose (after the fix) | **6.6%** |

On a display that *is* exactly 60Hz the interpolation is correctly a no-op —
there is nothing between steps to interpolate.

**Physics proven unaffected**, which is the real risk with this technique: same
input, distance per physics tick is 2.4256 / 2.4256 / 2.4381 before and
2.4256 / 2.4256 / 2.4381 after. All nine stages drive clean, jumps land, zero
page errors.

`GS._drawX/_drawY/_drawA` hold the pose actually handed to `draw()`, so this
stays measurable. **Sampling `GS.p.x` proves nothing** — that is the physics
pose and it is *supposed* to remain a 60Hz staircase.

## What this does NOT fix

**The jump animation is 8.6 fps and that is an art limit, not a code one.**
Airtime is 44 frames (0.73s); the jump sheet has **6 frames**, held 7 frames
each, so the six poses already map correctly onto the arc (crouch → rise → apex
→ fall → land). Playing them faster would finish the animation early and hold
the landing pose in mid-air — worse, not smoother. The jump *arc* is now smooth;
the *pose* cadence needs more drawn frames, which means an AutoSprite pass and
is blocked on `$AUTOSPRITE_KEY`.

For reference, `spd` is game-frames-per-animation-frame, so smaller is faster:

| anim | spd | fps | frames |
|---|---|---|---|
| attack | 2 | 30 | 8 |
| belt · downstrike | 3 | 20 | 5 · 4 |
| run · dash | 4 | 15 | 8 · 5 |
| dance | 6 | 10 | 6 |
| idle | 9 | 6.7 | 6 |
| **jump** | **7** | **8.6** | **6** |

## Open — a feel knob, not a bug

"Dry" may also be pointing at the **acceleration curve**, which is deliberately
snappy: `p.vx += (tgt-p.vx)*0.5` reaches 94% of top speed in four frames, and
`if(tgt===0&&onGround&&|vx|<0.6) vx=0` kills the residual glide outright. The
code says this was tightened *from* 0.3 on purpose — *"tight: snap to speed,
snap to stop (was 0.3 = slidey)"*. Loosening it would read as more natural and
less responsive, and that trade is the client's call, not a defect. **Not
changed.**
