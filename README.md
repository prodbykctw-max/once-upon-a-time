# Jandé — Once Upon A Time 🎤👑

A promotional browser game built for the R&B artist **Jandé** and her song
*"Once Upon A Time."* Play as Jandé across **nine themed stages** in **two modes** —
an **Action RPG** side-scroll (fight the foe roster and beat each stage's unique
boss) and **Royal Runner**, a behind-the-back 3D endless run.

**Play:** https://prodbykctw-max.github.io/once-upon-a-time/

Built for fan engagement and email capture — play the game, follow the queen.
The optional **Queen's Registry** sign-up asks for a name and email. As the code
stands, sign-ups are saved only in the player's own browser (`localStorage`,
key `jande_signups`): the EmailJS keys in `index.html` are still placeholders,
so nothing is sent anywhere.

📖 **[Complete Development Record](DEVELOPMENT_RECORD.md)** — the full history from
Day 1 onward (all eras, bosses, bug log, asset pipeline, and open threads).
Working notes for the current build are in [`CLAUDE.md`](CLAUDE.md).

---

## Which branch is live

The live site is served from the `gh-pages` branch, which `tools/deploy.sh`
rebuilds from whatever branch it is run on. At the time of this README, the live
`index.html` is identical to the one on `claude/hand-painted-architecture-bg-0MAiy`
(the development branch named in `CLAUDE.md`), which is ahead of `main`. The
`index.html` on `main` is an older build than what players see.

---

## Stack

The shipped game is a **single self-contained `index.html`** — no framework, no
bundler, no server:

- **Canvas2D** — Action RPG rendering (sprites, entities, particles, HUD)
- **Hand-written WebGL** — Royal Runner's behind-the-back 3D world (the "GLWORLD" engine)
- **Web Audio (synthesized)** — all music and SFX generated in-browser; no audio files
- **External hashed assets** — `web/<hash>.<ext>` (first 12 hex characters of the SHA-1, from `tools/externalize_assets.py`), referenced by path
- **Cloudflare Worker** — global leaderboard (the only runtime network call), with a local top-10 fallback when it is unreachable

Deployed to **GitHub Pages** through the guarded `tools/deploy.sh`.

> **Engine history:** the project moved through Canvas2D → hand-written WebGL →
> Phaser 3 → Godot 4 before settling on the Canvas2D + WebGL hybrid that ships
> today. The parked **Phaser 3 scaffold** (`src/`, `vite.config.js`,
> `package.json`, `public/assets/sprites/`) and the **Godot 4 projects**
> (`once-upon-a-time/`, `once_upon_a_time/`, `side-scroller-for-jande'/`) remain
> in the repo but are not the shipped build.
> Full rationale in the [Engine Evolution section](DEVELOPMENT_RECORD.md#engine-evolution).

---

## Quick Start

No install needed — the game is one file plus `web/`. Serve the repo root with
any static server and open `index.html`:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

`npm run dev` / `npm run build` run the parked Phaser scaffold in `src/`, not the
shipped game.

**Controls (keyboard):**
- `← →` or `A D` — Move (Royal Runner: change lane)
- `Space`, `↑` or `W` — Jump (press again in the air for a double jump)
- `↓` or `S` — Slide while running; hold while standing still to heal (Refrain, when below full lives and holding Resonance); with an air strike, a downward Downbeat
- `Z`, `X` or `J` — Attack (Mic Strike)
- `Shift` or `C` — Dash
- `P` or `Esc` — Pause

On touch devices the on-screen pad (JUMP / DASH / ATK) and swipe controls are
used. A connected gamepad also works (stick to move, A jump, X strike, B dash).

The old `K` Block (Hold Note) control is not wired: there is no `K` binding, and
the HOLD button on the ability bar sets a key nothing reads.

---

## Deploy

There is no bundler — the shipped artifact is `index.html` plus the hashed
`web/` assets. Deploy to GitHub Pages through the guarded script, from your
development branch:

```bash
bash tools/deploy.sh
```

On `main`, the script:

1. runs `tools/glyph_gate.py` and refuses to deploy if the game ships stock symbol or emoji characters;
2. generates the showcase build `fred/index.html` from `index.html` with `tools/build_fred.py`;
3. rebuilds `gh-pages` as a fresh orphan containing only `index.html`, `web/`, `fred/index.html`, the icons, `manifest.webmanifest` and `.nojekyll`;
4. **aborts if any sensitive file is staged** (real photos in `assets/` are gitignored and never published).

The leaderboard Worker deploys separately with Wrangler from `cloudflare/` —
see [`cloudflare/README.md`](cloudflare/README.md). It stores runs in a KV
namespace and rate-limits submits per IP (`cloudflare/wrangler.toml`).

## Checks

```bash
node tools/check.cjs                               # every inline <script> parses; expected assets present
node --test cloudflare/leaderboard-worker.test.mjs # leaderboard Worker tests
python3 tools/glyph_gate.py                        # the deploy-time glyph check
```

---

## Project Structure

```
index.html                 The shipped game (Canvas2D RPG + WebGL Runner + synth audio)
web/                       External hashed assets — web/<hash>.<ext>
manifest.webmanifest, icon-*.png, apple-touch-icon.png   PWA files
llms.txt, llms-full.txt, robots.txt, sitemap.xml          Discoverability files
tools/                     Asset bakers/composers, Blender scripts, glyph gate, fred build, deploy.sh
cloudflare/                Global-leaderboard Worker, its tests and wrangler.toml
docs/                      Design and fix briefs
DEVELOPMENT_RECORD.md      Canonical, consolidated project documentation
CLAUDE.md, HANDOFF.md      Working notes and session log

Not part of the shipped build (kept in-repo):
src/, vite.config.js, package.json, public/   Phaser 3 + Vite scaffold
once-upon-a-time/, once_upon_a_time/          Godot 4 projects
side-scroller-for-jande'/                     Godot 4 project stub
jande-game-improved.html                      Earlier single-file build (not deployed)
Jand-spritesheet/                             Raw individual animation frames
assets_whimsy/                                Environment mood-board kit and AutoSprite brief
archive/intro/                                Retired intro cutscene
```

---

## Artist

**Jandé** — R&B/Soul artist, Atlanta GA
Instagram: [@jandelove1](https://instagram.com/jandelove1)
*"Once Upon A Time"* — coming soon.

---

## Built by KCTW
