# Jandé — Once Upon A Time 🎤👑

A promotional browser game built for the R&B artist **Jandé** and her song
*"Once Upon A Time."* Play as Jandé across **nine themed stages** in **two modes** —
an **Action RPG** side-scroll (fight the foe roster and beat each stage's unique
boss) and **Royal Runner**, a behind-the-back 3D endless run.

Built for fan engagement and email capture — play the game, follow the queen.

📖 **[Complete Development Record](DEVELOPMENT_RECORD.md)** — the full history from
Day 1 to the current build (all eras, bosses, bug log, asset pipeline, and open
threads). The canonical, consolidated project documentation.

---

## Stack

The shipped game is a **single self-contained `index.html`** — no framework, no
build step, no server:

- **Canvas2D** — Action RPG rendering (sprites, entities, particles, HUD)
- **Hand-written WebGL** — Royal Runner's behind-the-back 3D world (the "GLWORLD" engine)
- **Web Audio (synthesized)** — all music and SFX generated in-browser; no audio files
- **External hashed assets** — `web/<sha1>.<ext>`, referenced by path (cacheable, deduplicated)
- **Cloudflare Worker** — global leaderboard (the only runtime network call)

Deployed to **GitHub Pages** through the guarded `tools/deploy.sh`.

> **Engine history:** the project moved through Canvas2D → hand-written WebGL →
> Phaser 3 → Godot 4 before settling on the Canvas2D + WebGL hybrid that ships
> today. The parked **Phaser 3 scaffold** (`src/`, `vite.config.js`) and **Godot 4
> project** (`once-upon-a-time/`) remain in the repo as migration / native targets.
> Full rationale in the [Engine Evolution table](DEVELOPMENT_RECORD.md#engine-evolution).

---

## Quick Start

No install needed — the game is one file. Serve the repo root with any static
server and open `index.html`:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

**Controls** (read off the input helpers `iL`/`iR`/`iU`/`iD`/`iA`/`iX` in
`index.html`, not from memory):

| | |
|---|---|
| Move | `←` `→` or `A` `D` |
| Jump | `Space`, `↑` or `W` |
| Crouch / slide | `↓` or `S` |
| Attack (Mic Strike) | `Z` or `J` |
| Dash | `Shift`, `X` or `C` |

On mobile, on-screen touch controls appear automatically, in both portrait and
landscape.

> **Block / Hold Note is not bound to anything.** This file used to document it
> as `K`; there is no `KeyK` binding anywhere in the game. The `block` sprite
> sheet exists in `SPRITES` (3 frames, `web/1b211642b143.png`) but the animation
> state is never entered — zero references to it in the draw path. So the
> mechanic is art-only in the shipped build. Left as-is and recorded rather than
> quietly deleted, because the art is there and the vocabulary is binding:
> whoever wires it up should keep the name **Hold Note**.

---

## Deploy

There is no build step — the shipped artifact is `index.html` plus the hashed
`web/` assets. Deploy to GitHub Pages through the guarded script:

```bash
tools/deploy.sh
```

It ships game-only files to the `gh-pages` branch and **aborts if any sensitive
file is staged** (real photos in `assets/` are gitignored and never published).

---

## Project Structure

```
index.html                 The shipped game (Canvas2D RPG + WebGL Runner + synth audio)
web/                        External hashed assets — web/<sha1>.<ext>
tools/                      Asset baker + composer scripts, and deploy.sh
cloudflare/                 Global-leaderboard Worker
DEVELOPMENT_RECORD.md       Canonical, consolidated project documentation

Parked scaffolds (kept in-repo, not the shipped build):
once-upon-a-time/          Godot 4 native project
src/, vite.config.js       Phaser 3 + Vite scaffold
Jand-spritesheet/          Raw individual animation frames
```

---

## Artist

**Jandé** — R&B/Soul artist, Atlanta GA
Instagram: [@jandelove1](https://instagram.com/jandelove1)
*"Once Upon A Time"* — coming soon.

---

## Built by KCTW
