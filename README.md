# Jandé — Once Upon A Time 🎤👑

A self-contained single-file browser platformer built for R&B artist **Jandé** and her song *"Once Upon A Time."* Fight through nine themed rooms of a dark painted mansion, collect Grace Notes, and face the final boss.

Built for fan engagement and email capture.

---

## How It Works

Single HTML file — open it in any browser, no install, no server, no build step. All sprites and the intro video are embedded as base64 data URIs.

**Live:** `https://prodbykctw-max.github.io/once-upon-a-time/`

---

## Screen Flow

1. **Title Screen** — animated starfield canvas background, JANDÉ logo pulse animation
2. **Intro Video** — embedded mp4 cutscene, skippable on click
3. **Login / Register** — name + email capture via EmailJS; falls back to localStorage (`jande_signups`) when keys aren't set
4. **Game** — side-scrolling platformer across 9 stages
5. **Overlay** — win / death / pause screens with stage progress

---

## Controls

| Key | Action |
|-----|--------|
| `← →` / `A D` | Move |
| `Space` / `↑` | Jump |
| `Z` | Mic Strike (melee attack) |
| `Q` | Sound Wave (ranged, costs RESONANCE) |
| `E` | Throw Note (ranged, costs RESONANCE) |
| `Shift` | Dash |
| `K` / `4` | Hold Note (block) |
| `P` / `Esc` | Pause |
| `M` / `Tab` | Map |

Touch controls appear automatically on mobile.

---

## The 9 Stages

| # | Name | Theme |
|---|------|-------|
| 1 | THE GRAND LIBRARY | Ancient Knowledge |
| 2 | EGYPTIAN HALL | Pharaoh's Treasury |
| 3 | SAMURAI GALLERY | Warrior's Path |
| 4 | ROYAL CHAMBERS | Luxury Estate |
| 5 | MUSEUM WING | World Artifacts |
| 6 | TECH MANOR | Modern Antiquity |
| 7 | ARMORY CORRIDOR | Knight's Legacy |
| 8 | ART GALLERY | Masters' Collection |
| 9 | TREASURE VAULT | Jeweled Paradise |

Each stage has a unique platform layout, color palette, and enemy mix.

---

## Enemies

Three behavior classes, visually themed per stage:

- **VOID** — airborne chaser (cupid / fairy / wraith / imp)
- **LANCER** — ranged caster, shoots projectiles (fallen angel / sorcerer / gargoyle)
- **WARDEN** — ground tank, high HP (bear / lion / golem / dragon)

All drawn with Canvas 2D painterly art: volume shading, cast shadows, rim light, watercolor washes.

### Bosses
- **REVENANT** — stages 1–8 (tuxedo, flowing cape, glowing eyes, wilted bouquet)
- **HEARTBREAKER** — stage 9 finale (thorn crown, cracked beating heart, phase-2 enrage)

Boss gate opens when all ground enemies are cleared.

---

## Resources & Collectibles

| Item | Effect |
|------|--------|
| **Grace Notes** ♩ | +30 RESONANCE, +70 score |
| **DEVOTION** | +1 life mask |
| **FULL VOICE** | Refill RESONANCE |
| **BELT IT OUT** | 2× damage for duration |
| **HIGH NOTE** | Temporary shield |

**RESONANCE** bar powers Sound Wave and Throw Note attacks. Breakable blocks also drop RESONANCE.

---

## Rendering

Two-canvas layered system:
- **WebGL canvas** (`#glC`) — atmospheric GLSL background shader, stage-tinted, parallax via `camX` uniform
- **Canvas 2D** (`#fxC`) — all game entities: player sprite, enemies, platforms, particles, HUD overlays

---

## Email Capture

Set three vars in the HTML to activate EmailJS:

```js
var EJ_KEY = 'your_public_key';
var EJ_S   = 'your_service_id';
var EJ_T   = 'your_template_id';
```

Without them the login screen still works — signups save to `localStorage` under key `jande_signups`.

---

## Artist

**Jandé** — R&B/Soul artist, Atlanta GA
Instagram: [@jandelove1](https://instagram.com/jandelove1)
*"Once Upon A Time"* — coming soon.

---

## Built by KCTW
