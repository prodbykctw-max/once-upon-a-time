# JANDÉ — "Once Upon A Time"
## The Complete Development Record — Day 1, Step 1 → Current State

**Client:** Jandé — R&B/Soul artist, Atlanta GA ([@jandelove1](https://instagram.com/jandelove1))
**Studio:** PRODBYKCTW (KCTW) — GitHub `prodbykctw-max`
**Tie-in:** the single *"Once Upon A Time"*
**Purpose:** a promotional browser game for fan engagement + email capture
**Live build:** https://prodbykctw-max.github.io/once-upon-a-time/
**Document assembled:** July 25, 2026 · **updated July 26, 2026 (Era V)** — supersedes and consolidates the CHANGELOG, the Development History & Technical Record, the Ultimate Development Record, and the PRODBYKCTW Build Assessment, and adds **Era IV — The Living Bosses** (the boss-overhaul session), previously undocumented.

---

## AT A GLANCE

| | |
|---|---|
| **Full development span** | ~May 2026 → July 26, 2026 |
| **Development sessions** | 5 origin/design sessions + parallel production sessions + the boss-overhaul session (this record's new Era IV) |
| **Commits shipped** | 150+ on the mainline (patch-delivered RPG overhaul, boss overhaul, Era V landscape/tally/audio/art) |
| **Game modes** | 2 (Action RPG · Royal Runner) |
| **Themed stages** | 9 per mode |
| **Engine pivots** | 5 (Canvas2D → WebGL → Phaser 3 → Godot 4 → hand-written WebGL, shipped as Canvas2D + WebGL hybrid) |
| **Character redesigns** | 4 (8-bit pixel → canvas vector → Silksong-styled → AI-rendered sprite sheets) |
| **RPG bosses** | **9 unique — one per stage**, each with idle + themed defeat animation, signature VFX & movement (The Groom Who Lied is the finale) |
| **Hero animations** | 10 (idle, run, jump, attack, dash, block, dance + Refrain, Belt, Downstrike) |
| **RPG enemy archetypes** | 6 (goblin, raven, sprite, Bramble Knight, Wisp Swarm, Rose Wraith) |
| **Boss projectiles** | 9 painted pieces — each boss throws its own matter (AutoSprite, first cloud-generated art) |
| **Stock glyphs in shipped UI** | **0** — swept 52 → 0, enforced by a deploy gate |
| **Deliverable** | 1 self-contained client-side build, external hashed assets, live on GitHub Pages |
| **Art pipeline** | AutoSprite (characters/bosses) + Blender/Cycles (environments), keyed/normalized/embedded/externalized through baker scripts |

---

## HOW THIS DOCUMENT IS EVIDENCED

Five tiers of evidence, labelled throughout.

- **[SESSION 1–4]** — the origin/design chats (~May 2026): 8-bit princess → Silksong pivot → Jandé photo references → single HTML file; the Ghibli-chibi identity lock-in; the Godot 4 Metroidvania build + bible; the project bible.
- **[PRODUCTION]** — the shipped build sessions, Jun 4 → Jul 23, 2026. Evidenced by the changelog and live-site verification.
- **[ASSESSMENT]** — *Jandé: Once Upon A Time — Build Assessment*, PRODBYKCTW, Jul 23, 2026 — the formal client-facing report with per-feature Playwright counts.
- **[BOSS OVERHAUL]** — **this session**, Jul 23–25, 2026, run in Claude Code (Opus 4.8) on the deploy machine. All work here is directly evidenced by the code written, the JS-validation + web-ref audits run, the in-browser smoke tests, the git history, and the live deploys. Where a claim could not be fully verified in-browser (the RAF-throttle limitation, below), it says so plainly.

---

# ERA I — THE 8-BIT PRINCESS (May 2026) · [SESSION 1]

The project began as a **Super Mario World 3-style** promo game: an 8-bit Black princess (64-px, dark-brown skin, gold ruby crown, purple→red power-up dress) running side-scrolling levels toward a flagpole, gated behind an **EmailJS** registration screen for email capture. Infrastructure (EmailJS + Cloudflare) was inherited from a prior unrelated project ("the luber app").

The concept was themed to the song's emotional arc — five acts, *He Seemed Perfect → Love Bombing → Mixed Signals → The Gaslighting → Once Upon A Time* (infatuation → liberation).

**The Silksong pivot.** The client asked for a dramatic quality jump: clone **Hollow Knight: Silksong**'s mechanics, with Silksong sprite sheets and Terminator 2D / Primal Planet uploaded as references. The build was rebuilt with wall-jump, aerial dive, i-frame dash, four-direction needle attack with pogo, silk-spit projectile, silk-shard collectibles, three enemy archetypes (VOID/WARDEN/LANCER), two boss types (REVENANT, HEARTBREAKER) with phase transitions, palette-shifting parallax, cycling lyric overlays, and mobile touch.

**Pixel → person.** The client uploaded photos of Jandé and called the princess "too childish." The character was redesigned to the real artist — long wavy auburn/honey hair that sways and flips airborne, rich dark-brown skin, urban-chic bodysuit with gold belt, battle cloak, thin glowing needle, chunky sneakers — at "64 bits, not pixels." The Session 1 deliverable: a single self-contained HTML file with all five acts, full Silksong-class mechanics, the mature Jandé, and mobile controls.

**Outcome:** the relationship-arc theme, the email-capture flow, and the core Silksong-inspired mechanics were all established here.

---

# ERA II — THE GODOT AMBITION (May 12–14, 2026) · [SESSIONS 2–4]

**Session 2 — identity lock-in.** AI-tool ranking for likeness (Midjourney v7, Leonardo, Sora/GPT-4o, Flux Kontext, Gemini 2.5 Flash / "Nano Banana"); a forensic portrait breakdown (collar points resting *on* the lapels, tie-knot style, blazer cut); a master **Ghibli-chibi** prompt; four Gemini chibi outputs. The chibi-watercolor style — soft painted shading, warm sienna skin, dark navy hair, storybook atmosphere — became the **canonical visual anchor**.

**Session 3 — the Godot build.** Godot 4.6.2 + GDScript + Compatibility renderer. Produced a full GDD, an **Art Style Bible** (palette: Veil White `#F4ECDC`, Champagne `#C9A86A`, Old Gold `#8B6A2C`, Warm Sienna `#6B3A24`, Plum Shadow `#3B1F37`, Vow Gold `#F2C75C`; master AI prompt template), seven ability designs, a full `CharacterBody2D` state-machine controller, a ready-to-open starter project (`PlayerJande.gd`, `GownTrail.gd`, `PorcelainGuest.gd`, scenes, input map), a 33-step build guide, and a three-act narrative set in the kingdom of **Veilmere** under **The Hush**. The client's uploaded sprite sheets (IMG_1657 "Jandé The Singer", IMG_1656 "Agent Elara") were assessed honestly as **reference sheets, not game-ready** — multi-outfit, inconsistent scale. Direction chosen: **suit = default form, gown = transformation.**

**Session 4 — the project bible.** `ONCE_UPON_A_TIME_PROJECT_BIBLE.md` consolidated everything and reframed the mandate: built **in the tradition of** Silksong (genre conventions + polish ambition) with **original** mechanics framing, visual identity, and lore. Original IP vocabulary locked (Veilmere, The Hush, Hushborn, The Refrain, Chorus, Verse Shards, Memorial Shrine, Thread-Step, Second Verse, Refrain Drop…). A 14-day vertical-slice plan (Chapel of Dust) was scoped.

**End of Era II:** a complete design bible, a Godot scaffold with scripts/scenes, a locked visual identity, a full narrative, and asset prompts — but no shipped public build yet.

---

# ERA III — THE PRODUCTION BUILD (Jun 4 – Jul 23, 2026) · [PRODUCTION]

The project pivoted back to the browser for speed-to-ship; the Godot project was parked as the eventual native engine.

## Phase 1 — Foundation (Jun 4 – Jun 25)

**The 2.5D WebGL rebuild.** One self-contained HTML file (~1.1 MB), base64-embedded sprites + intro video, offline-playable. Two stacked canvases: `#glC` (WebGL background) + `#fxC` (Canvas2D — sprites, entities, particles, HUD). Screen flow Title → BEGIN → intro → registration → game; `show(id)` toggles `.active` on `.screen` divs; the game lives in `#gameWrap` (deliberately not a `.screen`). Constants `T=32`, `GRAV=0.52`, `MASKS=5`, `PW=30`, `PH=86`.

**The sprite pipeline.** Seven animations processed from the artist's near-photographic renders (2688² 7×7 grids, attack 3840² 10×10; RGB on solid black) via Python+PIL/numpy: grid-slice → luminance key-out with soft alpha ramp (preserves hair/gown feathering) → bbox trim → scale-normalize → horizontal strip → 80-colour quantize. ≈150 px tall, 617 KB across seven strips. Convention: **faces right**, left is a mirror; drawn at ≈`PH*1.55` bottom-aligned. `dance` was wired but unbound (candidate: victory pose — *later bound in Era IV*).

**The intro cinematic.** A 4 MB white-gown-reading clip → ffmpeg 153 KB (640×360, CRF 32, no audio), base64-embedded, SKIP + autoplay fallback + 6-s timeout. *(The intro cutscene was later removed in Phase 4.)*

**The nine stages** — each its own palette + distinct layout, not recolors:

| # | Stage | Theme | Primary | Accent |
|---|---|---|---|---|
| I | The Grand Library | Ancient Knowledge | `#8b4513` | `#d4af37` |
| II | Egyptian Hall | Pharaoh's Treasury | `#d4af37` | `#cd853f` |
| III | Samurai Gallery | Warriors Path | `#8b0000` | `#4a3728` |
| IV | Royal Chambers | Luxury Estate | `#4b0082` | `#9370db` |
| V | Museum Wing | World Artifacts | `#2f4f4f` | `#708090` |
| VI | Tech Manor | Modern Antiquity | `#1a1a2e` | `#4a90e2` |
| VII | Armory Corridor | Knights Legacy | `#36454f` | `#c0c0c0` |
| VIII | Art Gallery | Masters Collection | `#800020` | `#b8860b` |
| IX | Treasure Vault | Jeweled Paradise | `#0f0f1e` | `#ffd700` |

*(The later whimsical-princess + outdoor-worlds art direction reskinned these into fairytale rooms and 3D outdoor worlds; the palette/theme spine held.)*

**Vocabulary evolution** — every borrowed term replaced with music-native language:

| Generic / borrowed | Became |
|---|---|
| resource meter | **RESONANCE** |
| collectibles | **Grace Notes** (eighth-notes) |
| melee attack | **Mic Strike** |
| projectile (costed) | **Sound Wave** (frequency rings, spends Resonance) |
| projectile (free) | **Throw Note** |
| block | **Hold Note** |
| health pickup | **DEVOTION** ♥ |
| resource refill | **FULL VOICE** ♪ |
| damage buff | **BELT IT OUT** ♫ (double damage) |
| shield | **HIGH NOTE** ♬ (shield bubble) |

**The art escalation.** Round 1 flat blobs (rejected) → Round 2 eleven hand-drawn themed creatures ("a kid drew them") → Round 3 a real painterly toolkit (`volume`, `wash`, `granulate`, `castShadow`, `rimLight`, `paintWing`, `softGlow`) + muscular anatomy, plus `drawMansionBG()` (parallax interior: bookshelves, gold-framed paintings, chandelier pools, parquet). **The honest limit** became a project principle: *hand-drawn canvas can't reach a rendered sprite — a medium ceiling, not an effort gap. The only path to matching quality is the render pipeline* — which drove the later Blender/AutoSprite hand-off.

**The Phaser 3 pivot + traversability.** Per-frame full-screen repainting was architecturally sluggish → a Phaser 3 + Vite scaffold (GPU-batched sprites, arcade physics; `DISPLAY_SCALE 0.62`, body `42×96`, `RUN 320`, `JUMP -720`) was built and headless-verified, then **parked** (single-file shipped faster). A Stage-2 soft-lock drove a **Python BFS reachability simulator** — all nine layouts rewritten to jump-reach rules and proven pathable spawn→gate. Mobile made first-class (74 px JUMP, thumb clusters, landscape media query).

## Phase 2 — Dual modes (Jul 2 – Jul 13)

The build became **two games in one file**: a textured **behind-the-back 3D Runner** (turns, pursuing chaser, power-ups, coin tiers, gems & revive, objectives multiplier) and a **free-control side-scroll Action RPG**, sharing a 2.5D component-built asset kit and a **fully synthesized in-browser audio engine** (no audio files) with the signature **"death blooms into music"** effect. Leaderboard, achievements, and smooth stage crossfades landed here.

## Phase 3 — Art & asset pipeline (Jul 14 – Jul 19)

**Full 3D texture overhaul** (Cycles stage tiles + 9 corridor backgrounds); the chaser became the rigged **3D Groom's Shadow**; Jandé's run/jump/slide were rebuilt on an armature-driven natural gait (the run had been animating one leg). **Whimsical-princess art direction** — pastel rooms, sans-serif UI, fairies/sparkles/birds; generative score shifted to major keys. **Real outdoor worlds** (GL world renderer) replaced corridor walls. **AutoSprite pipeline** established (key/normalize/embed). Level & XP tracking; chapter-progress track with a crown on the current stage.

## Phase 4 — Controls, HUD & UX (Jul 19 – Jul 21)

Game-feel pack (hitstop, near-miss bonus, instant retry); gamification backlog closed (adaptive difficulty, pity gem, daily streak, **The Boutique**); **full de-emoji sweep** (13 baked pixel icons + pixel arrows; house rule: no stock glyphs as UI); Storybook display font + two-tier type; intro cutscene removed; HUD cleanup; mode rename to **ACTION RPG / ROYAL RUNNER**; **global leaderboard** shipped on a deployed **Cloudflare Worker**; embedded Poppins wordmark; `PRODBYKCTW` footer.

## Phase 5 — Client polish (Jul 21 – Jul 23)

Runner sun/banner-ghost fixes; décor moved out of running lanes; **checkpoint rework** (paid CONTINUE vs free RESTART; removed tap-anywhere-to-jump); RPG **Comfort Split** controls → centered triangle; retired the out-of-place Egyptian ankh; **ledge-aware ground foes** (flyers exempt); killed the wall-band seam via mirror-tiling; library Runner obstacle → a reading table.

## Phase 6 — The RPG overhaul & Silksong reskin (Jul 23, *delivered as patches*)

Boss fights **restored** from orphaned dead code (gate → sealed arena → defeat advances); theme-tight `STAGE_RECIPE` per-stage layouts + escalating foe roster; progressive difficulty; a settings menu (difficulty/audio/reduce-motion/haptics); and the **Silksong combat reskin** — instant-decel vector movement, aerial **Downbeat** pogo, universal attack blowback, and **RESONANCE** as a dual-spend voice meter (**Refrain** heal / **Belt** magic strike). These were built and Playwright-tested on branches and **handed off as clean git patches** for the deploy machine to integrate — which is where Era IV picks up.

---

# ERA IV — THE LIVING BOSSES (Jul 23 – 25, 2026) · [BOSS OVERHAUL]

*Run in Claude Code (Opus 4.8) on the deploy machine. This era integrated every handed-off patch **and** built the game's biggest content addition to date: nine distinct, animated, behaviourally-unique stage bosses — plus persistence, sizing, and end-of-level structure the RPG had never had.*

## IV.0 · Environment & guardrails

- **Two branches:** the dev branch `claude/hand-painted-architecture-bg-*` and a deploy-only orphan `gh-pages`. Deploys run **only** through `tools/deploy.sh` — an orphan force-push that ships game-only files and **hard-aborts if any sensitive file is staged**.
- **Assets are externalized.** Inline base64 was refactored to content-addressed files `web/<sha1[:12]>.<ext>`, referenced as `img.src="web/…"`. The refactor was proven **1:1 lossless** by content-hash comparison against the inline parent (77 assets in → 77 out).
- **Original characters only.** Prince and Jandé are original characters; real photos of Jandé are never committed to the public repo (`assets/` is gitignored).

## IV.1 · Environment & décor polish (opening of the session)

- **Grass** made less dense (~40% thinned), shorter, with per-stage tint/recolor (`GTINT`); the "green-with-pink-blob" bush fixed; a full prop/asset audit.
- **Landscaping** — formal, castle-appropriate avenues (symmetric matched pairs, monument/planter rows) instead of scattered props.
- **Grid-lines killed** in the grass/ground via a domain-warp in the ground shader (`FS_T`), so tiling reads organic.
- **Stage-specific roll-under obstacles** — the library's is now a **table with books on top** (not a giant book stack to jump); globes sit on tables; library plants thinned; the nonsensical **grazing library bunny removed**.
- **Warped plant pots** fixed — the "cross-quad" second billboard was doubling rigid pot bases; the cross-plane was gated to trees only.
- Removed the **orphaned `CORRIDOR_BG` structure** (old overridden backdrop system + its 9 jpegs) so crash/load states present a clean stage-fog backdrop, and audited that all assets are present.
- **HARD difficulty** now removes helper affordances — the glowing slide-cue arrow/chevron is suppressed on Hard.
- **Heart mechanic** — DEVOTION refills open heart slots first, then banks capped extra lives (bonus hearts styled distinctly in the HUD).
- **Boss distance corrected** — `stageEnd` restored to the original `330` (bosses had been appearing far too soon at `108`); you now fight through the stage, then beat the boss to proceed.

## IV.2 · Integrating the handed-off patches

Applied via `git am --3way` (each dry-run-clean before applying), then validated and deployed:

- **rpg_changes / rpg_phase2 / rpg_phase34 / rpg_combat_resonance** — the Phase-6 boss + STAGE_RECIPE + difficulty + Silksong-combat set.
- **Shadow of the Groom** — during any boss (`GS.bossActive`) the fairytale curdles: the arena dims + desaturates, shadow-fog drifts, an ominous red backlight glows, a heavy vignette closes; eased in/out via `GS.bossMood`, dark wash behind the fighters + vignette on top so both stay readable.
- **The Wanderer's Map** — each stage hides a **cache** (Grace Notes + a heart) on a high ledge; its location stays secret until you find that stage's **map fragment**, which lights a ✦ beacon and persists per stage (`jande_maps`).
- **Vivid power-ups** — every pickup now carries a rotating segmented aura ring, orbiting sparks, and a floating **name label** (DEVOTION / FULL VOICE / BELT·2× / HIGH NOTE), colour-coded.
- **The Wanderer's Atlas** — a Boutique row (400 Grace Notes) that unlocks every stage's map at once; also fixed the Boutique being invisible at mode-select (moved `#shopScr` out of `#gameWrap`).

## IV.3 · Nine unique bosses — the headline

The RPG's single REVENANT/HEARTBREAKER pair became **nine distinct villains, one per stage** (atlas row = stage index). **The Groom Who Lied** — the story's true antagonist — is the stage-9 finale.

| Stage | Boss | Signature motif |
|---|---|---|
| I | **Ink Warden** | drifting torn pages, ink motes |
| II | **Thistle Ogre** | ground brute, kicked-up dust |
| III | **Blossom Revenant** | *floats* — a wraith's veil of orbiting petals |
| IV | **Thorn Queen** | rose-and-thorn motes coiling |
| V | **Lake Wraith** | *airborne vertical serpentine slither*, water-bead trail |
| VI | **Toadstool Warlock** | low fog bank + rising spores |
| VII | **Scarecrow King** | wheeling crows, scattering straw |
| VIII | **Storm Titan** | churning cloud, wind-charges + strobing lightning |
| IX | **The Groom Who Lied** | dark embers — the finale |

**Generation.** Each boss was created in **AutoSprite** (`create_character`, pro tier). For every boss, two animations were generated (`generate_spritesheet`, turbo): a **4-frame idle** and a **5-frame defeat/collapse** — 18 clips in two batches, polled to completion.

**The atlas.** `tools/compose_bosses.py` downloads all 18 signed sheets, keys the flat backdrop transparent (border flood-fill), bbox-crops, and fits each frame feet-anchored into a **200×280 cell**, assembling a **9-row × 9-column** atlas: **cols 0–3 = idle cycle, cols 4–8 = defeat**. Output is a content-addressed `web/<sha1>.webp`; the `TEX.boss` reference is swapped and the old atlas deleted, keeping the web-ref audit clean.

**`drawBoss` rewrite.** Row = `b.bi` (stage). During the fight it cycles the idle frames; on death it plays the defeat columns off `GS.bossDeadT` (`GS.bossDeadMax=90`) with a fade-out. The boss is drawn at `b.H*1.95` (larger, so the painted detail reads). Per-boss names drive the **"BOSS AHEAD"** toast and the health-bar label via a `BOSS_NAME` table.

## IV.4 · Signature behaviour — movement + atmosphere per boss

Bosses no longer share one look *or* one motion:

- **`drawBossAura(b,x,y,A)`** — cheap procedural, world-space, per boss: Ink Warden's drifting pages, Thistle's dust, Blossom's orbiting petal veil, Thorn Queen's coiling rose-thorn motes, Lake Wraith's head-to-tail water trail, Toadstool's fog bank + rising spores, Scarecrow's wheeling crows, Storm Titan's cloud haze + strobing lightning bolt, the Groom's rising dark embers.
- **Movement profiles** — airborne bosses (`b.float` = Blossom + Lake) hover with a **vertical serpentine slither** and use a new `DRIFT` attack pattern instead of ground JUMP/SLAM; the **Lake Wraith** slithers hardest (large amplitude, sway coupled into horizontal glide); the **Storm Titan** wind-charges more often; ground bosses keep JUMP/SLAM. Layered on top of the existing WAIT/CHASE/SHOOT/CHARGE/RAGE state machine so combat is unchanged.

## IV.5 · Defeat animations — and the Lake Wraith arc

Every boss now dies **in theme** — Ink scatters into pages, Blossom dissolves to petals, the Toadstool's cap topples, the Groom crumples to his knees under dark fire. Two client-directed iterations shaped the Lake Wraith specifically:

1. The first idle came out **humanoid** while the defeat rendered as an S-shaped water serpent. Reading the client's "but ok" as disappointment, the boss was proactively regenerated as a full serpent — which the client corrected: *"NO HE CAN BE HUMANOID… ASK BEFORE YOU ACT."* The serpent was discarded; the humanoid kept. **(This produced a standing working principle: propose aesthetic changes, don't self-originate them.)**
2. The client then gave an explicit direction: *"HE CAN HAVE A TRANSFORMATION. HIS DEFEAT HE VIOLENTLY BECOMES A PUDDLE OF WATER."* His defeat was regenerated so the humanoid figure bursts and melts straight down into a spreading, rippling **water puddle**; only row 4's defeat frames were recomposed, idle untouched.

## IV.6 · Larger, per-type sprites — "let me see the detail"

The foe atlas cells are **136×152** but were being drawn at a flat **76×84** (~56%, throwing away detail). Draw sizes are now **per-type and near-native**, so the hand-painted work reads: Bramble Knight/brute **≈138** (essentially full size), Rose Wraith elite **≈124**, goblin **≈112**, raven/sprite **≈100**, Wisp Swarm flyer **≈88** — all anchored to the same 52×58 collider so they stay planted. Bosses were bumped to `b.H*1.95` for the same reason. (Enemies had already been raised 61→76 earlier in the session; this is the per-type pass.)

New enemy archetypes wired earlier in the session: **tp3 Bramble Knight** (ground brute), **tp4 Wisp Swarm** (erratic flyer), **tp5 Rose Wraith** (homing elite), keyed into the STAGE_RECIPE rosters. Three new hero poses were also generated from Jandé's **original AutoSprite character** and wired to the combat states: **Refrain** (sing-to-heal), **Belt** (full-voice strike), **Downstrike** (aerial pogo), replacing the reused dance/attack frames.

## IV.7 · Persistent stages — backtracking

`pruneTrack` no longer culls behind the camera **within a stage**. The floor never vanishes when you walk back; uncollected **Grace Notes and power-ups persist** so you can return for a missed pickup or the hidden cache; only defeated foes are dropped. A stage is bounded (~330 cols + arena) and `initGS()` resets between stages, so keeping it all is free. This directly answered *"power-ups shouldn't disappear when I pass by them"* and *"the floor shouldn't disappear if I go backwards."*

## IV.8 · The end-of-level sequence

Beating a stage boss **no longer auto-loads the next stage**. The flow is now: boss defeat animation plays → **Jandé holds the cleared stage and dances (~1.6 s emote)** → a **STAGE CLEAR** results overlay rises with the tally — score, Grace Notes, distance, Resonance level, trophies unlocked, objectives multiplier + bank — a **leaderboard name/score save**, and a **PROCEED TO STAGE N ▶** button. Implemented by reusing `#overlay` via a `GS.ovMode='clear'` flag so the primary button proceeds instead of continuing. Each cleared stage is remembered (`jande_clears`).

## IV.9 · Stage select

Once you've beaten at least one stage, a **⚑ STAGE SELECT** entry appears on the mode screen: start a fresh run from **any stage whose boss you've beaten** (beaten stages show a green ✓; unbeaten are locked). `START_STAGE` flows through `begin()` and the restart handlers; returning to the main menu resets it. *(Runtime-verified end-to-end: seeding three clears surfaced I–III unlocked with ✓, IV–IX locked, and picking a beaten stage routes cleanly into the how-to → start flow.)*

## IV.10 · Verification & the honest limit

Standard for every edit: extract the two `<script>` blocks and `node --check` them; audit that the set of `web/…` references exactly equals the files on disk (no missing, no orphans); load the game over a local static server in the in-app browser and confirm **zero console errors** through boot, RPG start, terrain streaming, and combat input; capture the live frame via `canvas.toDataURL()` when the screenshot compositor is unavailable.

**The limit, stated plainly:** when the preview pane is hidden, `requestAnimationFrame` throttles, so the game loop effectively pauses — the hero can't be driven all the way to a boss headlessly. The boss-defeat overlay and live backtracking (both inside the RAF loop) were therefore verified by code review + JS validity + zero init-time errors, while the stage-select and all synchronous new code (cache/map seeding, definitions) were verified live. This is the same environment limit noted throughout the project's headless work.

---

# THE SHIPPED PRODUCT — July 25, 2026

Both modes ship in one file, share the **Grace Notes** economy and the global leaderboard, and each carries nine themed stages.

## Mode 01 — Action RPG (side-scroll)
Run the enchanted halls, fight through an escalating foe roster, and **beat the stage's unique boss to advance**.
- Instant-decel movement, **Mic Strike** with blowback, **Downbeat** pogo, dash, double jump
- **RESONANCE**: sing a **Refrain** to heal, or **Belt** a full-voice magic wave
- **Nine unique bosses**, each with an idle, a themed defeat animation, signature VFX and movement (floaters, a vertical serpent, a storm titan) — under **Shadow of the Groom** atmosphere; enrage phase + health bar; **The Groom Who Lied** is the finale
- **Persistent stages** — backtrack for missed notes, power-ups, and the hidden cache
- **The Wanderer's Map** — hidden caches found on the path or bought as **The Wanderer's Atlas** in the Boutique
- **STAGE CLEAR** end-of-level tally (score/notes/trophies + name save + Proceed)
- **Stage Select** — start from any stage you've beaten

## Mode 02 — Royal Runner (behind-the-back)
A WebGL "temple run" through nine real-time 3D worlds.
- Turns, a pursuing 3D Groom's-Shadow chaser, slide/jump obstacles, coin tiers
- Power-ups: Note Magnet, Crescendo Boost, ×2 Score, gems & revive
- Per-stage 3D worlds with grass, wind, animated water, landscaped shoulders
- An objectives multiplier feeding the shared score and leaderboard

## UI flow
Title → Queen's Registry (email capture) → Story framing → Mode Select (+ **Stage Select**) → Per-mode instructions → Gameplay → Stage cards → **Boss fights → STAGE CLEAR tally / Proceed** → Reunion ending → Game over (name entry + SAVE / CONTINUE / RESTART / MAIN MENU) → Pause → Settings → The Boutique.

## Architecture
One client-side page — Canvas2D RPG + hand-written WebGL Runner + synthesized audio, **external hashed assets** (`web/<sha1>.<ext>`), deployed to GitHub Pages via an orphan `gh-pages` branch through a guarded `tools/deploy.sh`. The only runtime network call is the **Cloudflare Worker** leaderboard (graceful local-top-10 fallback). PWA: `apple-mobile-web-app-capable`, app title "Jandé", theme `#1a0a2e`.

---

# THE COMPLETE BUG LOG

| # | Era | Symptom | Root cause | Fix |
|---|---|---|---|---|
| 1 | III | Every button dead | `DOMContentLoaded` timing — handler never fired | Immediately-invoked `wire()` |
| 2 | III | Blank after death → retry | State reset but render loop never restarted | `if(!running){running=true;loop();}` |
| 3 | III | Black screen after BEGIN | `startGame()` activated a full-screen overlay over the canvas | Hide all `.screen` overlays instead |
| 4 | III | Intro video black | WebGL rebuild dropped the video element + `playIntro` | Recompress, re-embed, rewire |
| 5 | III | Intro still black for client | Stale cached copy | Hard-refresh; file size as version check |
| 6 | III | Player trapped on Stage 2 | Platforms out of jump range | All 9 layouts rewritten + BFS-proven |
| 7 | III | Painted mansion pure black | WebGL produced no output | Move interior to Canvas2D |
| 8 | III | Wrong README | "luber app" README copied in | Rewritten with Jandé content |
| 9 | III | Enemies looked like blobs | Flat shapes, no shading | Painterly toolkit + anatomy |
| 10 | III | Build sluggish | Per-frame full-screen repaint | Pivot to Phaser 3 |
| 11 | III | Boss fights never triggered | Boss system orphaned as dead code | Rewired: gate → arena → advance |
| 12 | III | Runner décor blocking lanes | Scenery in the lanes | Moved to organic shoulders |
| 13 | III | Scrolling seam | Tiling discontinuity | Mirror-tiling |
| 14 | III | Enemies walking off ledges | No edge detection | Ledge-aware logic |
| 15 | IV | **Real Jandé photos pushed to public `gh-pages`** | A `git add -A` on the deploy branch staged gitignored `assets/` | Full **orphan-branch purge + force-push**; created guarded `tools/deploy.sh` (game-only, aborts on sensitive files) |
| 16 | IV | Painted obstacles never rendered | Duplicate `TEXDATA` obstacle keys (JS last-wins) | Deduplicated the keys |
| 17 | IV | Plant pots warped/misshapen | Cross-quad billboard doubled the rigid pot base | Gated the cross-plane to trees only |
| 18 | IV | Bosses appeared far too soon | `stageEnd=108` | Restored to `330` (fight through, then the boss) |
| 19 | IV | A bunny grazing in the library | Nonsensical prop placement | Removed it from the library prop set |
| 20 | IV | Can't drive to a boss headlessly | RAF throttles when the preview pane is hidden | Documented limit; verify RAF-gated paths by review + synchronous-path testing |

---

# ASSET INVENTORY & PIPELINE

**Reference material** (22 project files): Jandé Instagram photos (IMG_1392/1373/1386/1389 — outfit, casual, gown/performance, stage lighting); Silksong references (IMG_1369–1391 — sprite sheets, Hornet, NPC galleries, figurines); Gemini chibi outputs (4); client sprite sheets (IMG_1657 "Jandé The Singer", IMG_1656 "Agent Elara").

**Character/boss pipeline — AutoSprite.** `create_character` (pro) → `generate_spritesheet` (idle/walk/attack/custom, turbo) → poll → download signed sheet → key/bbox/fit/feet-anchor → compose into the target atlas (foes 136×152; bosses 200×280, 9×9 idle+defeat) → content-addressed `web/<sha1>.webp` → swap ref → delete old → web-ref audit. Baker scripts: `compose_bosses.py`, `append_enemies.py`, `append_hero_anims.py`, plus the environment/obstacle/prop composers.

**Environment pipeline — Blender/Cycles.** Stage tiles, corridor backgrounds, whimsy panels/floors/props, the 3D Groom's Shadow chaser, the rigged Jandé run/jump/slide, and 9 side-elevation backdrops.

**Storage.** Everything inline was externalized to hashed `web/` files; the build references them by path, keeping the HTML lean and the assets cacheable/deduplicated.

---

# ENGINE EVOLUTION

| # | Engine | Era | Why chosen | Why left |
|---|---|---|---|---|
| 1 | Canvas2D (vanilla) | I, III | Zero-dep, single-file, offline, instant iteration | Per-frame full-screen repaint sluggish |
| 2 | WebGL (hand-written) | III | GPU backgrounds, lighting, depth | Black-screen bugs; parallax heavy on phones |
| 3 | Phaser 3 + Vite | III | GPU-batched sprites, arcade physics | Parked — single-file shipped faster |
| 4 | Godot 4.6.2 | II | Multi-platform export, GDScript | Parked — long-term native engine |
| 5 | **Canvas2D + hand-written WebGL (hybrid)** | III–IV | Reliable Canvas2D RPG + custom WebGL Runner + synth audio, one self-contained page | **Currently shipping** |

---

# VERIFICATION METHODOLOGY

| Technique | Applied to |
|---|---|
| `node --check` / `new Function(src)` on extracted `<script>` blocks | Every HTML edit, before shipping |
| Puppeteer/Playwright headless (`--use-gl=swiftshader`) | Boot, intro, movement, combat, boss flow, settings, map, shop |
| Canvas pixel sampling / `canvas.toDataURL()` capture | Proving renders aren't black; live-frame proof when the compositor is unavailable |
| Python BFS reachability | All 9 stage layouts — anti-trap proof |
| Web-ref audit (refs set == files set) | Every asset externalization / atlas swap |
| In-app browser smoke test over a local static server | Zero-console-error boot, RPG start, stage-select flow |
| **Known limit** | RAF throttles while the preview pane is hidden — RAF-gated paths verified by review + synchronous testing |

---

# WORKING PRINCIPLES

1. **Prove it by running it** — execution catches black screens, dead code, and orphaned systems that syntax checks miss.
2. **Never let the player get stuck** — traversability is machine-verified; enemies falling in pits count as kills.
3. **Art quality has a medium ceiling** — when the bar is photoreal, use the render pipeline, not more code.
4. **Pivot when the architecture is the problem** — Canvas→Phaser and single-file→external assets were architecture calls.
5. **Reskin, don't copy** — Silksong-class mechanics, re-expressed entirely as Jandé's voice; the word "Silksong" is scrubbed to zero in shipped text.
6. **Ship one file the client can just open** — self-contained, offline, shareable, with a hosted URL on top.
7. **Cache is a real bug class** — version-check by file size.
8. **Identity preservation is non-negotiable** — the chibi-watercolor sheets are canonical; Prince and Jandé stay original characters.
9. **Guard the deploy** — never `git add -A` on the public branch; deploy only through the guarded script; real photos never touch the public repo.
10. **Ask before self-originating aesthetic changes** *(new, Era IV)* — a client's mild "but ok" is not a mandate; explicit patches/instructions = act, self-originated design changes = propose and wait.

---

# OPEN THREADS

## Newly closed in Era IV
Silksong feature set (**applied + deployed**) · Shadow of the Groom, Wanderer's Map, Wanderer's Atlas, vivid power-ups (**live**) · new enemy archetypes + Refrain/Belt/Downstrike hero poses (**wired**) · 9 unique bosses + defeat animations (**live**) · larger per-type sprites (**live**) · persistent stages, STAGE CLEAR sequence, Stage Select (**live**).

# ERA V — SIDEWAYS, SCORED & PAINTED (Jul 25–26, 2026) · [CLOUD + LAPTOP]
Client play-tested on device (iPhone/Safari) and reported the game looked broken
sideways. Root-caused to **one recurring mistake**: quantities that should scale
with the world or the hero were pinned to raw screen dimensions, which portrait
hid because `W < H`. All four shipped and are live:

- **Décor detached from the floor** — the backdrop drew in screen space while the
  world drew scaled by `ZOOM`; `groundY` lacked `* ZOOM`, so props sat buried and
  drifted on every jump. Fixed in two passes: the scale, then removing the
  leftover `Math.min(H*0.82, …)` clamp that pinned the baseline the instant the
  camera rose (landscape had 4px of headroom, so any jump tripped it).
- **Runner hazards ballooned** — obstacles sized off viewport WIDTH while the hero
  was sized off HEIGHT, making an arch 0.40× her height in portrait but 1.30× in
  landscape. Now height-derived and orientation-independent.
- **Backdrop seams** — painted backdrop tiled at fractional x/width; adopted the
  wall band's shared-integer-edge snap.
- **Ground slab** consuming ~40% of a landscape screen; blank untextured
  platforms; title seam; register/how-to/overlay clipping; the PRODBYKCTW footer
  now flows with content instead of floating over it.

**RPG end-of-stage SCORED TALLY** replaced the cumulative "THIS RUN SO FAR"
readout with a real arcade rank-out: per-stage TIME against par, Grace Notes,
foes, damage and a TOTAL. Par times derived from the stage constants
(`stageEnd=330`, `T=32`, run 6.4px/frame, boss HP `7+ai*2`) rather than guessed —
`STAGE_PAR=[70,70,80,90,95,100,105,115,120]` with `PAR_DIFF` scaling, because boss
HP already scales ×1.4 on Hard and a Normal clock would make Hard unbeatable.

**Documentation audit.** `CLAUDE.md` still described the parked Phaser 3 scaffold
and told sessions not to hand-roll a render loop (the shipped game *is* one);
`HANDOFF.md` still taught the `git add -A` deploy recipe that had leaked the
client's real photos; six finished tasks were still marked ACTIVE, two of which
were re-reported as bugs *because the docs said so*. All corrected, and the
client made doc-updating a binding standing rule.

**Still open from Era V:** the stock-glyph sweep (47 sites — a regression; the
July 21 baked-icon system is no longer in the build and new UI reintroduced raw
Unicode that iOS renders as Apple emoji), the overlay content clipping, and a
pre-deploy gate to stop the glyph rule regressing a third time.

### Era V continued — pre-game layout + boss score (Jul 26, cloud session)
- **Landscape was unstartable.** `body` is `overflow:hidden` and only the how-to
  screen and results overlay ever received `overflow-y`, so once content passed the
  bottom of a short viewport it was unreachable - BEGIN, ENTER THE KINGDOM and the
  mode cards could not be tapped. Every `.screen` now scrolls.
- **Content was pinned to the top**: the footer's `margin-top:auto` absorbed all
  free space before `justify-content:center` could distribute any. Giving the
  content blocks their own `margin-top:auto` makes the two split it.
- **Wordmark sized off the wrong axis** - `16vw` was 7.4% of a portrait viewport but
  32.6% of a landscape one. Capped with `min(16vw,20vh)`. Third instance of this
  class of bug, after the runner hazards and the decor baseline.
- **Ink Warden projectile was invisible, not thin** — drawn as a near-black rect
  (`BOSS_GORE[0]`) with a near-black glow on the dark library backdrop. Now cream
  paper with dark ink, torn edge, tumbling. Painted AutoSprite replacements for
  all nine projectiles specced in `docs/PROJECTILE_ART_BRIEF.md`.
- **Painted boss projectiles shipped end-to-end from the cloud** — first use of
  AutoSprite from a cloud session (network policy opened + MCP-over-HTTP with a
  Bearer key). Nine painted pieces, one per boss's matter, composed into a 9x96
  atlas (`TEXDATA.proj`); canvas primitives retained as the load fallback.
- **Boss music** now darkens on the same eased `GS.bossMood` curve as the Shadow of
  the Groom visuals; the mechanism existed in `musTick` but its `danger` flag was
  wired only to the runner's chaser, so RPG bosses had no musical change at all.

- **Glyph sweep finished and locked (52 → 0).** The last 10 sites became made
  assets: a drawn eighth-note (runner coins + death bloom), drawn map-legend
  markers, CSS pips and a CSS cleared-tick, and words for gems/notes. A glyph
  gate (`tools/glyph_gate.py`) now runs inside `deploy.sh` and fails any deploy
  shipping symbol/emoji characters — after regressing twice, the rule is enforced.
- **Overlay clipping** closed by the laptop's sticky `.ov-btns` action row.

### Era V close-out (Jul 26, cloud session)
- **Glyph sweep finished: 52 → 0** (38 laptop + 14 cloud). The final sites became
  made assets — a drawn eighth-note for runner coins and the death-bloom, drawn
  map-legend markers, CSS pips and cleared-tick. **`tools/glyph_gate.py` now runs
  inside `deploy.sh`** and fails any deploy shipping symbol/emoji characters.
- **First cloud-generated art:** with the environment network policy opened and a
  Bearer key, the cloud session drove AutoSprite's MCP endpoint directly and
  shipped the nine painted boss projectiles end-to-end (generate → best-of-4 →
  semantic background removal → 9x96 atlas → `TEXDATA.proj` → deploy). The art
  pipeline no longer requires the laptop.
- **Boss music** darkens on the eased `GS.bossMood` curve (minor third, drone,
  harder pulse, enrage peak riding the real `boss.enraged` flag).
- Overlay actions made always-reachable via the laptop's sticky `.ov-btns`.

- **Runner décor scale unified (client-reported from the record PDF):** prop
  billboard heights were a fixed 560px base while the hero scales with viewport
  height — a topiary stood ~4x Jandé on a landscape phone. The base is now
  H-anchored (identical at the tuned portrait reference) and the indoor
  pot/globe/topiary set was cut to human scale. Outdoor trees still tower, as
  designed. Fifth and final instance of the screen-vs-world sizing bug class.

## Still open
| Item | Status | Note |
|---|---|---|
| **Rotate the Cloudflare API token** | OPEN | Client action |
| **Rotate the AutoSprite API key** | OPEN | Client action — key was shared in chat for the projectile pass |
| Landscape controls on device | RESOLVED 07-26 | Client's own screenshots confirm the cluster fits; pre-game screens fixed & scrollable |
| Combat & economy tuning | OPEN | Play-test dials — par times, beacon range, Atlas price, Refrain speed, Belt range |
| Stage-Select starting stats | OPEN (design) | Late stages begin at LV1 stats; option to grant stage-scaled stats on request |
| Lake Wraith idle form | RESOLVED per client | Humanoid idle kept; violent puddle-transformation defeat shipped |
| EmailJS credentials | OPEN | Placeholders unfilled; signups fall back to `localStorage` |
| `dance` animation | RESOLVED | Now bound to the STAGE CLEAR victory emote |
| Dress → tuxedo swap | OPEN | Story beat ~stage 3; needs a tuxedo sheet |
| Actual song lyrics | OPEN | Client to supply; only short fragments used |
| Phaser scaffold / Godot project | PARKED | Preserved migration/native targets |

---

# TIMELINE AT A GLANCE

```
MAY 2026
├── ~early    Session 1: 8-bit princess → Silksong pivot → Jandé redesign → single HTML file
├── May 12–13 Session 2: Ghibli-chibi identity lock-in (tool ranking, forensic prompt, Gemini outputs)
├── May 12–13 Session 3: Godot 4.6.2 build — GDD, Art Style Bible, controller, starter project, Veilmere narrative
└── May 14    Session 4: project bible — original IP vocabulary, 14-day vertical slice

JUNE 2026
├── Jun 4     Production begins — Canvas2D rebuild
└── Jun 4–25  Phase 1: 2.5D WebGL engine, sprite pipeline, intro, 9 stages, vocabulary, painterly toolkit,
              mansion parallax, Phaser scaffold, BFS traversability, mobile

JULY 2026
├── Jul 2–13  Phase 2: Temple Run mode, dual-mode game, 3D runner, RPG conversion, synth audio
├── Jul 14–19 Phase 3: 3D texture overhaul, rigged Jandé, whimsical direction, outdoor worlds, AutoSprite, XP
├── Jul 19–21 Phase 4: game feel, gamification, de-emoji, typography, leaderboard + Cloudflare Worker, rename
├── Jul 21–23 Phase 5: client polish — checkpoint rework, comfort controls, ledge-aware foes, mirror-tiling
├── Jul 23    Phase 6: RPG overhaul + Silksong reskin (delivered as patches)
│
└── Jul 23–25 ERA IV — THE LIVING BOSSES (this session):
              décor/landscaping polish · grid-line + warped-pot fixes · library table obstacle · bunny removed
              · integrated all handed-off patches (combat, Shadow of the Groom, Wanderer's Map + Atlas, vivid pickups)
              · 9 UNIQUE BOSSES (AutoSprite) — idle + themed defeat animations, 9×9 atlas, drawBoss rewrite
              · per-boss VFX (drawBossAura) + movement (float/serpentine/wind) + boss names in toast/bar
              · Lake Wraith: humanoid idle → violent water-puddle transformation defeat
              · larger per-type enemy/boss sprites (show the detail) · new foe archetypes + Refrain/Belt/Downstrike
              · persistent stages (backtrack) · STAGE CLEAR end-of-level tally + Proceed · Stage Select
              · asset externalization + guarded gh-pages deploy (+ real-photo leak purge & remediation)

Jul 26       ERA V — landscape root-caused & fixed (decor/hazard/seams/slab), scored STAGE
             CLEAR tally + derived par times, boss-fight score (bossMood-driven), pre-game
             layout & scroll blocker fixed, glyph sweep 52→0 + deploy gate, nine painted
             AutoSprite projectiles generated FROM THE CLOUD, docs made current same-day

Jul 25/26    THIS DOCUMENT — complete record assembled; live build confirmed deployed and functional
```

---

*Jandé — "Once Upon A Time"*
*Complete development record · PRODBYKCTW · assembled July 25, updated July 26, 2026*
*Consolidates the CHANGELOG, the Development History & Technical Record, the Ultimate Development Record, and the PRODBYKCTW Build Assessment — and adds Era IV: The Living Bosses.*
