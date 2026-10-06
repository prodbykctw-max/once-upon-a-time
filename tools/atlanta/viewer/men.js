// THE THREE MEN SHE IS DODGING — silhouettes first, art later.
//
// Client, on the Game II redesign: the three obstacles stop being objects and
// become "guys that she's trying to avoid", in the register of the Gross
// Sisters — broad, blocking, deliberately in her way.
//
// ── WHY THIS IS A READABILITY PROBLEM, NOT A MODELLING ONE ─────────────────
// Today `low` / `gate` / `wall` are three different KINDS of object, so they
// telegraph jump / slide / dodge instantly — the player reads the shape, not
// the label. Make all three person-shaped and that telegraph is gone unless the
// silhouettes are designed to carry it. `docs/GAME_II_ATLANTA.md` puts the
// black-silhouette test before any rendering for exactly this reason, and it is
// the cheapest possible way to kill the risk: three generated characters that
// turn out to be confusable at speed is three wasted AutoSprite runs.
//
// So the rule driving every proportion below: THE MASS SAYS THE ACTION.
//
//   low   — mass LOW AND WIDE, nothing above knee height .... jump it
//   gate  — mass HIGH, a clear gap underneath ............... slide under it
//   wall  — mass FULL HEIGHT and solid, no gap anywhere ..... go round it
//
// Those read as different shapes with all colour removed, which is the whole
// point. Anything that only distinguishes them by detail, texture or face fails
// at 5.8 m on a phone, which is where the decision actually gets made.
import * as THREE from './vendor/three.module.min.js';

function box(w, h, d, x, y, z, rx = 0, rz = 0) {
  const g = new THREE.BoxGeometry(w, h, d);
  if (rx) g.rotateX(rx);
  if (rz) g.rotateZ(rz);
  g.translate(x, y, z);
  return g;
}

function merge(parts) {
  const pos = [], nor = [], idx = [];
  let base = 0;
  for (const g of parts) {
    const p = g.attributes.position, n = g.attributes.normal;
    for (let i = 0; i < p.count; i++) {
      pos.push(p.getX(i), p.getY(i), p.getZ(i));
      nor.push(n.getX(i), n.getY(i), n.getZ(i));
    }
    if (g.index) for (let i = 0; i < g.index.count; i++) idx.push(g.index.array[i] + base);
    else for (let i = 0; i < p.count; i++) idx.push(i + base);
    base += p.count;
    g.dispose();
  }
  const out = new THREE.BufferGeometry();
  out.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3));
  out.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(nor), 3));
  out.setIndex(idx);
  out.computeBoundingSphere();
  return out;
}

// ── low: CROUCHED, BRACED, BELOW HER JUMP ─────────────────────────────────
// Hard ceiling 0.90 m, because her apex is 1.20 m and `play.js` blocks a `low`
// whenever she is under 0.90. Wide (1.5 m) so the mass reads as a floor-level
// obstruction rather than a small thing she could sidestep — the action is
// jump, and a narrow crouching figure invites a lane change instead.
function manLow() {
  // THE PROFILE IS A WEDGE, NOT A SLAB. First pass made this a wide low
  // rectangle and `wall` a tall narrow one — measured shape-only IoU 0.56
  // against `wall`, marginal, because once scale is normalised away two
  // rectangles are the same rectangle. The outline has to differ, not just the
  // proportions: this one rises at the back and slopes away at the front, with
  // the head dropped forward below shoulder level, so it reads as a hunched
  // mass rather than a block.
  return merge([
    box(0.66, 0.50, 0.46, 0, 0.56, 0.10),         // high back / shoulders
    box(0.60, 0.34, 0.40, 0, 0.30, -0.22),        // mid, stepping down
    box(0.30, 0.26, 0.30, 0, 0.26, -0.48),        // head, low and forward
    box(0.30, 0.30, 0.34, -0.46, 0.17, 0.04),     // braced arm, low
    box(0.30, 0.30, 0.34, 0.46, 0.17, 0.04),      // braced arm, low
    box(1.44, 0.18, 0.40, 0, 0.09, 0.14),         // the low spread at the rear
  ]);
}

// ── gate: TALL, ARMS UP, A GAP SHE CAN SLIDE THROUGH ──────────────────────
// `play.js` blocks a `gate` whenever she is taller than 1.20, and her sliding
// height is 0.80 — so everything solid has to sit ABOVE 1.20 and the space
// below has to look empty. Legs are pushed wide to the lane edges, which both
// opens that gap visually and gives the figure an unmistakable inverted-V
// bottom that neither of the others has.
function manGate() {
  return merge([
    box(0.78, 0.60, 0.40, 0, 1.62, 0),            // chest, high
    box(0.32, 0.30, 0.32, 0, 2.05, 0),            // head
    box(1.70, 0.26, 0.34, 0, 2.18, 0),            // arms braced overhead
    box(0.24, 0.42, 0.26, -0.80, 2.00, 0),        // upper arm, left
    box(0.24, 0.42, 0.26, 0.80, 2.00, 0),         // upper arm, right
    box(0.26, 1.30, 0.28, -0.62, 0.70, 0, 0, 0.17),  // leg, splayed out
    box(0.26, 1.30, 0.28, 0.62, 0.70, 0, 0, -0.17),  // leg, splayed out
  ]);
}

// ── wall: FULL HEIGHT, SOLID, NO WAY THROUGH ──────────────────────────────
// Blocks unconditionally, so the silhouette must offer no gap anywhere — feet
// together, arms folded across the chest, shoulders wide. The only honest
// answer to it is another lane, and the shape should say so before she is close
// enough to try anything else.
function manWall() {
  // THE PROFILE IS A T. Shoulders far wider than the stance, so the mass is up
  // and out and the outline narrows toward the ground — the opposite reading to
  // `low`, which is wide at the floor and tapers upward. That contrast is what
  // separates the pair after scale is normalised away; matching rectangles did
  // not.
  return merge([
    box(1.46, 0.34, 0.46, 0, 1.76, 0),            // shoulder span, very wide
    box(0.36, 0.34, 0.36, 0, 2.08, 0),            // head
    box(1.30, 0.30, 0.42, 0, 1.40, 0.16),         // folded arms
    box(0.96, 0.62, 0.44, 0, 1.28, 0),            // chest
    box(0.62, 0.60, 0.40, 0, 0.74, 0),            // waist, narrower
    box(0.52, 0.46, 0.38, 0, 0.23, 0),            // stance, narrowest
  ]);
}

export const MEN = { low: manLow, gate: manGate, wall: manWall };

/** Heights the gameplay actually enforces, for the harness to assert against. */
export const MAN_LIMITS = { low: 0.90, gate: { solidAbove: 1.20 }, wall: null };

let _cache = null;
export function manGeometries() {
  if (!_cache) _cache = { low: manLow(), gate: manGate(), wall: manWall() };
  return _cache;
}
