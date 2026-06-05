# CLAUDE.md — Jandé: Once Upon A Time (Phaser 3)

## What this is
A 2.5D side-scrolling promotional platformer for the R&B artist **Jandé** and her
song *"Once Upon A Time."* The player controls Jandé (a real, photo-referenced
sprite the artist created) through nine themed rooms of a dark painted mansion,
fighting themed creatures and a boss per stage. Goal: fan engagement + email capture.

This project was rebuilt in **Phaser 3** after a single-file HTML/Canvas prototype
became sluggish and buggy. Phaser gives us GPU-batched sprites, arcade physics,
a scene system, and a real asset pipeline — keep using it; do not hand-roll a
render loop or physics again.

## Stack
- **Phaser 3** (game engine, WebGL) + **Vite** (dev server / bundler). ES modules.
- No TypeScript yet (can be added). No other runtime deps.

## Run
```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # outputs to dist/ (static, deploy anywhere — Cloudflare Pages)
```

## Project structure
```
src/
  main.js              Phaser game config (scale, physics, scene list)
  scenes/
    BootScene.js       loads sprite sheets, defines animations, loads level data
    TitleScene.js      branded title screen → Game
    GameScene.js       core playfield: builds level, input, camera, theming
    UIScene.js         parallel HUD + on-screen touch controls
  objects/
    Player.js          Jandé: arcade body + animation state machine + controls
    LevelBuilder.js    per-stage traversable platform layouts (no-trap rules)
  data/
    levels.json        the 9 stage definitions (name, theme, colors)
public/assets/sprites/ processed 256×256 uniform sprite sheets + manifest.json
```

## Sprites (IMPORTANT)
Jandé's seven animations are real rendered art the artist made. They live as
**uniform 256×256-cell horizontal sheets** (one row each) in
`public/assets/sprites/`: `idle, run, jump, attack, dash, block, dance`.
Frame counts are in `manifest.json` and mirrored in `BootScene.SHEETS`.

- The sprite faces RIGHT; left is handled by `setFlipX(true)`.
- Display scale is ~0.62 (≈159px tall on screen); the physics body is a tight
  42×96 box, NOT the whole frame.
- To regenerate sheets (new art), re-run the Python processor that keys out the
  black background, trims, and repacks to 256px cells, then update frame counts.

## Conventions / guardrails
- Keep the artist's name accented everywhere: **Jandé / JANDÉ**.
- Music-themed vocabulary (carried from the prototype, reintroduce as features):
  resource = RESONANCE; collectibles = Grace Notes; melee = Mic Strike;
  projectiles = Sound Wave / Throw Note; block = Hold Note; power-ups =
  DEVOTION (+life), FULL VOICE (refill), BELT IT OUT (2× dmg), HIGH NOTE (shield).
- **Traversability rule for levels:** ground is continuous except defined pits;
  every pit and high ledge must have platforms reachable within ≈4 tiles up /
  ≈5 across. Never create a spot the player can fall into with no way out.
- Mobile matters: touch controls live in `UIScene`; keep them working.
- Self-contained build: `npm run build` must produce a static `dist/` deployable
  to Cloudflare Pages with no server.

## Good next tasks (suggestions)
1. **Enemies**: add an `Enemy` class + a `Creatures` module. Behaviors:
   flyer (sine-wave chase), ranged caster (shoots projectiles), tank (charger).
   Theme the visuals per stage (cupid/fairy/wraith/imp, fallen angel/sorcerer/
   gargoyle, bear/lion/golem/dragon). When the artist provides enemy sprite
   sheets, load them like Jandé's; until then use Phaser graphics/shapes.
2. **Combat**: Mic Strike hitbox on attack frames; Sound Wave / Throw Note
   projectiles; stomp-kill; i-frames.
3. **Boss per stage** behind a gate that opens when ground enemies are cleared.
4. **Collectibles & power-ups** (Grace Notes + the four music power-ups).
5. **Stage flow**: clear → next stage; carry score/level; victory screen.
6. **Email capture**: registration screen before play (reuse EmailJS creds),
   fall back to localStorage when keys are absent.
7. **Intro video**: optional cutscene before registration.

## Notes
- Arcade physics gravity is global (`main.js`). Player jump/dash velocities live
  in `Player.js` constants.
- Stage colors come from `levels.json` (`primaryColor` / `accentColor`) and drive
  both background and platform tinting in `GameScene`/`LevelBuilder`.
