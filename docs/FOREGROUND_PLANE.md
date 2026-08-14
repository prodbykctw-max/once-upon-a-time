# FOREGROUND PLANE — ✅ SHIPPED (`43a124e`)

**Client, on the library:** *"It is the fact that I have those candlesticks there
that kind of gives it a different layer for it to move behind, and that's nice."*
**And:** *"I want all of the backgrounds to be spaces, to feel like being in a
space and not just a flat picture."* Plus: steal the parallax technique from the
game he is building.

## The diagnosis is in his own first quote

Every plane in this game sat **behind** her — the painted backdrop, the near
band, the undercroft. A stack of behind-planes still reads as scenery.

Parallax sells depth by also putting something **in front** of the subject,
moving **faster** than the world. The library felt different for exactly one
reason: its candlesticks are world props she walks *behind*. Nothing else in the
game had a near plane at all.

## What shipped

`drawForeground()` — a per-stage near plane at **~1.7× the world's own screen
rate**, drawn **after** the world transform is restored so it genuinely occludes
the hero.

**Top fringe.** Willow strands, cherry limbs with blossom, ivy, sunflower heads
leaning in over the edge, a library soffit with hung lamps. It hangs deeper at
the screen edges and thins through the middle — which is both how a real canopy
frames a view and how the play area stays legible. It takes the wind harder than
anything behind it, because it is closer.

**Slim verticals.** A trunk sweeping between the camera and the player. The
strongest depth cue available, and the riskiest, so it is bounded at both ends.

| stage | fringe | trunks |
|---|---|---|
| 0 library | soffit + hung lamps | **none** — indoors |
| 1 meadow · 3 rose waltz · 8 encore | leafy limb | yes |
| 2 petal mile | limb + blossom clusters | yes |
| 4 mirror lake · 5 glade | trailing strands | yes |
| 6 golden hour | heads leaning in | yes |
| 7 sky gardens | ivy | **none** — open air |

## Three things the first attempt got wrong

All three were invisible in the code and obvious the moment it rendered.

1. **The trunk ran `0..H`** as a wide soft gradient — a vertical haze band
   straight through the lake *and* the undercroft. It read as a rendering fault,
   not a tree. **A trunk stops at the ground**; it now ends at the floor line.
2. **A tinted gradient with parallel sides is a light shaft, not a trunk.**
   Anything this close to camera is near-silhouette and is never a rectangle. It
   now tapers, leans, carries a limb, and is drawn in two passes for a feathered
   edge.
3. **Alpha is 0.62, deliberately not opaque.** This strip crosses the *play*
   area, so a foe or projectile behind it must stay readable. Depth is not worth
   a death.

## Scope and cost

RPG only — the runner is 3D and returns early. **No new assets.** Median frame
time unchanged at 16.7/16.8ms, still vsync-locked.

## Where this stops

This is the last big depth win available from flat paintings. Genuine *spaces* —
real angles, cast shadows, correct occlusion — need the paintings re-rendered as
**separated depth layers out of Blender**, which is the next step and is blocked
only on render time on the laptop. See the Blender layer plan.
