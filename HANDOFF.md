# HANDOFF v2 — Jandé: Once Upon A Time (3D era)

Paid, professional-grade promo game for the R&B artist **Jandé** (always
accented: Jandé / JANDÉ). $5k upfront + $5k on delivery. Commercial bar.

## 🎨 ACTIVE for the BLENDER session: upgrade the Runner décor prop quality
Full brief with the exact drop-in spec, the 16-cell atlas map, per-stage
usage, workflow, and swap recipe: **`BLENDER_PROPS_BRIEF.md`**. Baseline
images: `assets_whimsy/outprops_current.png` (+ `_labeled.png`). TL;DR: same
whimsical style + same 16-cell **1728×240** transparent atlas (108×240 cells,
bottom-anchored), just far higher fidelity (real bark/marble/petals). Author
at neutral mid-key colour — the engine now adds per-prop hue variation.
Placement/composition is already done by the cloud session; this is the
sprites-detail lever for the "premium" look.

## 🎨 ACTIVE for the BLENDER session: library runner obstacle → reading table
The library full-blocker (`wall`, cell 0) reads as an abstract wooden board;
the client wants a clear **library reading table**. Exact spec + a drop-in
`obstacles3d.py` snippet + the render/embed steps:
**`tools/blender/OBSTACLE_LIBRARY_TABLE.md`**. No game-code change needed —
just re-render `wall_0` and re-run `tools/embed_obstacles.py`.

## 🐞 OPEN BUG for the LAPTOP session (your HUD area, so you own the fix)
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
1. The game is ONE self-contained file, **`index.html`** (~2.4MB). No runtime
   network requests; all assets base64-embedded. Watch total size — quantize
   PNGs (palette mode) before embedding when sheets get heavy.
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
▶ ACTIVE ART TASK (client-directed): generate the production versions of
this pack through AUTOSPRITE — the complete brief with all 27+ prompts,
processing spec, size budget, and QA gates is at
`assets_whimsy/AUTOSPRITE_BRIEF.md`. Execute it top to bottom; show the
user the preview contact sheet before embedding anything into index.html.

## CURRENT DIRECTION: Temple View goes 3D
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
Debug hook (REMOVE before commit): `window._dbg=function(fn){fn(GS);};`
Keys: Space jump · ArrowDown slide · X strike · Shift dash · Arrows · P pause.

## Deploy recipe
```
git add -A && git commit -m "..." && git push -u origin claude/hand-painted-architecture-bg-0MAiy
git checkout gh-pages && git checkout claude/hand-painted-architecture-bg-0MAiy -- index.html \
  && git commit -m "Deploy: ..." && git push -u origin gh-pages \
  && git checkout claude/hand-painted-architecture-bg-0MAiy
```

## Backlog (user-approved)
- 3D Temple phases 1→3 (above) — CURRENT FOCUS
- Gameplay: hitstop, instant retry, adaptive difficulty, near-miss, streak
- Store: spend Grace Notes on power-up upgrades
- Global leaderboard (user has Cloudflare connector: Workers + KV/D1)
- Custom domain + EmailJS keys for registration

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
