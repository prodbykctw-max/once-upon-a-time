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

// ── THE SIDE VIEW — the RPG's own sheets, in the 3D city ───────────────────
// The RPG camera looks ACROSS the route rather than down it, so the back sheets
// are the wrong art: it needs her profile. The shipped Action RPG already has
// it, and these are those exact files — never a re-render, never a mirror of
// the back view.
//
// MEASURED, like the back sheets were, and they turn out to be a different
// animal. The back sheets are 256 px cells with her floating inside them (body
// 182-227 px, foot gaps 13-35 px), which is why each needed its own offset.
// The side sheets are tightly cropped: body 150 of 154 rows, foot gap 2-3 px,
// top gap 2 px, on all three. So one scale covers them and the foot offset is
// almost nothing — but it is still derived rather than dropped.
//
// The cells are NOT square and NOT the same width (run 145, jump 102, dash
// 159), so the quad has to be rebuilt per sheet or she stretches. That is the
// whole reason this set is handled separately instead of being bolted onto the
// table above.
//
// Scale reference is the same as the back view's: 150 px of body = 1.70 m,
// which makes a 154 px cell 1.745 m tall.
const SIDE_CELL_M = (154 / 150) * 1.70;
const SIDE = {
  run:  { src: 'web/36be4ed7efc3.png', n: 8, cw: 145, footPx: 2.5, fps: 15 },
  jump: { src: 'web/9f32be555c97.png', n: 6, cw: 102, footPx: 2,   fps: 8.6 },
  // There is no side-view SLIDE sheet in the shipped game — the RPG has no
  // slide. `dash` is the low, fast, committed pose and is what a slide reads
  // as from the side, so the slide state borrows it rather than inventing art.
  slide:{ src: 'web/e803235545ba.png', n: 5, cw: 159, footPx: 2,   fps: 15 },
};

function sideTexture(url, n) {
  const t = new THREE.TextureLoader().load(url);
  t.colorSpace = THREE.SRGBColorSpace;
  t.magFilter = THREE.NearestFilter;
  t.minFilter = THREE.LinearMipmapLinearFilter;
  t.generateMipmaps = true;
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  t.repeat.set(1 / n, 1);          // one row, n columns
  return t;
}

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

  // Side-view materials and their per-sheet quads. Built up front so switching
  // view costs nothing mid-render; the geometries differ because the cells do.
  const sideMats = {}, sideGeo = {};
  for (const k of Object.keys(SIDE)) {
    const S = SIDE[k];
    sideMats[k] = new THREE.MeshBasicMaterial({
      map: sideTexture(asset(S.src), S.n),
      transparent: true, alphaTest: 0.35, depthWrite: true,
      toneMapped: true, side: THREE.DoubleSide,
    });
    sideGeo[k] = new THREE.PlaneGeometry((S.cw / 154) * SIDE_CELL_M, SIDE_CELL_M);
  }

  const quad = new THREE.Mesh(new THREE.PlaneGeometry(CELL_M, CELL_M), mats.run);
  quad.name = 'jande_quad';
  quad.castShadow = false;       // a billboard casts a cardboard shadow
  group.add(quad);

  let state = 'run', frame = 0, clock = 0, view = 'back';

  /**
   * 'back' is the Royal Runner billboard that faces the camera.
   * 'side' is the RPG profile: the quad's normal points at the camera and its
   * RIGHT edge points along travel, so she faces the way she is running — the
   * shipped art faces right, so nothing is ever mirrored.
   */
  function setView(v) {
    if (v === view) return;
    view = v; frame = 0; clock = 0;
    quad.geometry = view === 'side' ? sideGeo[state] : new THREE.PlaneGeometry(CELL_M, CELL_M);
    quad.material = view === 'side' ? sideMats[state] : mats[state];
  }

  /** @param st the run state from play.js · @param cam the camera to face */
  function update(dt, st, cam) {
    const want = st.slide > 0 ? 'slide' : (st.y > 0.02 ? 'jump' : 'run');
    if (want !== state) {
      state = want; frame = 0; clock = 0;
      if (view === 'side') { quad.material = sideMats[state]; quad.geometry = sideGeo[state]; }
      else quad.material = mats[state];
    }

    if (view === 'side') {
      const S = SIDE[state];
      if (state === 'jump') {
        // Same rule as the back view: the frame tracks WHERE SHE IS IN THE ARC,
        // not a timer, or a 6-frame sheet finishes early and holds the landing
        // pose in mid-air.
        const V0 = 6.57;
        const peak = st.vy > 0 ? 0.5 * (1 - st.vy / V0)
                               : 0.5 + 0.5 * Math.min(1, -st.vy / V0);
        frame = Math.max(0, Math.min(S.n - 1, Math.round(peak * (S.n - 1))));
      } else {
        clock += dt;
        frame = Math.floor(clock * S.fps) % S.n;
      }
      const sm = quad.material.map;
      if (sm) sm.offset.set(frame / S.n, 0);

      const p = st.pose();
      const foot = (S.footPx / 154) * SIDE_CELL_M;
      group.position.set(p.x, p.z + SIDE_CELL_M / 2 - foot, -p.y);

      // Normal at the camera, right edge along travel. With the route's normal
      // (nx, ny) and three.js mapping (x, h, -y), yaw = atan2(nx, -ny) sends
      // the quad's +Z to (nx, 0, -ny) and its +X to the forward direction.
      const r = st.at(st.s);
      group.rotation.set(0, Math.atan2(r.nx, -r.ny), 0);
      return;
    }

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

  return { group, update, setView, CELL_M, SIDE_CELL_M };
}
