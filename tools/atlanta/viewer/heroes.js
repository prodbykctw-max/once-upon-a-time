// HERO LANDMARKS — bespoke geometry for the buildings that ARE their shape.
//
// The facade pass fixes generic buildings, because a generic building really is
// a box with windows. It cannot fix a landmark: put the extruded Mercedes-Benz
// Stadium next to a photograph and it is a flat-topped drum, because OSM hands
// over a footprint and the single number height=93. No texture fixes a wrong
// silhouette.
//
// So: a registry keyed by OSM id. `buildCity` skips any building with a hero
// builder and calls the builder instead, handing it the REAL footprint — the
// hero still sits exactly on its surveyed outline, it just gets a shape worth
// recognising above it.
//
// This is the mechanism, not a one-off. Stone Mountain's carving, the school
// frontage and Apache all land here the same way.
import * as THREE from './vendor/three.module.min.js';
import { asset } from './base.js';

const centroidOf = (ring) => {
  let x = 0, y = 0;
  for (const [px, py] of ring) { x += px; y += py; }
  return [x / ring.length, y / ring.length];
};

/** Scale a ring toward its centroid. 1 = unchanged, 0.8 = pulled in 20%. */
const scaleRing = (ring, c, k) => ring.map(([x, y]) => [c[0] + (x - c[0]) * k, c[1] + (y - c[1]) * k]);

/**
 * A band of faceted wall between two rings at two heights.
 * FLAT-SHADED ON PURPOSE: the real building is folded metal and glass panels,
 * so each quad gets its own normal rather than a smoothed one. Smooth normals
 * would turn the folds back into the drum we are trying to get away from.
 */
function bandGeometry(ringA, hA, ringB, hB, uvScale = 0.05) {
  // hA/hB may be a NUMBER or a per-vertex ARRAY. The array form is what lets a
  // boundary zigzag instead of sitting as a flat ring, and on this building the
  // glass/shell boundary is a chevron — arguably its most recognisable line
  // after the roof.
  const HA = (i) => (Array.isArray(hA) ? hA[i % hA.length] : hA);
  const HB = (i) => (Array.isArray(hB) ? hB[i % hB.length] : hB);
  const POS = [], NOR = [], UV = [], IDX = [];
  let base = 0;
  const n = ringA.length;
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    const a0 = [ringA[i][0], HA(i), -ringA[i][1]];
    const a1 = [ringA[j][0], HA(j), -ringA[j][1]];
    const b1 = [ringB[j][0], HB(j), -ringB[j][1]];
    const b0 = [ringB[i][0], HB(i), -ringB[i][1]];
    // face normal from the quad itself
    const ux = a1[0] - a0[0], uy = a1[1] - a0[1], uz = a1[2] - a0[2];
    const vx = b0[0] - a0[0], vy = b0[1] - a0[1], vz = b0[2] - a0[2];
    let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    const L = Math.hypot(nx, ny, nz) || 1;
    nx /= L; ny /= L; nz /= L;
    const w = Math.hypot(a1[0] - a0[0], a1[2] - a0[2]);
    const hgt = Math.abs(HB(i) - HA(i));
    POS.push(...a0, ...a1, ...b1, ...b0);
    UV.push(0, 0, w * uvScale, 0, w * uvScale, hgt * uvScale, 0, hgt * uvScale);
    for (let k = 0; k < 4; k++) NOR.push(nx, ny, nz);
    IDX.push(base, base + 1, base + 2, base, base + 2, base + 3);
    base += 4;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(POS), 3));
  g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(NOR), 3));
  g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(UV), 2));
  g.setIndex(IDX);
  g.computeBoundingSphere();
  return g;
}


/**
 * A lattice of thin structural members laid over a band — the triangulated
 * steel that crosses Mercedes-Benz Stadium's curtain wall.
 *
 * THIS IS THE FEATURE THAT MAKES THE WALL RECOGNISABLE. Without it the glass is
 * a smooth leaning surface and could belong to any arena; the big diagonal
 * members are what people actually picture. Built as flat strips pushed
 * `off` metres out along each facet's own normal so they sit proud of the
 * glass and catch the sun separately from it.
 */
function latticeGeometry(ringA, hA, ringB, hB, { rows = 3, w = 0.9, off = 0.8, minH = 0 } = {}) {
  const HA = (i) => (Array.isArray(hA) ? hA[i % hA.length] : hA);
  const HB = (i) => (Array.isArray(hB) ? hB[i % hB.length] : hB);
  const POS = [], NOR = [], UV = [], IDX = [];
  let base = 0;
  const n = ringA.length;

  const lerp3 = (p, q, t) => [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, p[2] + (q[2] - p[2]) * t];

  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    const a0 = [ringA[i][0], HA(i), -ringA[i][1]];
    const a1 = [ringA[j][0], HA(j), -ringA[j][1]];
    const b1 = [ringB[j][0], HB(j), -ringB[j][1]];
    const b0 = [ringB[i][0], HB(i), -ringB[i][1]];
    // facet normal
    let nx = (a1[1] - a0[1]) * (b0[2] - a0[2]) - (a1[2] - a0[2]) * (b0[1] - a0[1]);
    let ny = (a1[2] - a0[2]) * (b0[0] - a0[0]) - (a1[0] - a0[0]) * (b0[2] - a0[2]);
    let nz = (a1[0] - a0[0]) * (b0[1] - a0[1]) - (a1[1] - a0[1]) * (b0[0] - a0[0]);
    const NL = Math.hypot(nx, ny, nz) || 1;
    nx /= NL; ny /= NL; nz /= NL;

    const strut = (P, Q) => {
      const dx = Q[0] - P[0], dy = Q[1] - P[1], dz = Q[2] - P[2];
      const L = Math.hypot(dx, dy, dz) || 1;
      const ux = dx / L, uy = dy / L, uz = dz / L;
      // in-plane perpendicular = normal x direction
      let sx = ny * uz - nz * uy, sy = nz * ux - nx * uz, sz = nx * uy - ny * ux;
      const SL = Math.hypot(sx, sy, sz) || 1;
      sx = (sx / SL) * (w / 2); sy = (sy / SL) * (w / 2); sz = (sz / SL) * (w / 2);
      const ox = nx * off, oy = ny * off, oz = nz * off;
      POS.push(P[0] + sx + ox, P[1] + sy + oy, P[2] + sz + oz,
               Q[0] + sx + ox, Q[1] + sy + oy, Q[2] + sz + oz,
               Q[0] - sx + ox, Q[1] - sy + oy, Q[2] - sz + oz,
               P[0] - sx + ox, P[1] - sy + oy, P[2] - sz + oz);
      for (let k = 0; k < 4; k++) NOR.push(nx, ny, nz);
      UV.push(0, 0, 1, 0, 1, 1, 0, 1);
      IDX.push(base, base + 1, base + 2, base, base + 2, base + 3);
      base += 4;
    };

    // Skip facets that carry almost no glass. With an extreme chevron, half the
    // facets are solid white panel — bracing them would draw a triangle across
    // a blank wall.
    if (Math.abs(HB(i) - HA(i)) < minH) continue;
    // the fold line at every facet edge — these are the verticals
    strut(a0, b0);
    for (let rI = 0; rI <= rows; rI++) {
      const t = rI / rows;
      strut(lerp3(a0, b0, t), lerp3(a1, b1, t));          // horizontal chord
    }
    // ZIGZAG diagonals: direction alternates per row AND per facet, so the
    // triangles chevron around the building instead of all leaning one way.
    for (let rI = 0; rI < rows; rI++) {
      const t0 = rI / rows, t1 = (rI + 1) / rows;
      const up = ((rI + i) % 2) === 0;
      const P = up ? lerp3(a0, b0, t0) : lerp3(a1, b1, t0);
      const Q = up ? lerp3(a1, b1, t1) : lerp3(a0, b0, t1);
      strut(P, Q);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(POS), 3));
  g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(NOR), 3));
  g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(UV), 2));
  g.setIndex(base > 65535 ? new THREE.Uint32BufferAttribute(IDX, 1)
                          : new THREE.Uint16BufferAttribute(IDX, 1));
  g.computeBoundingSphere();
  return g;
}

/** Resample a ring to exactly n points, evenly by perimeter distance. */
function resample(ring, n) {
  const segs = [];
  let total = 0;
  for (let i = 0; i < ring.length; i++) {
    const j = (i + 1) % ring.length;
    const d = Math.hypot(ring[j][0] - ring[i][0], ring[j][1] - ring[i][1]);
    segs.push(d); total += d;
  }
  const out = [];
  for (let k = 0; k < n; k++) {
    let want = (k / n) * total, i = 0;
    while (i < segs.length && want > segs[i]) { want -= segs[i]; i++; }
    i = Math.min(i, segs.length - 1);
    const f = segs[i] ? want / segs[i] : 0;
    const a = ring[i], b = ring[(i + 1) % ring.length];
    out.push([a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f]);
  }
  return out;
}

/**
 * MERCEDES-BENZ STADIUM.
 *
 * Driven by the real OSM footprint, so it sits on its surveyed outline. Built
 * from the photograph as four stacked bands plus a petal roof:
 *
 *   skirt   0.00 - 0.14   concrete podium, flared slightly
 *   glass   0.14 - 0.52   the triangulated curtain wall — the window to the city
 *   shell   0.52 - 1.00   folded white metal, tapering in
 *   roof                  EIGHT TRIANGULAR PETALS pinwheeling to an open oculus
 *
 * The petals are the thing. That aperture roof is what people picture when they
 * picture this building, and it is the one feature an extrusion can never have.
 */
// Tunables, overridable from the URL so shapes can be COMPARED rather than
// guessed at one edit per render: ?F=12&jit=0.02&peak=1.30&gmax=0.95
const Q = (typeof location !== 'undefined')
  ? new URLSearchParams(location.search) : new URLSearchParams();
const qn = (k, d) => (Q.has(k) ? parseFloat(Q.get(k)) : d);

export function mercedesBenzStadium(b, THREE_, mats) {
  // OSM's height=93 is to the TOP OF THE HIGHEST POINT, not the main mass. Used
  // as the body height it makes a tower; across four reference angles the
  // building is strikingly LOW AND WIDE — roughly 1:4 against its footprint.
  // So 93 is the peak, and the body sits well below it.
  const PEAK = b.h != null ? b.h : 93;
  const H = PEAK * 0.74;
  let ring = b.pts.slice();
  if (ring.length >= 2 && ring[0][0] === ring[ring.length - 1][0] && ring[0][1] === ring[ring.length - 1][1]) {
    ring = ring.slice(0, -1);
  }
  // TWELVE facets, not sixteen. The real shell is a handful of LARGE folded
  // planes; at sixteen they get small enough to read as a cylinder again, which
  // is exactly the drum this is meant to escape.
  // TWENTY-FOUR, with a strongly alternating radius. Twelve smooth facets gave
  // flat white blades; the real panels are FOLDED, with a crease running down
  // each one. A crease down a blade means the PLAN zigzags in and out — the
  // building is a star, not a polygon. More facets plus a weak jitter reads as
  // a cylinder; more facets plus a strong one reads as folded metal.
  const F = Math.round(qn('F', 24));
  ring = resample(ring, F);
  const c = centroidOf(ring);

  // ── ASYMMETRY. The building is not a figure of revolution. The roofline in
  // the photograph rises and falls, one corner juts up well above the rest, and
  // the plan is not a circle. A fixed per-facet profile breaks the symmetry in
  // a repeatable way — no randomness, so the model is the same every load.
  // JITTER OFF. The star fold was invented to make the shell look folded, and
  // once the white became a sloping roof the fold stopped helping and started
  // reading as crumple. Settled by rendering the variants side by side against
  // a photograph rather than reasoning about it — 0.03 and 0.05 both look
  // damaged next to 0.
  const JIT = qn('jit', 0.0);
  const RJIT = [];
  for (let i = 0; i < F; i++) RJIT.push(i % 2 === 0 ? 1 + JIT : 1 - JIT);
  // A JAGGED CROWN, not a rim. In every reference the top alternates hard
  // between peaks and valleys — that sawtooth silhouette is as recognisable as
  // the glass. A gently varying rim just reads as a wobbly drum.
  // The crown's sawtooth runs on a longer wavelength than the fold — a peak
  // every four facets, so each peak spans two folded blades.
  // Peak every PW facets; the crown's wavelength is independent of the fold.
  const PK = qn('peak', 1.12), VY = qn('valley', 0.95), PW = Math.round(qn('pw', 1));
  const TOPJ = [];
  for (let i = 0; i < F; i++) TOPJ.push(Math.floor(i / PW) % 2 === 0 ? PK : VY);
  const r = (k) => scaleRing(ring, c, k).map(([x, y], i) => {
    const s2 = RJIT[i % F];
    return [c[0] + (x - c[0]) * s2, c[1] + (y - c[1]) * s2];
  });

  // ── THE CHEVRON. The glass does not stop at a flat ring — the white shell
  // comes DOWN in points between the glass panels, and that zigzag is the
  // building's signature line after the roof. Alternating the boundary height
  // per facet is what produces it.
  // THE CHEVRON IS EXTREME, not gentle. The 0.74/0.44 alternation was still
  // basically a band with a wobble. In the photograph the white planes sweep
  // from the roof ALL THE WAY DOWN to the ground between tall glass panels —
  // some facets are almost entirely glass, their neighbours almost entirely
  // white. That near-total alternation is the shape of the building.
  // Above the concourse the white blades come to POINTS low down and the glass
  // pushes up in wedges between them.
  // Glass wedges push up where the crown dips, white blades come down where it
  // peaks — the two profiles are deliberately out of phase.
  // Glass pushes up where the crown dips and the white blade comes down where
  // it peaks — the two profiles run out of phase by design.
  // The glass wall carries more of the height than the roof does. At 0.26-0.62
  // the roof ate the building; against a photograph 0.42-0.78 is the split.
  const GMAX = qn('gmax', 0.78), GMIN = qn('gmin', 0.42);
  const GTOP = [];
  for (let i = 0; i < F; i++) {
    GTOP.push(H * (Math.floor(i / PW) % 2 === 0 ? GMIN : GMAX));
  }

  const parts = [];
  // A dark glazed CONCOURSE BAND runs the whole way round at ground level in
  // every reference photo, and it is what sets the building down rather than
  // leaving it floating.
  const parts2 = [];
  parts.push(['skirt', bandGeometry(r(1.00), 0, r(1.04), H * 0.06)]);
  parts.push(['glass', bandGeometry(r(1.04), H * 0.06, r(1.05), H * 0.24)]);
  // The glass leans out at the base and in at the top — that lean is what makes
  // it catch sky instead of ground.
  parts.push(['glass', bandGeometry(r(1.05), H * 0.24, r(0.99), GTOP)]);

  // ── BIG triangles. The first lattice used three rows and produced a fine
  // mesh; in the photograph there are only five or six triangles across the
  // whole face, each spanning nearly the full height of the glass. ONE row, and
  // heavy members, because these are primary structure and not window mullions.
  parts.push(['mullion', latticeGeometry(r(1.05), H * 0.24, r(0.99), GTOP,
                                         { rows: 1, w: 2.4, off: 1.2, minH: H * 0.3 })]);

  // shell: from the chevron up to a jagged rim
  const RIM = TOPJ.map((t) => H * 0.97 * t);
  void parts2;
  // ── THE WHITE IS A ROOF, NOT A WALL ──────────────────────────────────────
  // Side by side with a photograph this is the thing that was wrong. The white
  // panels are a SHALLOW SLOPING ROOF that OVERHANGS the glass and rises inward
  // to the peaks — not vertical blades standing on top of a glass band. Built
  // as blades they read as a crown of spikes; built as a roof they read as the
  // building. `ovh` is how far the roof's outer edge projects PAST the glass
  // below it, which is what makes it an overhang rather than a taper.
  const OVH = qn('ovh', 1.10), APEX = qn('apex', 0.62);
  parts.push(['shell', bandGeometry(r(OVH), GTOP, r(APEX), RIM)]);

  // ── roof: an ANNULUS WITH A REAL HOLE ──────────────────────────────────
  // The first two attempts closed the centre: eight triangles meeting at a
  // point make a tent, and that is the opposite of this building. The aperture
  // is the whole idea — it is a retractable roof and the opening is what people
  // picture. So the roof is a ring from the jagged rim to an inner ring, and
  // the middle is simply absent.
  //
  // The inner ring is pinwheeled — rotated against the outer one — so the
  // panels sweep rather than running straight in, which is what gives the
  // camera-shutter read.
  const rim = r(0.78), inner = r(0.30);
  const PINWHEEL = 1;                       // inner ring offset, in facets
  const POS = [], NOR = [], UV = [], IDX = [];
  let base = 0;
  const N = rim.length;
  for (let i = 0; i < N; i++) {
    const j = (i + 1) % N;
    const ii = (i + PINWHEEL) % N, jj = (j + PINWHEEL) % N;
    const a = [rim[i][0], RIM[i % F], -rim[i][1]];
    const bb = [rim[j][0], RIM[j % F], -rim[j][1]];
    // inner edge lifted, so the roof domes gently toward the opening
    const cc = [inner[jj][0], H * 1.04, -inner[jj][1]];
    const dd = [inner[ii][0], H * 1.04, -inner[ii][1]];
    let nx = (bb[1] - a[1]) * (dd[2] - a[2]) - (bb[2] - a[2]) * (dd[1] - a[1]);
    let ny = (bb[2] - a[2]) * (dd[0] - a[0]) - (bb[0] - a[0]) * (dd[2] - a[2]);
    let nz = (bb[0] - a[0]) * (dd[1] - a[1]) - (bb[1] - a[1]) * (dd[0] - a[0]);
    const L = Math.hypot(nx, ny, nz) || 1;
    if (ny < 0) { nx = -nx; ny = -ny; nz = -nz; }
    POS.push(...a, ...bb, ...cc, ...dd);
    for (let k = 0; k < 4; k++) NOR.push(nx / L, ny / L, nz / L);
    UV.push(0, 0, 1, 0, 1, 1, 0, 1);
    IDX.push(base, base + 1, base + 2, base, base + 2, base + 3);
    base += 4;
  }
  const roof = new THREE.BufferGeometry();
  roof.setAttribute('position', new THREE.BufferAttribute(new Float32Array(POS), 3));
  roof.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(NOR), 3));
  roof.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(UV), 2));
  roof.setIndex(IDX);
  roof.computeBoundingSphere();
  parts.push(['petals', roof]);

  // the opening is not empty space — the bowl and the ring of lights sit below
  const bowl = new THREE.Mesh(
    new THREE.CylinderGeometry(0, 1, 1, 8),
    mats.bowl || mats.skirt);
  {
    const cx = inner.reduce((a2, p2) => a2 + p2[0], 0) / inner.length;
    const cy = inner.reduce((a2, p2) => a2 + p2[1], 0) / inner.length;
    let rad = 0;
    for (const p2 of inner) rad = Math.max(rad, Math.hypot(p2[0] - cx, p2[1] - cy));
    bowl.geometry.dispose();
    // Keep the bowl's rim CLEAR of the roof's inner edge. At rad*1.02 and a top
    // at 1.01H it grazed the annulus at 1.04H and z-fought, which reads as
    // stripes across the roof.
    bowl.geometry = new THREE.CylinderGeometry(rad * 0.90, rad * 0.50, H * 0.40, 16, 1, true);
    bowl.position.set(cx, H * 0.78, -cy);
    bowl.material = mats.bowl || mats.skirt;
  }
  parts.push(['bowl', { __mesh: bowl }]);

  const meshes = parts.map(([k, g]) => (g && g.__mesh) ? g.__mesh
                                                      : new THREE.Mesh(g, mats[k] || mats.shell));

  // ── project the real photograph onto the shell and glass ────────────────
  // Position is URL-tunable so it can be ALIGNED by looking, the same way the
  // shape was: ?prx=..&pry=..&prz=..&pfov=..&pamt=..
  const PAMT = qn('pamt', 1.0);
  if (PAMT > 0.001) {
    // Parametrised by AZIMUTH rather than raw x/z, because aligning a
    // projection is a matter of walking around the building until the image
    // lands — and that is one number to sweep, not two.
    //
    // The photograph is cropped to the building alone. Uncropped, its sky,
    // trees and road project onto the shell as well, and a stadium wearing a
    // hedge is worse than one wearing nothing.
    const cx = c[0], cz = -c[1];
    const ANG = qn('pang', 2.2), DIST = qn('pdist', 150), PH = qn('pheight', 20);
    const proj = makeProjector(THREE, {
      image: asset('art/refs/mbs_july2018_cc0.jpg'),
      pos: [cx + Math.cos(ANG) * DIST, PH, cz + Math.sin(ANG) * DIST],
      target: [cx, H * qn('ptgt', 0.45), cz],
      fov: qn('pfov', 36),
      aspect: 796 / 316,
    });
    for (const m of meshes) {
      if (m.material === mats.skirt || m.material === mats.bowl) continue;
      m.material = m.material.clone();
      applyProjection(m.material, proj, { strength: PAMT });
    }
  }
  return meshes;
}

export const HEROES = {
  'way/536744534': { name: 'Mercedes-Benz Stadium', build: mercedesBenzStadium },
};

/**
 * PROJECTIVE TEXTURING — put the real building's PIXELS on the geometry.
 *
 * Five passes of parameter sweeping got the stadium to "the right family of
 * building" and stopped there, and the overlay test says why: the model is
 * roughly the right scale, but the real panel layout is bespoke — large, few,
 * asymmetric. There is no parameter set that produces it, because it is not a
 * family, it is one specific building. Procedural geometry can approximate a
 * type; it cannot match an instance.
 *
 * So the photograph becomes the texture. A projector camera is placed where the
 * shot was taken and the image is projected along its view, exactly like a slide
 * projector: every vertex gets a UV from its position in that camera's clip
 * space, so the real glass, the real mullions, the real panel joints and the
 * real signage all land on the geometry.
 *
 * This is the same move the Corner Store Dash hero storefronts make — facade art
 * "UV-projected from the same facade image, so paint and depth line up".
 *
 * THE LIMITATION IS REAL AND WORTH STATING: a projection is only correct from
 * near the direction it was taken. Turn far enough and it smears. For a runner
 * on a fixed route that is tolerable — she passes the building through a limited
 * arc — and several projections can be blended by facing. It is not a substitute
 * for a modelled asset if the player can orbit freely.
 */
export function makeProjector(THREE_, { image, pos, target, fov = 42, aspect = 1.5 }) {
  const cam = new THREE.PerspectiveCamera(fov, aspect, 1, 4000);
  cam.position.set(pos[0], pos[1], pos[2]);
  cam.lookAt(target[0], target[1], target[2]);
  cam.updateMatrixWorld(true);
  cam.updateProjectionMatrix();
  const m = new THREE.Matrix4()
    .set(0.5, 0, 0, 0.5, 0, 0.5, 0, 0.5, 0, 0, 0.5, 0.5, 0, 0, 0, 1)
    .multiply(cam.projectionMatrix)
    .multiply(cam.matrixWorldInverse);
  const tex = new THREE.TextureLoader().load(image);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = tex.wrapT = THREE.ClampToEdgeWrapping;
  return { matrix: m, texture: tex, camera: cam };
}

/** Patch a standard material so it samples the projected photograph. */
export function applyProjection(mat, proj, { strength = 1.0 } = {}) {
  mat.onBeforeCompile = (shader) => {
    shader.uniforms.uProjMat = { value: proj.matrix };
    shader.uniforms.uProjTex = { value: proj.texture };
    shader.uniforms.uProjDir = { value: proj.camera.getWorldDirection(new THREE.Vector3()) };
    shader.uniforms.uProjAmt = { value: strength };
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\nuniform mat4 uProjMat;\nvarying vec4 vProj;\nvarying vec3 vWN;')
      .replace('#include <worldpos_vertex>',
        '#include <worldpos_vertex>\n#if defined(USE_ENVMAP) || defined(DISTANCE) || defined(USE_SHADOWMAP) || defined(USE_TRANSMISSION) || NUM_SPOT_LIGHT_COORDS > 0\n#else\n  vec4 worldPosition = modelMatrix * vec4( transformed, 1.0 );\n#endif\n  vProj = uProjMat * worldPosition;\n  vWN = normalize( mat3( modelMatrix ) * objectNormal );');
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', '#include <common>\nuniform sampler2D uProjTex;\nuniform vec3 uProjDir;\nuniform float uProjAmt;\nvarying vec4 vProj;\nvarying vec3 vWN;')
      .replace('#include <color_fragment>',
        '#include <color_fragment>\n  {\n'
        + '    vec3 p = vProj.xyz / max(vProj.w, 1e-4);\n'
        + '    // only where the projector can actually SEE the surface: inside the\n'
        + '    // frustum and facing the projector. Without the facing test the image\n'
        + '    // also paints the far side of the building, back to front.\n'
        + '    float facing = clamp(-dot(normalize(vWN), normalize(uProjDir)), 0.0, 1.0);\n'
        + '    float inside = step(0.0, p.x) * step(p.x, 1.0) * step(0.0, p.y) * step(p.y, 1.0) * step(0.0, vProj.w);\n'
        + '    float k = uProjAmt * inside * smoothstep(0.05, 0.45, facing);\n'
        + '    vec3 shot = texture2D(uProjTex, p.xy).rgb;\n'
        + '    diffuseColor.rgb = mix(diffuseColor.rgb, shot, k);\n'
        + '  }');
  };
  mat.needsUpdate = true;
  return mat;
}

/** Materials the hero builders draw from. */
export function heroMaterials(THREE_) {
  return {
    skirt: new THREE.MeshStandardMaterial({ color: 0x8d8a85, roughness: 0.92 }),
    // GLASS IS A DIELECTRIC, NOT A METAL — and this is where the first pass
    // went wrong. At metalness 0.78 the reflection is tinted by the base colour,
    // so a dark blue base returned a dark reflection and the curtain wall came
    // out black. Diagnosed properly rather than guessed: the environment map WAS
    // bound and the normals DID point outward, so neither of the obvious causes
    // was it. Real architectural glass is a low-roughness dielectric whose
    // brightness comes from Fresnel at grazing angles. Hence low metalness, very
    // low roughness and a lifted envMapIntensity.
    glass: new THREE.MeshStandardMaterial({
      color: 0x607690, roughness: 0.06, metalness: 0.20, envMapIntensity: 2.6 }),
    shell: new THREE.MeshStandardMaterial({ color: 0xd8d9dc, roughness: 0.46, metalness: 0.22 }),
    petals: new THREE.MeshStandardMaterial({
      color: 0xe4e5e8, roughness: 0.40, metalness: 0.25, side: THREE.DoubleSide }),
    // Painted structural steel: bright enough to draw the triangles against the
    // dark glass, and double-sided because a flat strip is seen from both ends
    // as it wraps the building.
    // seen down through the open roof
    bowl: new THREE.MeshStandardMaterial({
      color: 0x3b3f46, roughness: 0.9, side: THREE.DoubleSide }),
    mullion: new THREE.MeshStandardMaterial({
      color: 0xdfe1e4, roughness: 0.52, metalness: 0.30, side: THREE.DoubleSide }),
  };
}
