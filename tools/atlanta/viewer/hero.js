// JANDÉ IN THE RUN — her real sprite art, billboarded into the 3D city.
//
// Royal Runner is behind-the-back, so what the player sees is her BACK, and the
// shipped game already has exactly that: `bkrun`, `bkjump`, `bkslide`, three
// 1280x1280 sheets of 5x5 cells, 25 frames each, 471 KB total, already in
// `web/`. No new art, no 3D character, no AutoSprite credit spent — and it is
// the real rendered Jandé rather than a stand-in.
//
// A camera-facing quad is the right primitive here and not a shortcut: the view
// is fixed behind her, so there is no angle from which a billboard betrays
// itself. Billboarding is YAW-ONLY — tilting the quad to face a camera that
// looks slightly down would lean her backwards out of the ground plane.
import * as THREE from './vendor/three.module.min.js';

// ── SHEET GEOMETRY, MEASURED FROM THE ART, NOT ASSUMED ─────────────────────
// Two traps here, both found by measuring the alpha bounds of all 75 cells
// rather than trusting that three sheets of the same pixel size mean three
// sprites of the same scale:
//
// 1. THE SHEETS FILL THEIR CELLS DIFFERENTLY. Her body is 182 px tall in
//    `bkrun` and 227 px in `bkjump`. Scaling every cell to the same world
//    height would make her GROW 25% the instant she jumps. One cell is one
//    fixed world size instead, so the difference reads as the pose it is —
//    limbs extended — which is what it actually is.
//
// 2. SHE SITS AT A DIFFERENT HEIGHT IN EACH CELL. The gap below her feet is
//    35 px in `bkrun`, 16 in `bkjump`, 13 in `bkslide`. Anchoring the quad by
//    the cell would float her 0.33 m off the ground while running and 0.12 m
//    while sliding — a different float per state, which reads as the ground
//    moving. Each sheet carries its own measured foot offset.
//
// The scale reference is the run sheet: 182 px of body = 1.70 m, so a 256 px
// cell is 2.391 m.
const CELL_M = (256 / 182) * 1.70;

const SHEETS = {
  run:   { src: 'web/73d33193c5ad.webp', footPx: 35 },
  jump:  { src: 'web/c2da2f2d110f.webp', footPx: 16 },
  slide: { src: 'web/1ff3fa4d05b5.webp', footPx: 13 },
};
const COLS = 5, ROWS = 5, FRAMES = 25;

// Animation rate. The shipped convention is game-frames PER animation frame, so
// SMALLER IS FASTER (run/dash 4 = 15 fps). 25 frames at 15 fps is a 1.67 s
// cycle; against a 4.8 m/s run that is 8.0 m per cycle, and her stride in the
// RPG is 2.36 body-heights — so the cycle is held to roughly that here too
// rather than being picked by eye.
const RUN_FPS = 15;

function sheetTexture(url) {
  const t = new THREE.TextureLoader().load(url);
  t.colorSpace = THREE.SRGBColorSpace;
  // NEAREST on a sprite sheet: linear filtering samples across the cell border
  // and bleeds the neighbouring frame in as a halo down one edge.
  t.magFilter = THREE.NearestFilter;
  t.minFilter = THREE.LinearMipmapLinearFilter;
  t.generateMipmaps = true;
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  t.repeat.set(1 / COLS, 1 / ROWS);
  return t;
}

/**
 * Build the hero billboard.
 * `asset` resolves a REPO-ROOT path for this host — her sheets are the shipped
 * game's own, in `web/` at the top of the repo (see `rootAsset` in base.js).
 */
export function createHero(asset) {
  const group = new THREE.Group();
  group.name = 'jande';

  const mats = {};
  for (const k of Object.keys(SHEETS)) {
    mats[k] = new THREE.MeshBasicMaterial({
      map: sheetTexture(asset(SHEETS[k].src)),
      transparent: true,
      // alphaTest, or the quad writes depth across its transparent corners and
      // punches a hole in whatever is behind her.
      alphaTest: 0.35,
      depthWrite: true,
      toneMapped: true,          // she is graded with the world, not outside it
      side: THREE.DoubleSide,
    });
  }

  const quad = new THREE.Mesh(new THREE.PlaneGeometry(CELL_M, CELL_M), mats.run);
  quad.name = 'jande_quad';
  quad.castShadow = false;       // a billboard casts a cardboard shadow
  group.add(quad);

  let state = 'run', frame = 0, clock = 0;

  /** @param st the run state from play.js · @param cam the camera to face */
  function update(dt, st, cam) {
    const want = st.slide > 0 ? 'slide' : (st.y > 0.02 ? 'jump' : 'run');
    if (want !== state) { state = want; quad.material = mats[state]; frame = 0; clock = 0; }

    if (state === 'jump') {
      // Map the frame to WHERE SHE IS IN THE ARC, not to a timer. Playing a
      // jump sheet at a fixed rate finishes early and holds the landing pose in
      // mid-air — the same trap the RPG's 6-frame jump hit, recorded in
      // CLAUDE.md. Airtime here is 0.73 s and the sheet has 25 frames, so the
      // arc drives them directly: rising maps the first half, falling the rest.
      // The reference is the LAUNCH VELOCITY, not a magic number: g*t/2 with
      // g = 18 and t = 0.73 is 6.57 m/s. An invented 8.9 compressed the whole
      // rise into the first fifth of the sheet.
      const V0 = 6.57;
      const peak = st.vy > 0 ? 0.5 * (1 - st.vy / V0)
                             : 0.5 + 0.5 * Math.min(1, -st.vy / V0);
      frame = Math.max(0, Math.min(FRAMES - 1, Math.round(peak * (FRAMES - 1))));
    } else {
      clock += dt;
      frame = Math.floor(clock * RUN_FPS) % FRAMES;
    }
    const m = quad.material.map;
    if (m) m.offset.set((frame % COLS) / COLS, 1 - 1 / ROWS - Math.floor(frame / COLS) / ROWS);

    const p = st.pose();
    // Feet on the ground: lift by half a cell, then take back the measured gap
    // below her in THIS sheet.
    const foot = (SHEETS[state].footPx / 256) * CELL_M;
    group.position.set(p.x, p.z + CELL_M / 2 - foot, -p.y);

    // YAW ONLY. Facing the camera outright would tip her off the ground plane.
    group.rotation.set(0, Math.atan2(cam.position.x - group.position.x,
                                     cam.position.z - group.position.z), 0);
  }

  return { group, update, CELL_M };
}
