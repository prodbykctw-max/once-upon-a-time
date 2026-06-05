# Jandé — Once Upon A Time 🎤👑

A 2.5D side-scrolling platformer built for the R&B artist **Jandé** and her
song *"Once Upon A Time."* Run through nine themed rooms of a dark painted
mansion as Jandé, fighting mythical creatures and bosses across each stage.

Built for fan engagement and email capture — play the game, follow the queen.

---

## Stack

- **Phaser 3** — game engine (WebGL, sprite-sheet native, arcade physics)
- **Vite** — dev server and bundler
- **Godot 4** — native engine build (in `once-upon-a-time/`)

---

## Quick Start (Phaser / Web version)

```bash
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

**Controls:**
- `← →` Move
- `Space` Jump
- `Z` Attack (Mic Strike)
- `Shift` Dash
- `K` Block (Hold Note)

On mobile, on-screen touch controls appear automatically.

---

## Build & Deploy

```bash
npm run build
```

Produces a static `dist/` folder — deploy directly to **Cloudflare Pages**,
Netlify, or GitHub Pages. No server required.

---

## Project Structure

```
once-upon-a-time/          Godot 4 native project
Jand-spritesheet/          Raw individual animation frames
src/                       Phaser source
  main.js                  Game config
  scenes/                  Boot, Title, Game, UI scenes
  objects/                 Player, LevelBuilder
  data/                    levels.json (9 stage definitions)
public/assets/sprites/     Processed 256x256 Phaser sprite sheets
```

---

## Artist

**Jandé** — R&B/Soul artist, Atlanta GA
Instagram: [@jandelove1](https://instagram.com/jandelove1)
*"Once Upon A Time"* — coming soon.

---

## Built by KCTW
