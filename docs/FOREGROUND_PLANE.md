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

## ❌ Retired on card stages; un-retiring it was TRIED and REVERTED (2026-09-15)

**Outcome first, so nobody repeats it:** switching this plane back on for the six
carded stages shipped a **worse** bug than the one it fixed, and was reverted the
same day. Client: *"as I move, big black gaps… you didn't test that."* He was
right — it was checked as stills and one straight walk in portrait, never driven.

**What it actually looks like in motion.** `FORE[]`'s slim verticals (`tr:1`) are
dark near-silhouettes by design, and they move at ~35× the plate rate. On a stage
that has never had them they do not read as trunks passing the camera; they read
as **big black bars sweeping across the frame.** Measured after the fact, over 26
camera positions per stage, as the fraction of the backdrop band below luma 24:

| | stages 1, 2, 3, 4, 6, 8 |
|---|---|
| before | 0.35 – 1.09% |
| with the plane on | **3.17 – 8.01%** |

**The rule this leaves behind: `tr:1` on a stage is a combat-readability
decision, not a depth decision.** Never switch this plane on for a stage without
driving that stage and measuring dark coverage — in **both** orientations.

The reasoning below was not wrong about the cards. It was wrong that being right
about the cards was sufficient.

### The original retirement, and the measurement that questioned it

**This doc described a plane that was switched off on six of the nine stages, and
did not say so.** When the multiplane cut landed, `drawForeground` gained an
early `if(CARD_READY[ai])return;` on the reasoning that *"the cards ARE the near
planes and this would be a second, contradictory depth system."* Stages 1, 2, 3,
4, 6 and 8 — every stage that got a real cut — silently lost their near plane.

**The premise was wrong, and measuring the cards is what shows it.** The whole
card set on Mirror Lake spans **0.036 to 0.053** screen px per world px: every
card within ±19% of the plate's own rate, a **1.22× near-to-far ratio** at the
shipped spread of 0.010. That is one slab moving at slightly
different speeds. There is no near plane anywhere in it.

`drawForeground` runs at `cam*ZOOM*1.7` ≈ **1.56 px per world px — about 35× the
plate rate.** It cannot be a second, contradictory depth system, because at that
distance there was never a first one. It is the only near plane in the scene, and
the carded stages were precisely the six that had given theirs up. **That analysis still stands** — the cards really are not near planes. It simply
was not the whole question, and the answer to "is there a near plane here?" turned
out not to settle "should this one be switched on?". The plane stays OFF on
stages 1, 2, 3, 4, 6 and 8.

## Scope and cost

RPG only — the runner is 3D and returns early. **No new assets.** Median frame
time unchanged at 16.7/16.8ms, still vsync-locked.

## Where this stops

This is the last big depth win available from flat paintings. Genuine *spaces* —
real angles, cast shadows, correct occlusion — need the paintings re-rendered as
**separated depth layers out of Blender**, which is the next step and is blocked
only on render time on the laptop. See the Blender layer plan.
