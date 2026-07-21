# Cloud Session — Work Log (share with the laptop session)

Everything below is **committed to `claude/hand-painted-architecture-bg-0MAiy`** and
**deployed to `gh-pages`** (live), unless marked *in progress*. Dev and gh-pages are in sync.

## Pre-game / branding
- **Intro cutscene removed + archived** → `archive/intro/` (mp4 + markup + JS + restore README). `#tPress` now goes straight to the register screen. A new intro is TBD.
- **Two-tier type system** (after client called all-Storyboo "AI slop"): Storyboo = display headings only; `var(--body)` (storybook serif) = all body/UI text. Then reskinned the pre-game screens to a **tavern/storybook theme** (carved gold-plaque buttons `.btn-tav`, aged-wood panels, cream serif).
- **JANDÉ wordmark = real Poppins** — embedded an 864-byte Poppins-Black subset (only the letters J A N D É) as `@font-face 'PoppinsJande'`. Self-contained, no web-font request. Everything else stays Storyboo.
- Title: removed the "veil for the spotlight" tagline; enlarged "ONCE UPON A TIME".
- **Footer `PRODBYKCTW`** → links to instagram.com/prodbykctw, on title / register / how-to (NOT the mode screen — it collided with the Boutique CTA there).
- Per-mode **instructions now come AFTER mode select** (login → mode select → mode-specific how-to → game).

## Mode select
- **TEMPLE VIEW renamed → ROYAL RUNNER**; ACTION RPG unchanged.
- **New card icons = her real side-view sprites**: ACTION RPG = a mic-strike **attack** frame; ROYAL RUNNER = a **run** frame. (Icons extracted from `SPRITES.attack` / `SPRITES.run`.)

## Collectibles & lives (whiteboard item ②)
- **Blue music note** = the Grace Note you collect all game (`drawNote`).
- **Heart** = lives → both the top-left life counter AND the earned extra-life pickup on the stage (`drawPwr` DEVOTION).
- Re-baked both as **2.5D thick-turntable spins with black borders + specular glare** (`tools/bake_collectibles.py`) — they never go thin/flat when rotating.
- Lives row: pixel hearts (replaced the balloon-looking SVGs); lost lives dim.

## HUD (whiteboard item ③)
- **Combined the bars Dragon-Ball style**: one tavern-framed status panel top-left stacks lives + RESONANCE + LV.
- **Chapter-progress crown** moved to its own bigger tavern ribbon top-center; score + sound/pause alone top-right (**this also cleared the RESONANCE/LV vs top-buttons overlap** I'd flagged — you also fixed it in `d252b61`, so that's double-covered now).
- Distance meter + power-up chips nudged down to clear the ribbon; mobile portrait tightened so the 3 columns never collide.
- **Stage-title banner** dropped below the HUD band so it never overlaps in landscape.

## Notifications / achievements
- **Achievement + objective pop-ups removed from gameplay** (client: distracting). They're summarized on the **game-over screen** under "— TROPHIES UNLOCKED —", which now grants **+20 Boutique tokens (banked Grace Notes) + 1 gem per trophy**.
- Power-up pickups kept, but as **small top-right corner pills** (was a full-width banner).

## Gameplay / controls
- **RPG landscape controls fix**: switched `html/body/#gameWrap` to `100dvh` (iOS was resolving `height:100%` to the large viewport, hiding the bottom controls) + landscape control cluster now sized by viewport height. All buttons verified on-screen in landscape.
- (Landscape obstacle scale left as-is — client likes it.)

## Background
- **Wall-band seam fixed**: tiles were drawn at fractional x/width → a moving brown seam in the sky while scrolling. Now each tile snaps its left/right edge to a shared integer. Added a ground-line shadow for depth separation.

## ⏳ In progress (LOCAL only — not yet deployed)
- **Royal Runner: runner floats above her shadow.** Her feet sit at ~87.5% of the sprite cell, but the draw plants the cell *bottom* on the ground line → ~12% empty space leaves her hovering. Added a `footPad` offset in the temple hero draw (`drawT`) to plant her feet on the floor; still tuning the exact amount + shadow alignment. **Heads-up: this touches the temple hero-draw block — if you're working there, ping me.**

## Coordination notes
- Branch discipline holds: dev-branch first, gh-pages deploy-only, always `git pull --rebase` before pushing.
- Typography two-tier system: don't put Storyboo back on body copy (see HANDOFF.md).
- `tools/bake_collectibles.py` is the baker for the note/heart sprites.
