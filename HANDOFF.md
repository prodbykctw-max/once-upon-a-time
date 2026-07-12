# HANDOFF — Jandé: Once Upon A Time (continue here)

You are continuing a paid, professional-grade promo game for the R&B artist
**Jandé** (always accented: Jandé / JANDÉ). The client is delivering this to a
label ($5k upfront + $5k on delivery). Quality bar is commercial.

## Ground rules (do not break)
1. The ENTIRE game is one self-contained file: **`index.html`**. No build step,
   no external requests at runtime (all assets are base64-embedded). It must
   stay deployable as a single static file.
2. **Never modify or replace Jandé's original side-view sprite art**
   (`SPRITES.idle/run/jump/attack/dash/block/dance`) — the artist made it.
   Only the `bk*` back-view slots are replaceable.
3. Develop on branch **`claude/hand-painted-architecture-bg-0MAiy`**, deploy by
   copying `index.html` onto **`gh-pages`** and pushing both.
   Live URL: https://prodbykctw-max.github.io/once-upon-a-time/
4. Never commit API keys. The user pastes the AutoSprite key in chat.
5. Mobile is the primary device: keep the fixed-timestep loop, DPR cap, and
   touch-action lockouts intact. Test with Playwright before every deploy.

## What exists (all working, all deployed)
Two selectable modes after the registration screen (`#modeScreen`):
- **ACTION RPG** (side-scroll, `MODE==='side'`): auto-runner + combat.
  Mic Strike (swipe→/X/Z/J), stomp kills, Heartbreak Imp + Cupid Skull foes
  (`TEX.foes`), persistent RPG level in localStorage `jande_rpg`, combos,
  damage pops, coyote time, double jump, slide.
- **TEMPLE VIEW** (`MODE==='temple'`): full Temple Run — 3 lanes, swipe
  up/down/left/right, corner TURNS with arrow gates + camera swing, chaser
  ("The Groom's Shadow", `TEX.chaser`) with stumble-twice-caught rule,
  power-ups (magnet/boost/x2/shield/encore via `TEX.items`), 3 coin tiers,
  gems + RISE AGAIN revive, textured perspective corridor.
Shared systems: 9 themed rooms crossfade every 500m (`themeShift`), toasts,
11 achievements (`ACH`), 10 objectives w/ permanent score multiplier (`MIS`),
top-10 leaderboard (`jande_runs`), gem wallet (`jande_wallet`), death = body
blooms into music notes (`noteBurst`).

## Asset pipeline (the important part)
All art is baked pixel art embedded as base64:
- `TEXDATA` → `TEX` images: `walls` (9 cells, 144x192 each — 2.5D shaded,
  composed from components), `floors` (9 cells 96x96), `decor` (9 props
  144x240), `chaser` (4 frames 176x224), `foes` (6 cells 136x152), `items`
  (8 icons 64x64).
- `SPRITES.bkrun/bkjump/bkslide`: back-view Jandé placeholder (144x208 cells,
  8/4/2 frames) used by Temple View; renderer falls back to side art if a bk
  sheet is missing. Drawn crisp via `imageSmoothingEnabled=false` when the
  sheet name starts with `bk`.
- Generator scripts live in `tools/` (`bake_25d.py` = walls/floors with the
  lighting compositor; `bake_decor.py` = props+foes; `bake_sprite.py` =
  back-view placeholder; `bake_world.py` = chaser/items). Python + Pillow.
  To swap an asset: regenerate PNG → base64 → replace the entry in
  `TEXDATA`/`SPRITES` (python re.sub on the data URI), keep cell dims stable.

## YOUR FIRST JOB: AutoSprite art pipeline
This environment has network access to `www.autosprite.io` (that's why this
session exists). The user's AutoSprite account already contains their original
Jandé character. Auth: `Authorization: Bearer <key from user's chat message>`.
- REST + MCP endpoint: `https://www.autosprite.io/api/mcp` (MCP over HTTP; the
  REST API uses the same key — docs at autosprite.io/docs).
- Useful MCP tools observed: `list_characters`, `get_character`,
  `generate_spritesheet`, `regenerate_single_spritesheet`, `animate_asset`,
  `get_job_status`, `get_spritesheet`, `create_asset`, `remove_asset_background`.
Pipeline to run:
1. `list_characters` → find the Jandé character.
2. Generate BACK-VIEW sheets (character seen from behind, running away from
   camera, transparent background): run cycle 8 frames, jump 4 (crouch/rise/
   peak/fall), slide 2 (low crouch). Any resolution ≥128px per frame.
3. Poll job status, download PNGs, normalize with Pillow into horizontal
   strips with uniform cells (match aspect ~144:208), transparent bg.
4. Swap into `SPRITES.bkrun/bkjump/bkslide` (keep `frames`, update `cw/ch` to
   the new cells — the renderer scales by ch, so any consistent size works).
5. Playwright-test Temple View, screenshot, deploy, show the user.
Then (in priority order, confirm with user between steps):
6. Themed enemy sprites for the Action RPG (replace `TEX.foes`, 3-frame walk +
   3-frame fly minimum; keep or grow cell grid, update the drawImage calls).
7. Boss sheet for "The Groom's Shadow" (replace `TEX.chaser`, 4+ frames).
8. Per-room decor upgrades via AutoSprite if the pixel props need more polish.

## Testing recipe (Playwright, headless Chromium at /opt/pw-browsers/chromium)
Boot flow: goto file:// → click `#tPress` → force-end the `<video>` + dispatch
'ended' → click element containing "play without" → click `#msSide` or
`#msTemple` → wait ~3.2s (level card) → play/screenshot.
For state manipulation append a debug hook before `})();`:
`window._dbg=function(fn){fn(GS);};` — REMOVE IT before committing.
Keyboard: Space jump, ArrowDown slide, X strike, Arrows lanes/turns, P pause.

## Deploy recipe
```
git add -A && git commit -m "..." && git push -u origin claude/hand-painted-architecture-bg-0MAiy
git checkout gh-pages && git checkout claude/hand-painted-architecture-bg-0MAiy -- index.html \
  && git commit -m "Deploy: ..." && git push -u origin gh-pages \
  && git checkout claude/hand-painted-architecture-bg-0MAiy
```
(If gh-pages doesn't exist locally: `git checkout -b gh-pages origin/gh-pages`.)

## Backlog after art (user-approved directions)
- Store: spend banked Grace Notes on power-up duration upgrades (Temple Run's
  last missing system). Wallet + objectives already exist to hang it on.
- Sound design (music-reactive; it's a promo for the song "Once Upon A Time").
- Global online leaderboard (user has a Cloudflare connector — Workers+KV/D1).
- Custom domain + EmailJS keys for the registration form (business polish).
