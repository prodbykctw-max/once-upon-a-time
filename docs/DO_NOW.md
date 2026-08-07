# DO NOW — prioritized, 2026-07-26

Client is on a dying laptop battery. **Work top to bottom.** Ordered by impact ÷
effort, so if you only get through item 1 and 2 the game is materially better.

Line numbers are against `index.html` at commit `728c46c`. Everything below is
already root-caused — no investigation needed.

---

## 1. ✅ DONE (`24049d4`) — décor detaches from the floor on jump
> **Fixed & deployed.** Verified in code: `var groundY=(FLOOR_R*T-(GS.camY||0))*_wz;`
> — the clamp is gone and the baseline tracks the world floor exactly.

<details><summary>original report</summary>


**Line 3596:**
```js
var groundY=Math.min(floorY,(FLOOR_R*T-(GS.camY||0))*_wz);
```
→
```js
var groundY=(FLOOR_R*T-(GS.camY||0))*_wz;
```

**Why:** `floorY = H*0.82` is a **fixed screen row** that doesn't move with the
camera. In landscape the at-rest value is 349 against a clamp of 353 — **4px of
headroom** — so any jump pins `groundY` and the props stop tracking the stage
floor. Portrait's clamp is ~475px away, which is why it only shows sideways.

The `*_wz` you added is correct; the clamp in front of it is what's left of the
bug. Client: *"locked to the background floor, but not the stage floor."*

If the backdrop image needs a bound so it can't fly off, clamp **that draw rect
only** — the décor baseline must be unclamped. Props are world objects.

**Verify:** jump on `?stage=0` in landscape, watch a candelabra base — welded to
the floor for the whole arc.

---

</details>

## 2. ✅ DONE (`24049d4`) — PRODBYKCTW footer covered THE BOUTIQUE in portrait
> **Fixed & deployed**, and better than specced: rather than hiding it, the
> footer is now `position:static; margin-top:auto; flex:0 0 auto` so it *flows*
> with the content and can't overlap in either orientation.

<details><summary>original report</summary>


**Line 340** is `.site-footer{display:none}` — but it's inside the
`@media (orientation:landscape) and (max-height:560px)` block at **line 329**, so
it only applies sideways. In **portrait** the footer is still
`position:absolute; bottom:12px; z-index:6` and lands on top of the THE BOUTIQUE
button on the how-to screen.

**Fix:** the collision is caused by *content height*, not orientation. Either let
the footer flow with the scroll content on `#howToScreen` (already
`overflow-y:auto`), or hide it on short viewports regardless of orientation.
Portrait is the primary orientation — this is the more important half.

---

</details>

## 3. ✅ DONE — GLYPH SWEEP COMPLETE (0 sites remain)
> Laptop cleared 38 (`adf3533`), cloud cleared the final 9+1: drawn eighth-note
> helper replaces every font `♪♫` (runner coins + death bloom), map legend uses
> drawn dots/squares, shop+atlas pips are CSS boxes, stage-select tick is a CSS
> drawn check, CONTINUE says GEMS, mode stats say NOTES. **index.html now ships
> zero stock glyphs.** Playwright 6/6.

<details><summary>original (was 47 sites)</summary>


Full list with line numbers and replacements: **`docs/GLYPH_SWEEP.md`**.
You already cleared the `▶` on PROCEED (thank you) — **47 sites remain**:
15 in the HTML/CSS block (<line 1000), 32 in the JS block.

**Client caught these live and named it: "Apple glyph button."** On device iOS
substitutes its own emoji font — `✦` renders as a yellow emoji sparkle, trophy
bullets render blue. Screenshot: `docs/refs/stage-clear-live-glyphs.jpg`.

**These cannot be judged from source** — in the editor they look like ordinary
text characters. That's why they regressed twice.

Fastest path:
1. **~Half are pure decoration → just delete** (`✦ QUEEN'S REGISTRY ✦` →
   `QUEEN'S REGISTRY`). No layout change.
2. **Most of the rest → plain words** (`⚙ SETTINGS` → `SETTINGS`).
3. **Only ~6 need a drawn primitive** (shop pips, cleared tick, cache beacon, map
   legend). `arc()` is fine — **a shape you draw is a made asset.** Do NOT
   re-embed an icon atlas.
4. The canvas `♪` at line ~2865 should reuse the Grace Note sprite already in
   `TEX.items` instead of a font character.

---

</details>

## 4. ✅ DONE (laptop, tally commit) — overlay actions always reachable
> `.ov-btns` is `position:sticky;bottom:0` with a fade gradient — TOTAL and
> PROCEED are reachable without scrolling on short viewports. Verified in test.

<details><summary>original report</summary>


In the client's STAGE CLEAR shot, `OBJECTIVES · ×1.0 MULTIPLIER` is cut off
**mid-heading** and its rows never render — the scroll region ends before the
content does. The new scored tally is **taller**, so this got worse, not better.

Make sure on a short viewport the **TOTAL row and the PROCEED button are
reachable without scrolling** (sticky footer inside `#overlay`, or tighter
vertical rhythm under the landscape query).

---

## 5. ✅ DONE (`24049d4`) — par times
> Adopted the derived table `STAGE_PAR=[70,70,80,90,95,100,105,115,120]` and
> added `PAR_DIFF` difficulty scaling. Verified in code. **Still needs one
> real play-test pass to confirm the values feel right** — that part is the
> client's call, not code.

<details><summary>original note</summary>


You shipped `STAGE_PAR=[150,160,165,170,180,185,190,200,215]`. The derived table
in `docs/STAGE_CLEAR_TALLY.md` is `[70,70,80,90,95,100,105,115,120]` — computed
from `stageEnd=330`, `T=32`, run `6.4px/frame`, boss HP `7+ai*2`. **Yours are
~2× that.** Not wrong — but if stages routinely finish far under par, the TIME
row stops meaning anything.

Also note **par must scale with the difficulty setting** (`PAR_DIFF` in that
doc). Boss HP already scales ×1.4 on Hard, so on a Normal clock **Hard players
can never beat par.**

---

</details>

</details>

## Then: ✅ DONE — the guard is live
> `tools/glyph_gate.py`, called from `deploy.sh` before staging: strips comments,
> then **fails the deploy** on any arrow/geometric/symbol/dingbat/emoji character
> in shipped code. Typography (é É — – ‘ ’ “ ” … · × ° ≈ ±) stays allowed.
> Tested both directions: current build passes; a planted `✦` blocks the deploy.

<details><summary>original spec</summary>


Add a pre-deploy gate in `tools/deploy.sh` that **fails the deploy** on non-ASCII
outside comments, allow-listing real accents (`é È à ç ü ö ñ`), typographic
punctuation (`— – ‘ ’ “ ” … ·`), `×`, `°`, and `═ ─` (comment box-drawing).

The no-stock-glyph rule has now regressed twice because nothing enforces it.
Sweeping without the gate just resets the clock.

---

</details>

## Reference docs (don't read unless you need detail)
- `docs/LANDSCAPE_FIX_BRIEF.md` — all landscape issues + the #0 reopen with numbers
- `docs/GLYPH_SWEEP.md` — every glyph site, line-by-line
- `docs/STAGE_CLEAR_TALLY.md` — tally spec + par derivation + scoring formulas

---

## 6. ⚠️ AFTER EVERY ITEM — UPDATE THE DOCS (client directive, binding)

**Client, 2026-07-26:** *"After all commitments are done, update all
documentation… every time y'all complete some shit update all documentation so
everything is accurate and up-to-date and factual."*

This is now a **standing rule, not a one-off**. As each item above lands:

1. **Mark it done where it's specced** — tick it off in `DO_NOW.md`,
   `GLYPH_SWEEP.md`, `LANDSCAPE_FIX_BRIEF.md` or `STAGE_CLEAR_TALLY.md`. Cite the
   commit hash. Don't leave a finished thing labelled ACTIVE/OPEN.
2. **Update `HANDOFF.md`** — move it out of the ACTIVE banners.
3. **Update `DEVELOPMENT_RECORD.md`** — it is the canonical history; add what
   shipped and close the matching Open Thread.
4. **Update `CLAUDE.md`** if the change alters architecture, a workflow, or a
   guardrail.

**Why this is worth the two minutes:** on 2026-07-25/26 an audit found `CLAUDE.md`
still telling every new session the project was Phaser 3 and to "not hand-roll a
render loop" (it ships a hand-rolled loop), `HANDOFF.md` teaching a `git add -A`
deploy recipe that had already leaked the client's real photos, and six finished
tasks still marked ACTIVE — including two that got re-reported as open **because
the docs said they were.** Stale docs actively cost this project rework.

**Rule of thumb: a task isn't done when the code works — it's done when the code
works and the docs say so.**
