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
  const POS = [], NOR = [], UV = [], IDX = [];
  let base = 0;
  const n = ringA.length;
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    const a0 = [ringA[i][0], hA, -ringA[i][1]];
    const a1 = [ringA[j][0], hA, -ringA[j][1]];
    const b1 = [ringB[j][0], hB, -ringB[j][1]];
    const b0 = [ringB[i][0], hB, -ringB[i][1]];
    // face normal from the quad itself
    const ux = a1[0] - a0[0], uy = a1[1] - a0[1], uz = a1[2] - a0[2];
    const vx = b0[0] - a0[0], vy = b0[1] - a0[1], vz = b0[2] - a0[2];
    let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    const L = Math.hypot(nx, ny, nz) || 1;
    nx /= L; ny /= L; nz /= L;
    const w = Math.hypot(a1[0] - a0[0], a1[2] - a0[2]);
    const hgt = Math.abs(hB - hA);
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
function latticeGeometry(ringA, hA, ringB, hB, { rows = 3, w = 0.9, off = 0.8 } = {}) {
  const POS = [], NOR = [], UV = [], IDX = [];
  let base = 0;
  const n = ringA.length;

  const lerp3 = (p, q, t) => [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, p[2] + (q[2] - p[2]) * t];

  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    const a0 = [ringA[i][0], hA, -ringA[i][1]];
    const a1 = [ringA[j][0], hA, -ringA[j][1]];
    const b1 = [ringB[j][0], hB, -ringB[j][1]];
    const b0 = [ringB[i][0], hB, -ringB[i][1]];
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
export function mercedesBenzStadium(b, THREE_, mats) {
  const H = b.h != null ? b.h : 93;
  let ring = b.pts.slice();
  if (ring.length >= 2 && ring[0][0] === ring[ring.length - 1][0] && ring[0][1] === ring[ring.length - 1][1]) {
    ring = ring.slice(0, -1);
  }
  // 16 facets reads as folded panels; the raw OSM ring is too irregular to
  // fold cleanly and too coarse to curve.
  ring = resample(ring, 16);
  const c = centroidOf(ring);

  const r = (k) => scaleRing(ring, c, k);
  const parts = [];

  // skirt → glass → shell
  // Proportions read off the photograph. The GLASS is the dominant face from
  // the street — the first pass gave it a third of the height and it read as a
  // black belt on a drum. The white shell is the upper structure, and it tapers
  // hard; the real building leans in noticeably toward the roof.
  parts.push(['skirt', bandGeometry(r(1.00), 0, r(1.04), H * 0.10)]);
  // THE LEAN IS NOT DECORATION. A vertical mirror reflects the horizon and the
  // ground; a leaning one catches the sky, which is why the real curtain wall
  // reads bright. Nearly vertical glass renders dark no matter what the material
  // says. ~10% inward over the band is about 11 degrees.
  parts.push(['glass', bandGeometry(r(1.06), H * 0.10, r(0.96), H * 0.60)]);
  parts.push(['shell', bandGeometry(r(0.96), H * 0.60, r(0.74), H * 0.96)]);
  parts.push(['mullion', latticeGeometry(r(1.06), H * 0.10, r(0.96), H * 0.60,
                                         { rows: 3, w: 1.1, off: 0.9 })]);

  // ── the eight-petal aperture roof ──
  const rim = r(0.74), oc = r(0.20);
  const POS = [], NOR = [], UV = [], IDX = [];
  let base = 0;
  const N = rim.length, PET = 8, per = N / PET;
  for (let p = 0; p < PET; p++) {
    const i0 = Math.round(p * per), i1 = Math.round((p + 1) * per) % N;
    // each petal: from two rim points in to ONE oculus point, offset around the
    // ring so the petals pinwheel rather than meeting head-on
    const oi = Math.round((p * per + per * 0.5 + per * 0.45)) % N;
    const a = [rim[i0][0], H * 0.96, -rim[i0][1]];
    const bb = [rim[i1][0], H * 0.96, -rim[i1][1]];
    // the petal tip rises well above the rim — that lift is what makes the
    // roof read as a pinwheel of blades instead of a lid
    const d = [oc[oi][0], H * 1.14, -oc[oi][1]];
    let nx = (bb[1] - a[1]) * (d[2] - a[2]) - (bb[2] - a[2]) * (d[1] - a[1]);
    let ny = (bb[2] - a[2]) * (d[0] - a[0]) - (bb[0] - a[0]) * (d[2] - a[2]);
    let nz = (bb[0] - a[0]) * (d[1] - a[1]) - (bb[1] - a[1]) * (d[0] - a[0]);
    const L = Math.hypot(nx, ny, nz) || 1;
    if (ny < 0) { nx = -nx; ny = -ny; nz = -nz; }
    POS.push(...a, ...bb, ...d);
    NOR.push(nx / L, ny / L, nz / L, nx / L, ny / L, nz / L, nx / L, ny / L, nz / L);
    UV.push(0, 0, 1, 0, 0.5, 1);
    IDX.push(base, base + 1, base + 2);
    base += 3;
  }
  const roof = new THREE.BufferGeometry();
  roof.setAttribute('position', new THREE.BufferAttribute(new Float32Array(POS), 3));
  roof.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(NOR), 3));
  roof.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(UV), 2));
  roof.setIndex(IDX);
  roof.computeBoundingSphere();
  parts.push(['petals', roof]);

  return parts.map(([k, g]) => new THREE.Mesh(g, mats[k] || mats.shell));
}

export const HEROES = {
  'way/536744534': { name: 'Mercedes-Benz Stadium', build: mercedesBenzStadium },
};

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
      color: 0x51657d, roughness: 0.07, metalness: 0.22, envMapIntensity: 2.2 }),
    shell: new THREE.MeshStandardMaterial({ color: 0xd8d9dc, roughness: 0.46, metalness: 0.22 }),
    petals: new THREE.MeshStandardMaterial({
      color: 0xe4e5e8, roughness: 0.40, metalness: 0.25, side: THREE.DoubleSide }),
    // Painted structural steel: bright enough to draw the triangles against the
    // dark glass, and double-sided because a flat strip is seen from both ends
    // as it wraps the building.
    mullion: new THREE.MeshStandardMaterial({
      color: 0xdfe1e4, roughness: 0.52, metalness: 0.30, side: THREE.DoubleSide }),
  };
}
