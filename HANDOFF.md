# HANDOFF v2 — Jandé: Once Upon A Time (3D era)

> ## ▶ START HERE: `docs/DO_NOW.md`
> ✅ **FIXED 07-26 — pre-game screens: `docs/PREGAME_LAYOUT_BUGS.md`.** Content is
> pinned to the top (the footer's `margin-top:auto` cancels `justify-content:
> center`), the wordmark is sized off WIDTH so it eats 33% of a landscape
> screen, and **title/login/mode-select have no `overflow-y` while `body` is
> `overflow:hidden` — so in landscape BEGIN is unreachable and the game cannot
> be started.** Blocker.
> **And when you finish anything: update the docs in the same session** —
> tick the spec, clear the ACTIVE banner here, record it in
> `DEVELOPMENT_RECORD.md`. Client directive, binding. See DO_NOW item 6.
> One prioritized list, ordered by impact ÷ effort. Items 1 and 2 are
> **one-line fixes** (décor detaching on jump; the PRODBYKCTW footer covering
> THE BOUTIQUE in portrait). Item 3 is the 47-site glyph sweep. Everything is
> already root-caused with line numbers — no investigation needed.

> ✅ **DONE 07-26 — boss music: `docs/BOSS_MUSIC.md`.** Client wants darker,
> dynamic score during RPG boss fights. The mechanism already exists in
> `musTick` but its `danger` flag is wired ONLY to the runner's chaser, so RPG
> bosses get no musical change at all. One-line quick win, then drive it from
> the existing eased `GS.bossMood` so the score darkens on the same curve as
> the Shadow of the Groom visuals.

## 🎬 08-10 (cloud session) — ground line raised AGAIN to 0.65
> ✅ **DONE — `32b280f`. Client: "Higher."** Spec updated: `docs/GROUND_LINE_UNDERCROFT.md`.
- **`GROUNDF` 0.72 → 0.65, `LH` 20 → 22.** Her head sits at 56%, ground at 65%.
- **The Mario number, settled.** SMB1's ground is at 86.7% *of the NES frame* —
  the figure everyone quotes, and the wrong one for a phone. Letterboxed 4:3 into
  19.5:9, the ground lands at **66% of the physical screen**, head at 63%. 0.82
  and 0.72 were both below Mario-on-a-phone; **0.65 is it.**
- **Landscape had NEVER honoured `GROUNDF`.** The branch eased toward
  `p.y - VH*0.55` and used `GROUNDF` only as a *ceiling*, so while she's grounded
  the follow target won. Proof: 0.72 → 0.65 left `camY` at 87 in both. Now
  **anchor first, follow second** — the follow term only pulls the camera UP when
  she climbs. `camY` 87 → 123 = ground at exactly 0.650.
- **⚠️ `LH` IS DERIVED FROM `GROUNDF`: `LH*T >= FLOOR_R*T / GROUNDF`.** Lowering
  `GROUNDF` again **requires** raising `LH` or landscape silently pins to the
  world's bottom edge (which is what it did at 18). Derivation is in the code.
- **`CTRL_TOP` replaces the guessed `0.66`-of-the-band fudge.** `#mCtrl` sits on
  `env(safe-area-inset-bottom)` — it cannot be derived from `H`, so it is now
  MEASURED (on resize, and again on the start-of-run toggle where the pads
  actually get `.on`). Consumed by the undercroft's content window and the lyric.

## 🎬 08-09 (cloud session) — ground line raised + undercroft built
> ✅ **DONE — spec: `docs/GROUND_LINE_UNDERCROFT.md` (`dabe9e2`). RPG only.**
- **`GROUNDF=0.72`** replaces three independent hard-coded `0.82`s (both camera
  branches + `drawMansionBG`'s `floorY`). They agreed by coincidence, not by
  construction. **`floorY` now derives from `groundY`** — the earth band can
  never tear away from the tiles again at any anchor.
  **Never re-introduce a literal ground fraction; read `GROUNDF`.**
- **`LH` 18 → 20.** At 18 the landscape camera clamped to the world's own bottom
  edge at **0.744** and raising the anchor below that did *nothing* there
  (measured: identical `camY` at 0.72 and 0.65). Both orientations now reach 0.72.
- **`SLAB_R=2`** caps how many ground rows are *DRAWN*; collision is untouched.
  Tiles are opaque, so without it the new rows buried the undercroft they were
  added to expose.
- **`drawUndercroft` / `drawUCLayer`** — shared substrate + one themed layer per
  stage (library stacks · meadow roots · petal cobble · rose cistern · **Mirror
  Lake seen from under the water** · glade mycelium · sunflower taproots · **Sky
  Gardens: no ground at all, open sky** · palace foundations). Parallaxed 0.6-0.9×.
  **It is play space, not decor** — pits drop her through it before the death plane.
- **Sixth screen-vs-world instance found and deleted:** the "abyss below the
  track" gradient compared WORLD units against screen `H` after `restore()` and
  therefore never drew at all. Removed rather than repaired — one owner per band.
- **`drawLyric` reseated** (was another fixed `H-92`, landed on her feet at 0.72).
  **SIDE MODE ONLY** — it is shared with ROYAL RUNNER, which is left as it was.

## 🌙 07-26 EVENING (cloud session) — décor scale, jelly UI, illustrated record
- **Runner décor scale fixed at the root** (fifth screen-vs-world instance): prop
  heights were a fixed 560px base vs the H-scaled hero — ~4x her height on a
  landscape phone. Now `H*0.601`-anchored (identical at the tuned portrait
  reference) with the indoor pot/globe/topiary set cut to furniture scale.
- **Scope correction honored:** an RPG candelabra trim shipped alongside it was
  the cloud session over-reading feedback; client corrected (runner only) and it
  was reverted same-day. Working Principle #10 applies to sessions, not just art.
- **Jelly UI shipped** (client-directed): CSS spring press + single-bounce card
  pop, staggered overlay rows, `.tpress` hook in `tbind` for touch pads. All
  gated by `body.rm` = reduce-motion setting OR OS preference. Don't add motion
  outside this system, and don't animate under `body.rm`.
- **Illustrated Development Record PDF** (client edition, for Jandé): generated
  by `build_client.py` from DEVELOPMENT_RECORD.md + fresh captures of the LIVE
  build; play-link buttons embedded; internal plumbing (bug log, credentials)
  stripped. Regenerate, never hand-edit.

Paid, professional-grade promo game for the R&B artist **Jandé** (always
accented: Jandé / JANDÉ). $5k upfront + $5k on delivery. Commercial bar.

## 📋 DOC ACCURACY PASS — 2026-07-25 (cloud session) — laptop, please read
This file is append-only strata, so its older body had drifted into contradicting
its own newer top. Nothing historical was deleted; stale entries are now marked
inline and dated. What changed:
1. **`## Deploy recipe` (bottom) was DANGEROUS** — it taught `git add -A` +
   hand-built `gh-pages`, i.e. exactly the leak vector the 🚨 banner below
   forbids, and it predated `web/` so it shipped a broken deploy. Replaced with
   `bash tools/deploy.sh`.
2. **Ground rule #1 was wrong** on all three claims (~2.4MB / all-embedded /
   no-network). Corrected to ~0.33MB + `web/` + the leaderboard Worker.
3. Shipped work no longer labelled "ACTIVE"/"CURRENT FOCUS": 3D Temple phases,
   the AutoSprite whimsy pack, the Groom boss, and the backlog.
4. Testing recipe: `window._dbg` → the shipped `#dev` hooks.
5. **Corrected 07-26 after a code-verified sweep:** item 8 below and the PRO
   AUDIT list still called the stage 1-8 obstacles "Blender clay" and THE
   PRINCE "a Blender primitive". Both were already painted and shipped
   (`076c90a`, `ce84def`). **All three PRO-AUDIT items are now closed.**
   Verified against the code, not the prose — the atlases and `prince` all
   resolve to painted `web/*.webp`, and all 54 asset refs exist on disk.
6. **Also closed 07-26:** three sections still headed "ACTIVE"/"OPEN BUG" were
   already shipped — Runner décor prop quality (`eae13f7`, `d707394`), the
   library reading-table obstacle (`4a224fc`), and the RESONANCE/LV vs
   `#topBtns` HUD overlap (fixed by the laptop). **Net result: this file no
   longer lists any open art/Blender task that is actually finished.**

**Also corrected: `CLAUDE.md`** — its top still described the parked **Phaser 3 +
Vite** scaffold and instructed sessions to "keep using it; do not hand-roll a
render loop," pointing work at `src/scenes/` instead of `index.html`. Rewritten to
the shipped architecture; your July 25 session note is preserved verbatim.
`DEVELOPMENT_RECORD.md` (committed 07-25) is now the canonical full history.

## ✅ RESOLVED + ENFORCED — STOCK GLYPHS (52 → 0, gate live)
All 52 sites cleared (38 laptop + 14 cloud, incl. drawn note/pips/tick/legend
primitives). `tools/glyph_gate.py` now runs inside `deploy.sh` and BLOCKS any
deploy that ships symbol/emoji characters — the directive is enforced, not
remembered. NOTE FOR LAPTOP: your deploys now run this gate automatically.

### (was) 🔴 ACTIVE — STOCK GLYPHS REGRESSED
Client flagged the `▶` on the PROCEED button. Audit found **52 user-visible
stock-glyph sites** — this is a **REGRESSION**: the de-emoji sweep shipped
2026-07-21 (13 baked pixel icons) but that icon system is gone from the build,
and every UI added since (stage select, settings, Boutique atlas, map legend,
STAGE CLEAR tally, boss toasts) reintroduced raw Unicode. On iOS `⏸ ⚙ ⚑ ✦`
render as Apple system/emoji art inside a storybook UI — exactly the look the
client banned. **Full site-by-site list + replacements: `docs/GLYPH_SWEEP.md`.**
~Half are pure decoration (just delete); most of the rest become plain words;
only ~6 need a drawn primitive. Includes a proposed `tools/deploy.sh` gate that
FAILS the deploy on non-ASCII outside comments — the rule keeps coming back
because nothing enforces it.

## ✅ DONE — RPG end-of-stage SCORED TALLY (laptop `23f8558`/`24049d4`)
Shipped: per-metric arcade rank-out with achieved/par columns, derived
`STAGE_PAR=[70..120]` + `PAR_DIFF` difficulty scaling, per-stage counters
(`GS.kills/dmgTaken/notes0`), sticky action row. Remaining: one play-test pass
on the par values (client's call).

### (was) 🟡 ACTIVE — RPG end-of-stage SCORED TALLY
Client wants a proper arcade rank-out after each RPG boss instead of rolling
straight into the next stage. **Spec + reference image:
`docs/STAGE_CLEAR_TALLY.md`.** Note: `showLevelClear()` already exists and
works (overlay, freeze, PROCEED button) — this is a **content/presentation
change to that function**, not a new screen. Today it prints *cumulative run*
totals; the client wants *this stage's* performance scored per metric with
achieved/par values and a TOTAL. Time and distance already reset per stage
(`GS.tick`, `GS.dist`); kills, foes-spawned, damage-taken, per-stage notes and
a `STAGE_PAR[9]` table all need adding. RPG only — the runner has no stage boss.
**Par times + scoring are now specced** in the same doc — derived from the real
constants (`stageEnd=330`, `T=32`, run 6.4px/f, boss HP `7+ai*2`) rather than
guessed: `STAGE_PAR=[70,70,80,90,95,100,105,115,120]` seconds, rising 1:10→2:00
with the difficulty ramp, plus a `PAR_DIFF` multiplier (par MUST scale with the
difficulty setting or Hard can never beat par — boss HP already scales ×1.4).
Scoring formulas included; note the reference's TIME row is exactly
`10000 − secondsOver×20`. Needs one play-test calibration pass.
Heads-up: the current tally uses `✦ ◈ ♪ ◆ ▶` as visual elements, which breaks
the no-stock-glyphs directive — free chance to retire them during the redesign.

## ✅ MOSTLY RESOLVED — LANDSCAPE (client-reported 07-26, fixed same day)
All four root-caused bugs are **fixed and live** (`e15df64`, `706b6d8`,
`745b348`, `24049d4`): décor baseline now tracks the world floor (clamp
removed), runner hazards are height-derived, backdrop tiles snap to shared
integer edges, the ground slab is gone, blank platforms use the baked floor
texture, and the footer flows instead of floating. Landscape controls confirmed
OK on device. **Still open from this report: the overlay clips its own content**
(needs an on-device retest). Original brief kept below for the record.

### (was) 🔴 ACTIVE — LANDSCAPE IS BROKEN
Client played in landscape on iPhone/Safari: *"This is how horrible everything
looks sideways."* Portrait is fine. **Full brief with 10 annotated screenshots,
root-cause analysis and code line refs: `docs/LANDSCAPE_FIX_BRIEF.md`.**
**ROOT CAUSE (issue #0):** the backdrop/décor band is drawn in **screen space**
while the world is drawn `scale(ZOOM)` — and `drawMansionBG` computes
`groundY = min(H*0.82, 14*32 - camY)` with **no `* ZOOM`**. Since side-mode
`ZOOM` is clamped to [0.5,0.78] and is never 1, the props' ground line never
matches the real floor (statues/candles sit buried), and `groundY` tracks
`camY` at rate 1.0 while the floor tracks it at 0.78 — so they **drift apart
when you jump**. Prop sizes (`propSp/dh2/dw2/plant`) are fixed screen px too,
so nothing is sized right per orientation. Client: *"statues and candles are
under the floor, then in the air when you jump."*
**Two more root-caused (client-reported 07-26):** (a) RUNNER hazards are sized
off viewport WIDTH (`obW=max(laneW,H*0.125)`, `laneW=W*0.185`) while the hero is
sized off HEIGHT (`figH=H*0.34`) — so an obstacle is 0.40x her height in
portrait but 1.30x in landscape (3.3x bigger relative to her), which is why
roll-under arches tower instead of reading as duckable; same on any large
desktop window. The portrait floor is fine, it just never got a ceiling.
(b) The painted RPG backdrop still tiles at **fractional** x/width (line 3539)
so seam lines scroll across — the wall band's `Math.round` shared-edge snap
(line 3563) was never applied to it.
Second, separate bug: in landscape a fixed *world-space* camera margin below the floor
becomes ~39% of a short viewport (vs ~15% in portrait), so a featureless
ground slab eats the screen and hides the painted backdrops.
*(Superseded 08-09 `dabe9e2`: the below-floor band is no longer featureless — it
is `drawUndercroft`, a per-stage cross-section — and the anchor is `GROUNDF`,
not a literal. See the 08-09 entry at the top of this file.)* Plus blank
untextured platforms, a tile column into the sky, a backdrop seam, and
overlay/footer clipping on register / how-to / game-over.
✅ **#0 RESOLVED 07-26 (`24049d4`):** clamp removed, verified in code. *(was:* the `* _wz` half landed, but the leftover
`Math.min(floorY=H*0.82, …)` clamp (line 3555) is now the bug — `floorY` is a
FIXED screen row, so the moment the camera rises `groundY` pins and stops
tracking, freezing the décor to the backdrop while the stage floor scrolls.
In landscape it sits just **4px** under the clamp at rest, so any jump pins it;
in portrait the clamp is ~475px away and never engages — which is why it only
shows sideways. Client: *"locked to the background floor, but not the stage
floor."* Drop the clamp (or clamp only the backdrop draw rect and give the
décor an unclamped baseline). Full numbers in the brief.)*
⚠️ **RETEST 07-26 (post-deploy):** #0b/#1 confirmed FIXED on device — the
slab is gone and décor plants correctly. **But the `.site-footer` fix was gated
to `@media (orientation:landscape)` (line 298→309), so in PORTRAIT the
PRODBYKCTW footer still sits on top of the THE BOUTIQUE button.** Portrait is
the primary orientation — content height, not orientation, is what causes the
collision. See the FOLLOW-UP section of the brief.
✅ Resolved by the same report: the landscape **control cluster fits on screen**
— the long-open "verify landscape controls on device" item is now confirmed OK.

## 🚨 REPO CHANGED — read before you deploy (2026-07-22, laptop session)
1. **Assets are now EXTERNAL.** `index.html` shrank 4.4 MB → 0.30 MB; every
   embedded base64 blob ≥1 KB was extracted to **`web/<sha1>.<ext>`** (55 files,
   content-addressed). Consumers just do `img.src="web/…"`. To re-embed or edit
   an asset, edit the file in `web/` (or re-run `tools/externalize_assets.py`
   after re-inlining). The game now REQUIRES the `web/` folder to be deployed.
2. **gh-pages history was PURGED and force-pushed.** Old deploys had leaked
   `assets/` (Jandé's real reference photos + 3D-likeness + a Cloudflare account
   cache) onto the PUBLIC branch via `git add -A`. gh-pages is now a fresh orphan
   with game files only. If you have a local gh-pages, reset it:
   `git fetch origin && git branch -f gh-pages origin/gh-pages`.
3. **DEPLOY ONLY via `bash tools/deploy.sh`.** It publishes index.html + web/ +
   icons + manifest as a fresh orphan and hard-aborts if anything sensitive is
   staged. **NEVER `git add -A` on gh-pages** — that is what leaked the photos.
4. **`assets/` stays git-ignored** (real photos live there locally only).
5. TODO (client, not us): rotate the Cloudflare API token — its account cache
   was briefly public before the purge.
6. **Load/crash state is now controlled.** The retired corridor-backdrop system
   (data, loader, draw code, 9 image files) is fully removed, and the runner's
   old procedural-terrain fallback is gone. When the GL world's textures are
   still streaming, `drawT` paints a clean backdrop in the stage's own sky→fog
   palette and `updateT` HOLDS the run (no spawns/collisions) until `GLW.ready()`.
   Never reintroduce a pre-GL placeholder renderer for outdoor stages.
7. The library no longer has a (nonsensical) grazing bunny — `LOOK[0].props`
   is `[12,13]` (globe-on-table + topiary only).
8. ~~**OPEN / OPTIONAL:** stages 1-8 obstacles are still older Blender "clay"~~
   ✅ **DONE — superseded 2026-07-23/25.** All stage 1-8 obstacles were painted in
   `076c90a` ("Paint all stage 1-8 obstacles (24 assets): arches/logs/hedges/
   balustrades/toadstools/hay/clouds/truss — retire Blender clay"). Two of the
   three atlases were revised again on 07-25: `obgate` → `c294e49` (sky-stage
   arch = roll-under gate), `obwall` → `98cce3c` (solid cloud wall). Verified in
   code: `oblow/obgate/obwall` all point at painted `web/*.webp`. **No clay
   remains.**


## ✅ DONE (was "🎨 ACTIVE for the BLENDER session"): Runner décor prop quality
> **Shipped.** Executed premium (`3bc652a`), then superseded by the painted
> AutoSprite set: `eae13f7` (procedural → painted) + `d707394` (last 4 cells —
> globe, topiary, bunnies = full painted set). Brief kept below as reference.
Full brief with the exact drop-in spec, the 16-cell atlas map, per-stage
usage, workflow, and swap recipe: **`BLENDER_PROPS_BRIEF.md`**. Baseline
images: `assets_whimsy/outprops_current.png` (+ `_labeled.png`). TL;DR: same
whimsical style + same 16-cell **1728×240** transparent atlas (108×240 cells,
bottom-anchored), just far higher fidelity (real bark/marble/petals). Author
at neutral mid-key colour — the engine now adds per-prop hue variation.
Placement/composition is already done by the cloud session; this is the
sprites-detail lever for the "premium" look.

## ✅ DONE (was "🎨 ACTIVE for the BLENDER session"): library obstacle → reading table
> **Shipped** in `4a224fc` — painted library obstacles: reading table (slide),
> bookcase (block), books (jump). Spec kept below as reference.
The library full-blocker (`wall`, cell 0) reads as an abstract wooden board;
the client wants a clear **library reading table**. Exact spec + a drop-in
`obstacles3d.py` snippet + the render/embed steps:
**`tools/blender/OBSTACLE_LIBRARY_TABLE.md`**. No game-code change needed —
just re-render `wall_0` and re-run `tools/embed_obstacles.py`.

## ✅ FIXED (was "🐞 OPEN BUG for the LAPTOP session"): RESONANCE/LV vs #topBtns
> **Resolved by the laptop session** (`d252b61` + the top-left combined-bar
> move) — see the cross-session log near the bottom of this file. Kept for
> context; not an open bug.
The enlarged RESONANCE/level meters from `c3286be` ("larger health/power
meters") now **overlap the top-right sound + pause buttons** (`#topBtns`).
On mobile `.strk` is 128px wide and the `.slbl` labels ("RESONANCE" / "LV
N") in `.hud-r` collide with the two round buttons — visible in both RPG
and Temple. A cloud session found this while integrating and is
deliberately NOT touching it to avoid clashing with your active HUD work.
Fix by capping `.hud-r` width or nudging `#topBtns` clear (or shrink the
meters a touch). NB: the top-CENTER band under the distance meter is the
power-up chip HUD (`drawFxChips`) — leave room for it, don't move meters
into it.

## ⚠ BRANCH DISCIPLINE (a real incident, don't repeat it)
A previous session committed 10 game changes ONLY to `gh-pages`, splitting the
live game from the dev branch. That is now reconciled. The rule:
- **Develop on `claude/hand-painted-architecture-bg-0MAiy`** — every game
  change lands here first.
- **`gh-pages` is deploy-only**: `git checkout <dev-branch> -- index.html`,
  commit, push. Never author changes there.
- Before starting work, ALWAYS `git fetch` and check BOTH branches for
  commits you don't have (other sessions + the user's laptop push here too).

## ⚠ TYPOGRAPHY — two-tier system (don't flatten it back)
A cloud session established a type SYSTEM after the client called the
all-Storyboo look "AI slop". Storyboo is now the **display** face only:
the JANDÉ wordmark, the one hero heading per screen (`.tw-j`, `.lb-h`,
`.ms-h`, `.ht-title`, in-game `.lc-t`), and big canvas titles. **Body/UI
text — sub-copy, labels, inputs, hints, card descriptions, buttons — uses
`var(--body)`** (a system humanist sans, defined in `:root`, no web
request). Do NOT put Storyboo back on body copy; a novelty face on running
text is exactly what read as "slop". Add new UI text with `var(--body)`
and reach for `var(--disp)` only for a genuine display moment.

## ⚠ INTRO CUTSCENE — removed + archived (client-directed)
The old intro video no longer fits the game's direction and is retired.
It's archived at `archive/intro/` (mp4 + the exact markup/JS + a restore
README). `#tPress` now goes straight to `#loginScreen`. A NEW intro will
be produced later — when it exists, follow `archive/intro/README.md` to
re-wire it. Don't resurrect the old one.

## Ground rules
1. The game is ONE file, **`index.html`** (~0.33MB) **+ the `web/` folder**.
   *(Corrected 2026-07-25: this rule used to say ~2.4MB / "all assets
   base64-embedded" / "no runtime network requests" — all three are now wrong.
   Assets were externalized to `web/<sha1>.<ext>`, and the leaderboard Worker is
   a real runtime call. See the 🚨 banner at the top.)* Watch total size —
   quantize PNGs (palette mode) before adding heavy sheets.
2. **Never modify Jandé's original side-view sprite art**
   (`SPRITES.idle/run/jump/attack/dash/block/dance`). Back-view `bk*` slots
   and everything else is fair game.
3. Never commit API keys, and never commit photos of Jandé (real person,
   public repo). Process reference from chat uploads only.
4. Mobile first: fixed-timestep loop, DPR cap, touch-action lockouts stay.
   Playwright-test before every deploy (recipe below).
5. NO STOCK GLYPHS IN GAME UI (client directive, learned the hard way):
   never use Unicode arrows/symbols/emoji as visual elements — the OS
   renders them as generic system/emoji art, off-theme. Anything visual
   is a MADE asset in the game's pixel style (see the baked data-URI
   arrows in the CSS, tools/ bakers) or plain words. This applies to
   buttons, cards, hints, canvas text, toasts — everywhere.

## ART DIRECTION PIVOT (client-directed): WHIMSICAL PRINCESS FAIRYTALE
The dark mansion is out. New vibe: sunshine, fairies, sparkles, birds,
water fountains, statues, outdoor stages — bright pastel fairytale. A full
approved starter kit is committed at `assets_whimsy/` (same cell dims as
current TEXDATA — drop-in): `walls_whimsy.png`, `floors_whimsy.png`, and
`ambient_whimsy.png` (fairy x2, bird x2, sparkle x3, petal — for an ambient
overlay particle system: drifting fairies, birds crossing sky rooms,
sparkle trail behind Jandé, falling petals). Baker: `tools/bake_whimsy.py`.
The 9 rooms, re-themed as a day-cycle that ends in her concert:
  0 THE SUNLIT LIBRARY — Morning Pages          (honey wood, sky window, butterflies)
  1 ROSE GARDEN WALTZ — Courtyard of Roses      (outdoor: hedge, roses, doves)
  2 BLOSSOM PROMENADE — Petals in the Wind      (cherry canopy, red bridge)
  3 THE CRYSTAL BALLROOM — First Dance          (pastel pink, mirrors, chandelier)
  4 FOUNTAIN PLAZA — Wishes in the Water        (tiered fountain, rainbow, statue)
  5 SWAN LAKE TERRACE — Grace on the Water      (lake, swans, willow) [swap w/ 6 for day-cycle order]
  6 STARLIGHT CONSERVATORY — Fireflies at Dusk  (glass, glow flowers, fireflies)
  7 GALLERY OF DREAMS — Once Upon a Canvas      (pastel paintings, sun medallion)
  8 THE SUNSET STAGE — Her Encore               (outdoor concert finale: truss lights,
                                                 confetti, crowd with phone lights)
Update STAGES names/themes/pc/ac to pastels+gold; skies go bright; keep the
chaser DARK (the one shadow in a bright world = drama). Music: transpose the
generative score to MAJOR keys / brighter timbres to match.
✅ **DONE (was "▶ ACTIVE ART TASK")** — the whimsical pack was produced through
AutoSprite and shipped, then superseded by the painted-props overhaul logged
further down this file. Brief kept for reference:
`assets_whimsy/AUTOSPRITE_BRIEF.md`.

## ✅ SHIPPED (was "CURRENT DIRECTION"): Temple View goes 3D
> **Done as of 2026-07-25** — all three phases shipped. "Temple View" is now
> **ROYAL RUNNER**: a real hand-written WebGL 3D world (GLWORLD). Kept below as
> the architectural rationale; it is history, not an open task.
The user has, on their laptop: Blender (with blender-mcp), a **Rodin AI 3D
model of Jandé**, and a working **lattice-deformation animation pipeline**
that already produced the current bkrun/bkjump/bkslide sheets (3D renders →
sprite strips). "Going 3D" means evolving Temple View from the canvas-2D
pseudo-perspective into real 3D rendering while KEEPING the single-file rule.

Recommended phased architecture (no three.js — a custom minimal WebGL
renderer keeps us self-contained; there is already GL scaffolding in the file:
`initGL`, `VERT`/`FRAG`, `glC` canvas under the 2D `fxC` canvas):
- **Phase 1 — GL corridor**: true perspective-projected corridor geometry
  (two wall quads, floor, vaulted ceiling) textured from the existing TEX
  atlas, depth fog, real camera yaw swing on corner turns. Gameplay logic in
  `updateT` stays byte-identical; only drawT's world layer moves to GL.
  HUD/toasts/sprites stay on the 2D canvas above.
- **Phase 2 — 3D obstacles**: hurdles/gates/walls as textured boxes in the
  same GL scene (replaces billboard rects), coins/pickups stay billboards.
- **Phase 3 — character**: EITHER keep the Rodin-rendered sprite billboards
  (near-identical at this camera, cheap) OR embed a minified glTF of the
  Rodin model + a tiny skinned-mesh renderer. Billboards recommended unless
  the user insists — realtime skinning in hand-rolled GL is a big lift.
Division of labor: the user's LAPTOP session (Blender/Rodin) is the asset
factory — request renders/sheets from the user; cloud sessions integrate.

## What exists (all live at https://prodbykctw-max.github.io/once-upon-a-time/)
- **ACTION RPG** (side, free control — NOT an auto-runner): stick/arrows move
  her both ways, dash w/ i-frames kills on contact, Mic Strike, stomps,
  hunting imps + diving cupid skulls, persistent RPG level (`jande_rpg`),
  combos, damage pops, idle + dance easter egg, joystick+buttons on touch.
- **TEMPLE VIEW** (3-lane Temple Run): corner turns w/ camera swing, The
  Groom's Shadow chaser (stumble-twice rule), magnet/boost/x2/shield/encore,
  3 coin tiers, gems + RISE AGAIN revive, vaulted ceilings + pillars + 3D
  obstacle rendering (previous session's upgrade), Rodin-rendered character.
- **Shared**: 9 themed rooms w/ 500m crossfades, 2.5D component-built
  wall/floor/decor assets used by BOTH modes, achievements (11), objectives
  w/ permanent multiplier (10), local top-10 leaderboard, gem wallet,
  death-into-music-notes bloom, synthesized WebAudio score (transposes per
  room, reacts to speed/danger/boost; coin pickups walk a pentatonic scale)
  + full SFX kit + mute toggle (`jande_mute`).

## Design principles (binding — mitigations for speed-game pitfalls)
1. Reaction budget ≥0.3s: difficulty scales via density/variety, never via
   reaction time below the floor (spacing already scales with speed).
2. Readability first: every hazard grounded (contact shadows, plinths,
   floor-scroll synced to entity speed — do not break `wz`).
3. Forgive inputs: coyote time, buffers, generous pickups, tight hazards,
   i-frames. All implemented — preserve them.
4. Juice every verb. DONE: hitstop on kills/stumbles (GS.hitstop).
5. Fail fast, retry faster. DONE: tap-anywhere-to-retry on the overlay.
6. Teach one verb at a time (coins-only <40m, turns >130m). Keep.
7. DONE: adaptive difficulty (jande_adapt: early-death counter widens
   spawn spacing via adaptF(), cruisers >800m get +pressure; pity gem
   after 3 quick deaths). 8. DONE: near-miss bonus (+25x, CLOSE! flash).
9. DONE: daily streak (jande_streak: consecutive days pay 1-5 gems).
   THE BOUTIQUE (jande_shop): banked Grace Notes (wallet.notes, banked
   at game over) buy power-up duration levels + Devotion Hearts; UI on
   the mode screen (msShop/shopScr); durations read shop() at pickup.
   Dev hooks (_devStep/_devState) now require #dev in the URL.
10. Frame rate is a mechanic: keep 60Hz fixed timestep and draw budgets.

## Asset pipeline
- `TEXDATA`→`TEX`: walls (9×144x192, 2.5D shaded), floors (9×96x96), decor
  (9×144x240), chaser (4×176x224), foes (6×136x152), items (8×64x64).
- `SPRITES.bkrun/bkjump/bkslide`: Rodin-model renders (current), swappable.
- `tools/` has the Python/Pillow bakers for every procedural asset.
- Swap recipe: new PNG → base64 → re.sub the data URI in TEXDATA/SPRITES;
  keep cell dims stable or update the drawImage source rects.

## Character reference
Reference subject IS Jandé (first-party likeness). Costume: the GOWN (white,
high slit, gold belt/hem, auburn curls down, white boots/gloves) — reference
photos are for proportions/likeness only. User holds jande_character_ref.zip
(4 stills + 8 turnaround keyframes); ask for it in chat when needed.

## Testing recipe (Playwright, /opt/pw-browsers/chromium)
file:// → click `#tPress` → force-end `<video>` + dispatch 'ended' → click
"play without" → `#msSide` / `#msTemple` → wait ~3.2s → play/screenshot.
Dev hooks (shipped, gated behind `#dev` in the URL — no longer removed before
commit): `_devMut(fn)`, `_devStep(n)`, `_devState()`, `_devWallet(g)`.
*(Corrected 2026-07-25: the old `window._dbg` hook no longer exists.)*
Keys: Space jump · ArrowDown slide · X strike · Shift dash · Arrows · P pause.

## Deploy recipe
> ⛔ **CORRECTED 2026-07-25.** The old recipe here used `git add -A` and hand-built
> `gh-pages` — that is **exactly what leaked Jandé's real photos** onto the public
> branch (see the 🚨 banner at the top of this file). It also predates external
> assets, so it shipped `index.html` **without `web/`** — a broken deploy. Never
> use it. The only supported path:
```
# 1. land work on the dev branch
git add <specific files> && git commit -m "..." \
  && git push -u origin claude/hand-painted-architecture-bg-0MAiy
# 2. deploy (ships index.html + web/ + icons + manifest; aborts on sensitive files)
bash tools/deploy.sh
```

## Backlog (user-approved) — status 2026-07-25
- ✅ 3D Temple phases 1→3 — **DONE** (shipped as Royal Runner / GLWORLD)
- ✅ Gameplay: hitstop, instant retry, adaptive difficulty, near-miss, streak — **DONE**
- ✅ Store: spend Grace Notes on power-up upgrades — **DONE** (The Boutique)
- ✅ Global leaderboard (Cloudflare Worker) — **DONE + live**
- ⬜ Custom domain + EmailJS keys for registration — **still open** (placeholders
  unfilled; signups fall back to `localStorage`)

## Cross-session log
- RESOLVED (laptop session): RESONANCE/LV meters vs #topBtns overlap. Fixed by dropping .hud-r below the 40px top-button row (vertical clearance), not horizontal padding (the map button makes #topBtns too wide to reserve). Verified no overlap desktop+mobile.

## Cross-session log (laptop → cloud)
- Read CLOUD_SESSION_SUMMARY.md. In sync on everything EXCEPT one intertwine:
  your in-progress `footPad` fix in drawT's temple hero-draw is the SAME block
  my behind-view sprite swap (c6cd1e8) touched. The float-above-shadow gap is
  from the new iso_run_up sprite's feet sitting ~87.5% up the cell. It's yours
  — I will NOT touch drawT hero-draw; land footPad and it accounts for my sprite.
- My d252b61 (.hud-r margin-top:42px) is now likely vestigial after your
  top-left combined-bar move — only nudges the score. User likes current HUD;
  leaving it. Remove if the score ever sits low.
- Open decision (user's call): in-game HUD labels (.slbl/.hud-act/.hud-sc) are
  still Storyboo from my fcad3d5 swap — violates the two-tier rule but the user
  said they like the current HUD, so untouched.

## Leaderboard — LIVE (laptop session deployed it)
- Worker DEPLOYED: https://jande-leaderboard.prodbykctw.workers.dev (binds the
  jande-leaderboard KV). `npx wrangler login` + `wrangler deploy` from the
  laptop, per cloudflare/README.md.
- Verified end-to-end: OPTIONS preflight 200, POST /submit {ok,rank}, GET /top
  returns runs with Access-Control-Allow-Origin:* — cross-origin from gh-pages
  works.
- LB_URL baked into index.html (0cc88e5) + deployed to gh-pages — every visitor
  gets the global board, no ?lb= needed. Boards cleared to [] for launch.
- Backlog item "Global leaderboard (Cloudflare)" → DONE.

## Runner prop-quality upgrade — DONE (laptop/Blender session)
- Executed BLENDER_PROPS_BRIEF.md. All 16 cells re-authored premium in
  tools/blender/outdoor_props_hq.py: organic displaced canopies clad in leaf
  cards, procedural bark, HQ marble, real rose blooms, swept angel wings,
  layered swan feathers. Neutral mid-key (engine aTint untouched).
- Atlas 3456x480 (16x 216x480, same 0.45 aspect → NO JS change; /16 UV holds),
  WebP 121KB. Swapped GLWDATA.props. Contact sheet: assets_whimsy/outprops_new.png.
- Verified: atlas independently (contact sheet — bottom-anchored, correct cells,
  clean alpha) + syntax. NOT visually confirmed in-engine: the rebuilt pre-game
  flow + GL rAF suspension in the headless preview blocks single-shot GL capture.
  Structurally a pure data swap over unchanged render code, so low risk — but a
  cloud Playwright pass on ?stage=1/4 would be a good confirm if you can.

## PRO AUDIT + prop overhaul → PAINTED (laptop session)
Ran a full pro audit both modes. Verdict: GL world/ground/characters good;
PROCEDURAL PROPS + OBSTACLES were the weak link (clay blobs). Proved it with a
3-way tree test (procedural vs PolyHaven CC0 3D vs AutoSprite 2D) — AutoSprite
painted wins decisively for this storybook style.
- EXECUTED: retired the procedural décor. Cells 0-11 are now AutoSprite ULTRA
  painted props (trees, blossom, willow, rose bush, marble fountain, angel,
  lamp-flower, daisies, swans), white-keyed + bottom-anchored into the same
  3456x480 / 16-cell / 0.45-aspect atlas (NO JS change, u=kind/16 holds).
  GLWDATA.props swapped, 262KB WebP. Contact: assets_whimsy/outprops_painted.png.
- STILL PROCEDURAL (follow-up): cells 12-15 (indoor globe/topiary/bunny,
  library-only). Paint later for full consistency.
- AUDIT items — ✅ **ALL THREE CLOSED** (verified in code 2026-07-26):
  - ~~RPG BOSS "The Groom Who Lied" is still canvas rectangles~~ → **DONE.**
    Superseded entirely: there are now **nine** unique painted AutoSprite bosses
    (idle + themed defeat), the Groom being the stage-9 finale.
  - ~~THE PRINCE (ending) is Blender primitive~~ → **DONE** in `ce84def`
    ("Painted Boss + Prince — retire canvas/primitive versions"). Live as
    `prince:"web/6bfe5d567826.webp"` (78 KB painted).
  - ~~Temple OBSTACLES still procedural~~ → **DONE** in `076c90a` (all 24 stage
    1-8 assets painted), with `obgate`/`obwall` further revised 07-25. See item 8.

## Runner prop system fixes (laptop) + engine-source note
Fixed client-reported Runner prop issues in index.html:
- Per-kind world height (new PROPH table) so TREES tower over Jandé and
  bunnies stay small (was one flat 560 for everything → trees read short).
- Billboard aspect corrected to the painted cell 0.45 (pw=ph*0.45) — no stretch.
- Library (stage 0): added the GLOBE (props 13,14,13 → 12,13,14); pushed the
  bookcase walls out (uWallX 1.18→1.5) and moved décor bands into the shoulder
  (1.22-1.46) so plants stand on the floor in front of the shelves instead of
  clipping into them.
- Wider height + placement variation (hv 0.6-1.57, more jitter/spacing).
⚠ NOT visually verified — the headless preview suspends the GL world. These are
best-judgment; the library wall-push + band placement especially may need a
tuning pass once someone sees it (cloud Playwright on ?stage=0#dev).
⚠ tools/glworld_engine.js is now STALE vs index.html for the prop system. Do NOT
re-sync the engine into index.html without re-applying these changes, or it
reverts them. index.html is authoritative.

## Session update - July 25, 2026

**Shipped today (all live on gh-pages):**
- Nine unique RPG bosses (one per stage, Groom = finale) with themed 5-frame defeats, per-boss
  movement/VFX, and a cinematic death (slow-mo, KO spotlight, push-in that centres the boss).
- STAGE CLEAR end-of-level tally + PROCEED; cleared stages persist and are replayable via Stage
  Select. Stage Select and The Boutique now live on the per-mode how-to screen.
- Six stacked backdrops un-doubled; backdrops draw full and unimpeded at true aspect; ground tiles
  made opaque; interior parquet floor and chandeliers removed from outdoor stages.
- Runner: taller trees + sunflowers, sky-stage arch is now the slide gate and a new solid cloud
  wall is the blocker, wall telegraph added, no more old-world flash on start.
- Every legacy fallback that could surface on a slow/failed load retired.

**Critical fix:** the boss-defeat cinematic left a stale world zoom (`nextStage()` hardcoded
`ZOOM=1` while `resize()` fits it to the device and `VW`/`VH` derive from it), so after the first
boss kill the hero and foes rendered off-screen on every later stage. Zoom now flows through
`BASEZ` + `setZoom()`. **Never assign `ZOOM` directly** - `setZoom()` is the only safe path.

**Verification note:** with the browser pane hidden, `requestAnimationFrame` throttles and the game
loop stalls, so in-pane checks look blank. Use a local harness page that iframes `index.html?stage=N`
and clicks through, captured with headless Chrome - that renders reliably.

**Still open:** rotate the Cloudflare API token (owner action); landscape controls on device;
combat/economy tuning; Stage-Select starting stats (late stages begin at LV1).

## 2026-07-26 — themed gore + projectiles, glyph sweep, tally, landscape

- **Per-boss projectiles**: every villain threw the same red dot. `drawBoss` now
  draws the boss's OWN matter, sized to read as an object — Scarecrow straw,
  Thistle/Thorn barbed thorns, Storm lightning shard, Blossom petal, Lake droplet,
  Ink torn page, Toadstool spores, Groom ember. Colour from `BOSS_GORE`.
- **Lesser-foe blood**: `FOE_GORE[tp]` + `goreOf(f)` — creatures bleed what they
  are made of, humanoids bleed red. Wired into `hitE` and the kill burst.
- **Stock-glyph sweep**: ~38 sites cleared (decoration deleted, label icons to
  words, data icons to words). Load-bearing marks are DRAWN now: `.ic-pause`
  (two CSS bars), `.ic-star`, and `starMark()` for the Wanderer's Map beacon.
- **End-of-stage scored tally** with derived `STAGE_PAR` + `PAR_DIFF`.
- **Landscape/portrait**: reopened #0 fixed (the `floorY` clamp pinned `groundY`),
  footer now flows instead of overlapping, invisible themed scrollbars.

**Standing rule acknowledged:** documentation is updated as part of the same
commit as the work, not afterwards.
