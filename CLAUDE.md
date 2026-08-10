# CLAUDE.md — Jandé: Once Upon A Time

> **Doc correction, 2026-07-25 (cloud session).** Everything above the "Session
> update" note used to describe the **Phaser 3 + Vite** scaffold and told sessions
> to "keep using it; do not hand-roll a render loop." That was stale and pointed
> work at `src/scenes/`, which is **not** the shipped game. Phaser was parked long
> ago. The sections below now describe what actually ships. The laptop session's
> July 25 note at the bottom is preserved verbatim.

## What this is
A paid, professional-grade promotional browser game for the R&B artist **Jandé**
(always accented: **Jandé / JANDÉ**) and her song *"Once Upon A Time."*
$5k upfront + $5k on delivery — commercial bar. Goal: fan engagement + email capture.

Two modes, nine themed stages each:
- **ACTION RPG** — side-scroll, free control. Fight an escalating foe roster and
  beat each stage's unique boss to advance.
- **ROYAL RUNNER** — behind-the-back 3D endless run (turns, chaser, obstacles).

Live: https://prodbykctw-max.github.io/once-upon-a-time/

## Stack — ONE self-contained file
The shipped game is **`index.html`** (~0.33 MB). No framework, no bundler, no
build step, no server.

- **Canvas2D** (`#fxC`) — the Action RPG: sprites, entities, particles, HUD.
- **Hand-written WebGL** (`#glC`, the "GLWORLD" engine) — Royal Runner's 3D world.
- **Web Audio, fully synthesized** — all music/SFX generated in-browser, no audio files.
- **External hashed assets** — `web/<sha1>.<ext>` (55 files). The game REQUIRES
  the `web/` folder to be deployed alongside `index.html`.
- **Cloudflare Worker** — the global leaderboard. This is the ONLY runtime
  network call (graceful local-top-10 fallback).

> Hand-rolling the loop and physics is the **deliberate, shipped architecture** —
> not a mistake to undo. Phaser 3 (`src/`, `vite.config.js`) and Godot 4
> (`once-upon-a-time/`) remain in-repo as **parked** scaffolds. Do not migrate the
> game into them without an explicit client decision.

## Run
```bash
python3 -m http.server 8000   # then open http://localhost:8000
```
There is no `npm run dev` / `npm run build` for the shipped game.

## Deploy — the guarded script ONLY
```bash
bash tools/deploy.sh
```
Publishes `index.html` + `web/` + icons + manifest to `gh-pages` as a fresh orphan,
and **hard-aborts if anything sensitive is staged**.

- **NEVER `git add -A` on `gh-pages`.** That is exactly what once leaked Jandé's
  real reference photos onto the public branch.
- `assets/` stays git-ignored — real photos live there locally only, never committed.
- Develop on `claude/hand-painted-architecture-bg-0MAiy`; `gh-pages` is deploy-only.
- `git fetch` before starting — the laptop session pushes here too.

## Where things live in index.html
- **RPG level gen:** `buildRunner` / `genAhead` (streaming; despite the name this
  is the **RPG's** generator, not Royal Runner's) driven by `STAGE_RECIPE[ai]`
  (per-stage gap/platform/hazard/verticality + foe roster).
- **RPG foes:** `GS.foes` — tp0 goblin, tp1 raven, tp2 sprite, tp3 Bramble Knight,
  tp4 Wisp Swarm, tp5 Rose Wraith. Ground types MUST keep the ledge-guard
  (`isSolid(leadC,grow)`) so they don't glide over gaps. Flyers are exempt — they fly.
- **Bosses:** nine unique, one per stage (`BOSS_NAME`, `drawBoss`, `drawBossAura`);
  **The Groom Who Lied** is the stage-9 finale. Gate → sealed arena → defeat → STAGE CLEAR.
- **RPG camera & ground:** `GROUNDF` / `SLAB_R` / `LH` (game-state block) drive both
  camera branches in `update()`; `drawMansionBG` derives `floorY` from `groundY`.
- **Under the floor:** `drawUndercroft` + `drawUCLayer` + the `UCROFT[]` palette
  table — one themed cross-section per stage, drawn before the tiles.
- **Runner:** `updateT` / `drawT` + the GLWORLD engine and `GLWDATA`.
- **Atlases:** `TEXDATA`→`TEX` — `walls, floors, decor, chaser, foes (136×152),
  items, boss (200×280, 9×9 idle+defeat), props`.
- **Persistence:** `jande_maps`, `jande_clears`, `jande_shop`, `jande_settings`,
  `jande_adapt`, `jande_streak`, `jande_mute`, `jande_rpg`.

## Sprites (IMPORTANT)
Jandé's animations are real rendered art. Hero slots in `SPRITES`:
`idle, run, jump, attack, dash, block, dance` (side view) · `refrain, belt,
downstrike` (combat states) · `bkrun, bkjump, bkslide` (Royal Runner back view).

- **Never modify Jandé's original side-view art** (`idle/run/jump/attack/dash/
  block/dance`). Other slots are fair game.
- The sprite faces **RIGHT**; left is a mirror.
- Character/boss art comes from **AutoSprite**; environments from **Blender/Cycles**.
  Bakers/composers live in `tools/`.

## Conventions / guardrails
- Keep the artist's name accented everywhere: **Jandé / JANDÉ**.
- **Music-themed vocabulary** (binding): resource = **RESONANCE**; collectibles =
  **Grace Notes**; melee = **Mic Strike**; projectiles = **Sound Wave / Throw Note**;
  block = **Hold Note**; heal = **Refrain**; magic strike = **Belt**; aerial pogo =
  **Downbeat**; power-ups = **DEVOTION** (+life), **FULL VOICE** (refill),
  **BELT IT OUT** (2× dmg), **HIGH NOTE** (shield).
- **Reskin, don't copy.** Silksong-class mechanics re-expressed as Jandé's voice;
  the word "Silksong" stays at zero in shipped text.
- **Traversability rule:** ground is continuous except defined pits; every pit and
  high ledge must be reachable (≈4 tiles up / ≈5 across). Never create a spot the
  player can fall into with no way out.
- **NO STOCK GLYPHS IN GAME UI** (client directive): never use Unicode arrows/
  symbols/emoji as visual elements — the OS renders them off-theme. Anything
  visual is a made asset in the game's style, or plain words.
- **Two-tier typography:** Storyboo is the **display** face only (wordmark, one
  hero heading per screen). All body/UI text uses `var(--body)`. Don't flatten it
  back — all-Storyboo read as "AI slop" to the client.
- **Never assign `ZOOM` directly** — `setZoom()` is the only safe path (see the
  July 25 note below).
- **The RPG ground line is `GROUNDF` (0.65) — never a literal.** It was a
  hard-coded `0.82` in three independent places (both camera branches and
  `drawMansionBG`'s `floorY`) that agreed only by coincidence. `floorY` now
  derives from the scaled world floor; keep it derived. `SLAB_R` (2) caps how
  many ground rows are **drawn** and is deliberately separate from collision
  depth. **`LH` (22) is DERIVED from `GROUNDF`: `LH*T >= FLOOR_R*T / GROUNDF`** —
  lower `GROUNDF` again and you MUST raise `LH` with it, or landscape silently
  pins to the world's bottom edge and stops matching portrait. The landscape
  camera anchors first and only follows her UP; it must never go back to easing
  at `p.y - VH*0.55`, which made `GROUNDF` a no-op there. Spec:
  `docs/GROUND_LINE_UNDERCROFT.md`.
- **The framing reference is Mario ON A PHONE (~66% ground), not raw NES (~87%).**
  The 4:3 frame is letterboxed into a tall screen and the bars absorb the bottom.
  Quoting the NES number will send you back down to 0.82.
- **`CTRL_TOP` is measured, never guessed.** `#mCtrl` sits on
  `env(safe-area-inset-bottom)`, so where the touch pads start cannot be derived
  from `H`. It is read on resize AND on the start-of-run toggle (the pads only
  get `.on` there). Anything laying out against the bottom of the screen should
  use it rather than inventing another fraction.
- **Below the floor is `drawUndercroft`'s, and only its.** One owner per band —
  the dead "abyss" gradient existed because there were two. It is also real play
  space (pits drop her through it), so anything added there must read at speed,
  stay darker than the hero, and go still under `body.rm` (multiply animated
  terms by `amb`).
- **Screen-vs-world is THE recurring bug of this project — seven instances so
  far.** Décor baseline, runner hazards, backdrop seams, ground slab, wordmark,
  the abyss gradient, the lyric line. Before pinning any quantity to `W`, `H`, or
  a raw screen fraction, ask whether it should scale with the world instead; if
  it must be a screen fraction, derive it from the world value rather than
  restating the number. Portrait hides these — always check landscape.
- **Jelly UI:** all UI motion lives in the JELLY UI CSS block, gated by
  `body.rm` (reduce-motion setting + OS preference via `applyMotionClass()`).
  New buttons/cards get the existing classes; never animate under `body.rm`.
- **Mobile first:** fixed-timestep loop, DPR cap, touch-action lockouts stay.
  Touch controls must keep working in portrait AND landscape.
- Never commit API keys; never commit photos of Jandé (real person, public repo).

## Verifying changes
- Extract the `<script>` blocks and `node --check` them before shipping.
- Audit that `web/…` references exactly equal the files on disk (no missing, no orphans).
- Playwright/headless Chromium at `/opt/pw-browsers/chromium`; dev hooks require
  `#dev` in the URL: `_devMut`, `_devStep`, `_devState`, `_devWallet`.
- **Known limit:** with the preview pane hidden, `requestAnimationFrame` throttles
  and the loop stalls. Use the iframe harness described in the July 25 note.

## Documentation — UPDATE IT WHEN YOU SHIP (client directive, binding)
**A task is not done when the code works — it is done when the code works and
the docs say so.** After every completed item, in the same session:
1. tick it off in whichever `docs/*.md` specs it, citing the commit;
2. move it out of the ACTIVE banners in `HANDOFF.md`;
3. record it in `DEVELOPMENT_RECORD.md` and close the matching Open Thread;
4. update `CLAUDE.md` if architecture, workflow or a guardrail changed.
Never leave finished work labelled ACTIVE/OPEN. Stale docs have already cost
this project real rework — a 2026-07-25/26 audit found this file still
describing a Phaser 3 build, `HANDOFF.md` teaching the `git add -A` deploy
recipe that leaked the client's real photos, and six shipped tasks still
marked open (two of which were re-reported as bugs because the docs said so).

## Documentation
`DEVELOPMENT_RECORD.md` is the canonical, consolidated project history (all eras,
bug log, engine evolution, asset pipeline, open threads). `HANDOFF.md` is the
cross-session coordination log. Prefer those over re-deriving history.

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
