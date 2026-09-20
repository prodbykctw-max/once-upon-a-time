# ART REFERENCES — what the client has sent, and what it actually shows

Reference clips the client sends, read against our own rendered frames. Each
entry records what was **measured**, not what it looked like — twice now the
eyeball read and the measurement disagreed.

---

## 1. UNSTRUNG MACHINE (sent 2026-09-20)

`instagram.com/reel/DcjbjtsxHCK` — `@cloudedstudioindie`. *"One of the first
outdoor areas I'm currently building for Unstrung Machine… a 2D
action-exploration Metroidvania set in a post-apocalyptic world inhabited by
conscious machines."* Steam app 3940770.

> **Getting at it:** the share link is login-walled and WebFetch 429s. The
> public **oEmbed endpoint** (`/api/v1/oembed/?url=…`) returns the full caption,
> the author and a **640×640 thumbnail** with no auth. That is the route for any
> future Instagram reference.

### What it is

A side-scroller frame: a small character running left-to-right along a stone
balustrade, past columns, under a hanging **"OAKRAVEN HOSPITAL"** sign, with
vines, leaves and a raven overhanging the top of the frame.

### Measured against our meadow, world only (HUD and undercroft excluded)

| | Unstrung Machine | Jandé — meadow |
|---|---|---|
| luma p5 | 42 | **43** |
| luma p95 | 132 | 176 |
| tonal range | 90 | **133** |
| mean saturation | 52 | **126** |
| near/far saturation falloff | 1.15× | **1.80×** |

**Three of my own assumptions were wrong, and the numbers say so:**

1. **We are not washed out at the bottom end.** Both frames sit at the same
   black floor (p5 42 vs 43).
2. **We have MORE aerial perspective, not less.** Our far hills desaturate to
   94.5 against near ground at 170.5 — a **1.80×** falloff. Theirs is nearly
   flat at **1.15×**. The depth cue we kept trying to add to the backdrop is
   already there and already stronger than the reference.
3. **Their look is LOW chroma and a COMPRESSED range** (sat 52, range 90) — a
   muted overcast palette. Ours is a bright saturated storybook by design.

> ⚠ **Do not "fix" our palette toward this reference.** Matching sat 52 would
> directly reverse a delivered client directive — *"the colours aren't rich like
> pixel art colour is rich"* — which is why `GRADE` carries saturate **1.34**.
> See `docs/COLOUR_GRADE.md`.

### What IS transferable — and it is one thing

**The foreground plane.** Their frame has vines, leaves, a raven and a hanging
sign in near-silhouette across the top and left edges. Ours has **nothing** in
front of the character. That single difference accounts for most of the
"standing inside a space" feel, and it is not a palette or a parallax problem.

**This is the feature that was enabled and reverted on 09-15**, and the
reference explains exactly why theirs reads and ours did not:

| | Unstrung Machine | our reverted attempt |
|---|---|---|
| shape | recognisable organic forms — leaves, a branch, a bird | abstract dark **vertical bars** |
| placement | hangs from the **top and corner edges**, clear through the middle | swept **through the middle of the play area** |
| result | frames the shot | read as *"big black gaps"* |

Same concept, opposite execution. If the near plane is ever revisited, the
reference says: **shaped foliage clinging to the frame edges, nothing crossing
the lane she fights in.** See `docs/FOREGROUND_PLANE.md`, which already carries
the measured failure.

### Two smaller observations

* **Diegetic signage.** "OAKRAVEN HOSPITAL" is a named place painted into the
  world. None of our nine stages carry in-world signage, and the stage names
  exist only in the HUD.
* **Framing is comparable.** Their character occupies a similar fraction of the
  frame to Jandé (eyeballed, not measured). This reference does **not** support
  Frédéric's *"widen line of sight"* note — if anything it matches what we ship.
