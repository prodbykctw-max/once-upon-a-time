// Build an Atlanta location as three.js geometry, straight from world.json.
//
// This is the first piece of the Game II renderer, not a throwaway preview: the
// same world.json the Blender blockout reads is read here, which is the whole
// point of the format — "one source of truth for both the Blender build and the
// game engine."
//
// MERGE BY MATERIAL, NOT BY OBJECT. The budget adopted on 10-02 is <=150 draw
// calls on a mid-range phone. One mesh per building would be 50+ calls for a
// single location before a single prop exists, so every building of a kind goes
// into ONE BufferGeometry. The Blender blockout keeps them separate on purpose
// (facades and LODs need per-building objects); the runtime does not.
import * as THREE from './vendor/three.module.min.js';
import { HEROES, heroMaterials } from './heroes.js';
import { buildProps } from './props.js';
import { buildLife } from './life.js';
import { buildLevel, levelGizmo, corridorFilter } from './level.js';
import { asset } from './base.js';

// TILE SIZE COMES FROM THE FILENAME, deliberately. make_facades.py bakes the
// real-world size of each trim sheet into its name, so there is exactly one
// place that knows it. Rename a sheet and the UVs follow; there is no second
// constant to forget.
const FACADES = [
  { max: 12,       file: 'brick_lowrise_14.4x9.6m.jpg' },
  { max: 32,       file: 'concrete_midrise_18.0x16.0m.jpg' },
  { max: Infinity, file: 'glass_tower_18.0x19.2m.jpg' },
];
const tileOf = (f) => {
  const m = f.match(/_([\d.]+)x([\d.]+)m\./);
  return m ? [parseFloat(m[1]), parseFloat(m[2])] : [16, 16];
};
const heightOfB = (b) => (b.h != null ? b.h : (EST_H[b.kind] ?? EST_DEFAULT));

const FOOT_KINDS = new Set(['footway', 'path', 'steps', 'cycleway', 'pedestrian']);
const LANE_M = 3.3;
const CLASS_W = {
  motorway: 14, trunk: 12, primary: 11, secondary: 10, tertiary: 9,
  residential: 7.5, unclassified: 7, service: 4.5, living_street: 6,
  pedestrian: 5, footway: 2, path: 1.8, cycleway: 2.5, steps: 1.6, track: 3,
};
// Same estimate table as the Blender blockout. If these ever disagree, the
// preview stops predicting the bake — keep them in step.
const EST_H = {
  house: 6, detached: 6, residential: 9, apartments: 15, retail: 7,
  commercial: 12, office: 20, industrial: 9, school: 9, church: 12,
  stadium: 35, roof: 4, garage: 3,
};
const EST_DEFAULT = 8;

const ringArea2 = (pts) => {
  let a = 0;
  for (let i = 0; i < pts.length; i++) {
    const [x1, y1] = pts[i], [x2, y2] = pts[(i + 1) % pts.length];
    a += x1 * y2 - x2 * y1;
  }
  return a;
};

function cleanRing(pts) {
  let p = pts;
  if (p.length >= 2 && p[0][0] === p[p.length - 1][0] && p[0][1] === p[p.length - 1][1]) {
    p = p.slice(0, -1);                       // OSM repeats the closing vertex
  }
  return p.length >= 3 ? p : null;
}


// ── TERRAIN ────────────────────────────────────────────────────────────────
// Replaces the flat plate. Stone Mountain measures 240 m of relief inside a
// single 450 m extract — on flat ground that location is not simplified, it is
// deleted. Everything else in the scene now has to sit ON this, so the height
// sampler below is used by the roads, the areas and the buildings too.

/** Bilinear height at world (x, y). y is NORTH, not three.js z. */
export function heightAt(E, x, y) {
  if (!E) return 0;
  const N = E.grid;
  const fi = (x - E.x0) / E.step, fj = (y - E.y0) / E.step;
  const i = Math.max(0, Math.min(N - 2, Math.floor(fi)));
  const j = Math.max(0, Math.min(N - 2, Math.floor(fj)));
  const tx = Math.max(0, Math.min(1, fi - i)), ty = Math.max(0, Math.min(1, fj - j));
  const z = E.z;
  const a = z[j * N + i], b = z[j * N + i + 1];
  const c = z[(j + 1) * N + i], d = z[(j + 1) * N + i + 1];
  return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty;
}

// Ground cover, painted ONTO the terrain rather than laid over it.
const COVER = {
  water:      [0.09, 0.19, 0.31],
  wood:       [0.10, 0.19, 0.09],
  forest:     [0.10, 0.19, 0.09],
  scrub:      [0.21, 0.24, 0.14],
  bare_rock:  [0.47, 0.46, 0.44],   // Stone Mountain's dome IS this
  sand:       [0.60, 0.54, 0.40],
  park:       [0.17, 0.33, 0.13],
  grass:      [0.19, 0.36, 0.14],
  grassland:  [0.22, 0.34, 0.16],
  meadow:     [0.23, 0.35, 0.16],
  recreation_ground: [0.18, 0.34, 0.14],
  cemetery:   [0.20, 0.32, 0.16],
  pitch:      [0.16, 0.38, 0.15],
  track:      [0.38, 0.17, 0.12],   // the rubberised oval
  // A stadium footprint is the track surface plus its infield, and it is the
  // whole point of the Track & Field location — without a colour it paints as
  // bare ground and the landmark disappears into the grass around it.
  stadium:    [0.36, 0.16, 0.12],
  sports_centre: [0.20, 0.33, 0.15],
  playground: [0.33, 0.26, 0.18],
  garden:     [0.19, 0.34, 0.15],

  // ── URBAN GROUND ──────────────────────────────────────────────────────────
  // Without these the extract is one tan plane with road ribbons on it. Parking
  // is the big one: 16 lots at MBS alone, and they are what actually surrounds
  // an American stadium. Kept DESATURATED and close in value to each other —
  // the point is to break the plane into readable areas, not to turn the city
  // into a landuse map.
  amenity_parking:      [0.21, 0.21, 0.22],
  amenity_school:       [0.25, 0.28, 0.22],
  amenity_university:   [0.25, 0.28, 0.22],
  amenity_hospital:     [0.28, 0.27, 0.27],
  amenity_place_of_worship: [0.27, 0.25, 0.24],
  residential:          [0.27, 0.25, 0.22],
  retail:               [0.30, 0.27, 0.24],
  commercial:           [0.28, 0.27, 0.27],
  industrial:           [0.26, 0.25, 0.24],
  construction:         [0.34, 0.30, 0.22],
  brownfield:           [0.30, 0.27, 0.19],
  railway:              [0.22, 0.20, 0.19],
  farmland:             [0.33, 0.31, 0.19],
  military:             [0.24, 0.25, 0.21],
  quarry:               [0.38, 0.36, 0.33],
  plaza:                [0.33, 0.32, 0.30],
  bridge:               [0.25, 0.25, 0.26],
};
const BARE = [0.34, 0.31, 0.27];

function pointInRing(x, y, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i], [xj, yj] = ring[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}

/**
 * Terrain, SUBDIVIDED finer than the elevation grid and painted per vertex.
 *
 * Two bugs fixed at once, both from laying ground cover over the ground as
 * separate geometry: a coarse ShapeGeometry polygon draped on a hill cuts
 * STRAIGHT THROUGH the terrain and through the roads, which is why Wade Walker
 * came out as unbroken green with every road swallowed. Painting the surface
 * instead means there is nothing to z-fight with and nothing to drape.
 *
 * SUB is why the boundaries stay sharp: the elevation grid is only 40x40 (23 m
 * spacing), which would put a park edge in 23 m steps. Sampling bilinearly
 * between those gives a finer mesh for free — the DEM is the limit on height
 * detail, not on how finely it can be coloured.
 */
function terrainGeometry(E, areas, SUB = 3, EXT = 2.2, opts = {}) {
  // ── TWO RINGS, BECAUSE 80% OF THE TRIANGLE BUDGET WAS OUT HERE ──────────
  // Measured at MBS: terrain was **132,098 of 165,446 triangles — 79.8%** of
  // the whole scene, more than the city, the crowd and the traffic combined.
  // One uniform grid at SUB=3 across EXT=2.2 meshes a 1,536 m square at 6 m
  // spacing, which is (a) three times finer than the 17.9 m DEM actually
  // resolves and (b) spread over 4.84x the area the data even covers. Culling
  // buildings to the level corridor saved 5% of triangles; this is where the
  // other 75% lives.
  // SUB exists for the ground-cover COLOUR, which is painted per vertex and
  // needs resolution only where the player can see the edges of it. So: the
  // sampled extent gets the full SUB, and the filler ring beyond it — distant
  // ground, no cover boundaries worth resolving — gets SUB=1, with the quads
  // under the inner ring skipped so nothing z-fights.
  if (opts.ring !== 'inner' && opts.ring !== 'outer' && EXT > 1) {
    const inner = terrainGeometry(E, areas, SUB, 1, { ring: 'inner' });
    const outer = terrainGeometry(E, areas, 1, EXT, { ring: 'outer' });
    return mergeGeometries([inner, outer]);
  }
  // EXTEND PAST THE SAMPLED GRID instead of adding a flat skirt underneath it.
  // The skirt was a plane at (min height - 2), and from a runner's eye it filled
  // the lower half of the frame as a black wedge — it reads as a rendering
  // fault. `heightAt` already clamps outside the grid, so simply meshing a wider
  // area gives a border that joins the terrain seamlessly and has no step.
  const span = E.step * (E.grid - 1);
  const N = Math.round(((E.grid - 1) * SUB) * EXT) + 1;
  const step = (span * EXT) / (N - 1);
  const x0 = E.x0 - span * (EXT - 1) / 2, y0 = E.y0 - span * (EXT - 1) / 2;
  const POS = [], UV = [], COL = [], IDX = [];

  // biggest polygons first so a pitch inside a park wins over the park
  const sorted = (areas || []).slice().sort((a, b) => {
    const ext = (p) => {
      let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
      for (const [x, y] of p.pts) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
      return (x1 - x0) * (y1 - y0);
    };
    return ext(b) - ext(a);
  });

  for (let j = 0; j < N; j++) {
    for (let i = 0; i < N; i++) {
      const x = x0 + i * step, y = y0 + j * step;
      POS.push(x, heightAt(E, x, y), -y);
      UV.push(x / 24, y / 24);
      let c = BARE;
      for (const a of sorted) {
        if (a.pts.length > 2 && pointInRing(x, y, a.pts)) c = COVER[a.kind] || c;
      }
      COL.push(c[0], c[1], c[2]);
    }
  }
  // the hole the inner ring fills, in this grid's own index space
  const holeLo = opts.ring === 'outer' ? Math.floor((E.x0 - x0) / step) : -1;
  const holeHi = opts.ring === 'outer' ? Math.ceil((E.x0 + span - x0) / step) : -1;
  const holeLoY = opts.ring === 'outer' ? Math.floor((E.y0 - y0) / step) : -1;
  const holeHiY = opts.ring === 'outer' ? Math.ceil((E.y0 + span - y0) / step) : -1;
  for (let j = 0; j < N - 1; j++) {
    for (let i = 0; i < N - 1; i++) {
      if (opts.ring === 'outer' &&
          i >= holeLo && i + 1 <= holeHi && j >= holeLoY && j + 1 <= holeHiY) continue;
      const a = j * N + i, b = a + 1, c = a + N, d = c + 1;
      // WINDING: (a,c,b) gives a DOWNWARD normal here and the terrain renders
      // black — lit from underneath. Verified by hand: with vertices at
      // (x, h, -y), cross(b-a, c-a) points +Y and cross(c-a, b-a) points -Y.
      IDX.push(a, b, c, b, d, c);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(POS), 3));
  g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(UV), 2));
  g.setAttribute('color', new THREE.BufferAttribute(new Float32Array(COL), 3));
  g.setIndex(N * N > 65535 ? new THREE.Uint32BufferAttribute(IDX, 1)
                           : new THREE.Uint16BufferAttribute(IDX, 1));
  g.computeVertexNormals();
  g.computeBoundingSphere();
  return g;
}

/** Walls for many footprints, with FACADE UVs, as one merged geometry.
 *
 * NOT ExtrudeGeometry. Extrude gives you the shape but not the UVs — and the
 * UVs are the entire point of a facade pass. Walls are built by hand so that
 * U runs along the wall in metres and V runs up it in metres, divided by the
 * trim sheet's real-world tile size. A 3.2 m storey is then a 3.2 m storey on
 * screen, and the window rows line up with the floors the building actually has.
 */
function wallsGeometry(list, tileW, tileH, E) {
  const POS = [], UV = [], NOR = [], IDX = [];
  let base = 0;
  for (const b of list) {
    const pts = cleanRing(b.pts);
    if (!pts) continue;
    const h = b.h != null ? b.h : (EST_H[b.kind] ?? EST_DEFAULT);
    const ring = ringArea2(pts) < 0 ? pts.slice().reverse() : pts;
    // Sit on the ground, and sink 1 m so a building on a slope never shows a
    // gap on its downhill side. Sampling the MINIMUM under the footprint rather
    // than the centroid is what stops that gap.
    let g0 = Infinity;
    for (const [x, y] of ring) g0 = Math.min(g0, heightAt(E, x, y));
    g0 -= 1.0;
    let run = 0;
    for (let i = 0; i < ring.length; i++) {
      const [x0, y0] = ring[i];
      const [x1, y1] = ring[(i + 1) % ring.length];
      const dx = x1 - x0, dy = y1 - y0;
      const len = Math.hypot(dx, dy);
      if (len < 0.05) continue;
      // outward normal for a CCW ring in x/east, y/north, before the z flip
      const nx = dy / len, nz = dx / len;
      const u0 = run / tileW, u1 = (run + len) / tileW, v1 = h / tileH;
      POS.push(x0, g0, -y0,  x1, g0, -y1,  x1, g0 + h, -y1,  x0, g0 + h, -y0);
      UV.push(u0, 0,  u1, 0,  u1, v1,  u0, v1);
      for (let k = 0; k < 4; k++) NOR.push(nx, 0, nz);
      IDX.push(base, base + 1, base + 2, base, base + 2, base + 3);
      base += 4;
      run += len;
    }
  }
  if (!POS.length) return null;
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(POS), 3));
  g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(UV), 2));
  g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(NOR), 3));
  g.setIndex(base > 65535 ? new THREE.Uint32BufferAttribute(IDX, 1)
                          : new THREE.Uint16BufferAttribute(IDX, 1));
  g.computeBoundingSphere();
  return g;
}

/** Flat roof caps at each building's height. */
function roofsGeometry(list, E) {
  const geos = [];
  for (const b of list) {
    const pts = cleanRing(b.pts);
    if (!pts) continue;
    const h = b.h != null ? b.h : (EST_H[b.kind] ?? EST_DEFAULT);
    const ring = ringArea2(pts) < 0 ? pts.slice().reverse() : pts;
    let g0 = Infinity;
    for (const [x, y] of ring) g0 = Math.min(g0, heightAt(E, x, y));
    const shape = new THREE.Shape(ring.map(([x, y]) => new THREE.Vector2(x, y)));
    const g = new THREE.ShapeGeometry(shape);
    g.rotateX(-Math.PI / 2);
    g.translate(0, g0 - 1.0 + h, 0);
    // roof UVs in metres, so the concrete tiles at a believable scale
    const p = g.attributes.position;
    const uv = new Float32Array(p.count * 2);
    for (let i = 0; i < p.count; i++) {
      uv[i * 2] = p.getX(i) / 8;
      uv[i * 2 + 1] = p.getZ(i) / 8;
    }
    g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
    geos.push(g);
  }
  return geos.length ? mergeGeometries(geos) : null;
}

/** Minimal merge — avoids pulling in BufferGeometryUtils for one function. */
function mergeGeometries(geos) {
  let vcount = 0, icount = 0;
  for (const g of geos) {
    vcount += g.attributes.position.count;
    icount += g.index ? g.index.count : g.attributes.position.count;
  }
  const pos = new Float32Array(vcount * 3);
  const nor = new Float32Array(vcount * 3);
  const uvs = new Float32Array(vcount * 2);
  // CARRY VERTEX COLOUR. This helper handled position, normal and uv only, and
  // the moment the terrain was built as two LOD rings and merged, the whole
  // ground went **black** — a material compiled with `vertexColors: true` and no
  // `color` attribute reads zero. The ground cover is painted per vertex, so
  // dropping it silently deletes every park, verge and patch of grass.
  const anyCol = geos.some((g) => g.attributes.color);
  const col = anyCol ? new Float32Array(vcount * 3).fill(1) : null;
  const idx = vcount > 65535 ? new Uint32Array(icount) : new Uint16Array(icount);
  let vo = 0, io = 0;
  for (const g of geos) {
    const p = g.attributes.position, n = g.attributes.normal, u = g.attributes.uv;
    pos.set(p.array.subarray(0, p.count * 3), vo * 3);
    if (n) nor.set(n.array.subarray(0, n.count * 3), vo * 3);
    if (u) uvs.set(u.array.subarray(0, u.count * 2), vo * 2);
    if (col && g.attributes.color) {
      col.set(g.attributes.color.array.subarray(0, p.count * 3), vo * 3);
    }
    if (g.index) {
      for (let i = 0; i < g.index.count; i++) idx[io++] = g.index.array[i] + vo;
    } else {
      for (let i = 0; i < p.count; i++) idx[io++] = i + vo;
    }
    vo += p.count;
    g.dispose();
  }
  const out = new THREE.BufferGeometry();
  out.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  out.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
  out.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
  if (col) out.setAttribute('color', new THREE.BufferAttribute(col, 3));
  out.setIndex(new THREE.BufferAttribute(idx, 1));
  out.computeBoundingSphere();
  return out;
}

/**
 * Resample a centreline so no segment is longer than `step` metres.
 *
 * SAME LESSON AS THE AREAS, learned twice. An OSM way can run 50 m or more
 * between nodes, and a ribbon built straight between two terrain samples cuts
 * through every hill in between — roads burst out of hillsides and vanish into
 * them. Anything draped on terrain has to be subdivided FIRST, at a spacing
 * finer than the terrain's own detail.
 */
function densify(pts, step = 8) {
  if (pts.length < 2) return pts;
  const out = [pts[0]];
  for (let i = 1; i < pts.length; i++) {
    const [x0, y0] = pts[i - 1], [x1, y1] = pts[i];
    const d = Math.hypot(x1 - x0, y1 - y0);
    const n = Math.max(1, Math.ceil(d / step));
    for (let k = 1; k <= n; k++) {
      out.push([x0 + (x1 - x0) * (k / n), y0 + (y1 - y0) * (k / n)]);
    }
  }
  return out;
}

/** Flat ribbon along a centreline, at `lift` metres, `w` metres wide. */
function ribbon(pts, w, lift, E) {
  // RIBBONS HAD NO UVs. A material with a `map` and no uv attribute samples one
  // corner texel for the whole surface, so the footways rendered as a flat dark
  // wedge — which looks like bad geometry or bad lighting and is neither. Found
  // by raycasting the wedge rather than guessing at it again.
  // U runs ACROSS the width, V runs ALONG the length in metres, so the surface
  // tiles at a believable scale however long the way is.
  const hw = w / 2, pos = [], uv = [], idx = [];
  let run = 0;
  for (let i = 0; i < pts.length; i++) {
    const [ax, ay] = pts[Math.max(i - 1, 0)];
    const [bx, by] = pts[Math.min(i + 1, pts.length - 1)];
    const dx = bx - ax, dy = by - ay;
    const L = Math.hypot(dx, dy) || 1;
    const nx = -dy / L, ny = dx / L;
    const [x, y] = pts[i];
    // per-vertex ground sample: a road laid flat across a hill floats at one
    // end and buries itself at the other
    pos.push(x + nx * hw, heightAt(E, x + nx * hw, y + ny * hw) + lift, -(y + ny * hw));
    pos.push(x - nx * hw, heightAt(E, x - nx * hw, y - ny * hw) + lift, -(y - ny * hw));
    if (i > 0) run += Math.hypot(x - pts[i - 1][0], y - pts[i - 1][1]);
    uv.push(0, run / 4, 1, run / 4);
  }
  for (let i = 0; i < pts.length - 1; i++) {
    const a = i * 2;
    idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2);
  }
  return { pos, uv, idx };
}

function ribbonsGeometry(ways, liftFn, widthFn, E) {
  const POS = [], UV = [], IDX = [];
  let base = 0;
  for (const w of ways) {
    if (!w.pts || w.pts.length < 2) continue;
    const { pos, uv, idx } = ribbon(densify(w.pts), widthFn(w), liftFn(w), E);
    POS.push(...pos);
    UV.push(...uv);
    for (const i of idx) IDX.push(i + base);
    base += pos.length / 3;
  }
  if (!POS.length) return null;
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(POS), 3));
  g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(UV), 2));
  g.setIndex(base > 65535 ? new THREE.Uint32BufferAttribute(IDX, 1)
                          : new THREE.Uint16BufferAttribute(IDX, 1));
  g.computeVertexNormals();
  g.computeBoundingSphere();
  return g;
}

function areasGeometry(list, lift, E) {
  const geos = [];
  for (const a of list) {
    const pts = cleanRing(a.pts);
    if (!pts) continue;
    const ring = ringArea2(pts) < 0 ? pts.slice().reverse() : pts;
    const shape = new THREE.Shape(ring.map(([x, y]) => new THREE.Vector2(x, y)));
    const g = new THREE.ShapeGeometry(shape);
    g.rotateX(-Math.PI / 2);
    // drape: lift each vertex onto the terrain
    const pa = g.attributes.position;
    for (let i = 0; i < pa.count; i++) {
      pa.setY(i, heightAt(E, pa.getX(i), -pa.getZ(i)) + lift);
    }
    pa.needsUpdate = true;
    geos.push(g);
  }
  return geos.length ? mergeGeometries(geos) : null;
}

/**
 * Build the whole location. Returns { group, stats, route }.
 * `route` is the longest way — a candidate line for the run, same choice the
 * Blender blockout makes, so the two previews agree.
 */
export function buildCity(world, opts = {}) {
  const group = new THREE.Group();
  const stats = { draws: 0, tris: 0, surveyed: 0, estimated: 0 };

  const addMesh = (geo, mat, name) => {
    if (!geo) return null;
    const m = new THREE.Mesh(geo, mat);
    m.name = name;
    m.castShadow = opts.shadows !== false;
    m.receiveShadow = true;
    group.add(m);
    stats.draws++;
    stats.tris += (geo.index ? geo.index.count : geo.attributes.position.count) / 3;
    return m;
  };

  // ── REAL MATERIALS: PBR, lit by a sun and a sky. Client, 10-02: "I need real
  // materials." No textures yet — this is massing under correct lighting, which
  // is what tells you whether the geometry and the scale are right. Trim-sheet
  // facades come next and plug into these same slots.
  const tex = (p, rx, ry) => {
    const t = new THREE.TextureLoader().load(p);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8;
    if (rx) t.repeat.set(rx, ry);
    return t;
  };
  const matRoof = new THREE.MeshStandardMaterial({
    map: tex(asset('art/pbr/rough_concrete/diff.jpg')), roughness: 0.95 });
  // Asphalt has to read DARK AGAINST THE GROUND, not merge with it. The first
  // pass had ground 0x23231f and road 0x2b2b30 — nearly the same luma — which
  // looked acceptable from above and became a sea of black at eye level, where
  // the game is actually played. Always judge surface contrast from the runner
  // camera, never the overview.
  const matRoad = new THREE.MeshStandardMaterial({
    map: tex(asset('art/pbr/asphalt_02/diff.jpg')), color: 0x9a9a9a, roughness: 0.95 });
  const matFoot = new THREE.MeshStandardMaterial({
    map: tex(asset('art/pbr/concrete_pavement/diff.jpg')), roughness: 0.95 });
  const matPark = new THREE.MeshStandardMaterial({ color: 0x2f5327, roughness: 0.97 });
  const matWater = new THREE.MeshStandardMaterial({ color: 0x1d3f5c, roughness: 0.12, metalness: 0.5 });
  // ── A NEUTRAL DETAIL MAP, or the vertex colours never show ────────────────
  // Ground cover is carried by vertex colour, and `map` MULTIPLIES it. The
  // concrete scan is a strong tan, so grey granite came out tan, grass came out
  // tan, everything came out tan — and it reads as "the painting is not
  // working" when in fact the painting was fine and the texture was shouting
  // over it. A detail map for a tinted surface has to be neutral: grain only.
  const grainTexture = () => {
    // MULTI-SCALE, OR IT VANISHES AT ALTITUDE. This was one octave of per-pixel
    // white noise at repeat 90 — detail finer than a screen pixel the moment the
    // camera leaves the ground, so it averaged to flat grey and bare ground read
    // as paper. That is a large part of the client's "thin lines over each
    // other… it doesn't look finished": the roads had detail and the ground had
    // none, so the roads were the only thing the eye could find.
    // Three octaves: broad patches that survive a drone shot, mid-scale mottle,
    // and the original fine grain for when she is standing on it. Still NEUTRAL
    // grey — this multiplies the vertex colours that carry the ground cover, and
    // any hue here tints every surface in the world.
    const n = 512, cv = document.createElement('canvas');
    cv.width = cv.height = n;
    const ctx = cv.getContext('2d');
    const img = ctx.createImageData(n, n);
    let seed = 1337;
    const rnd = () => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return (seed >> 16) / 32768; };
    // value-noise octave: a coarse lattice, smoothly interpolated
    const octave = (cells) => {
      const g = new Float32Array((cells + 1) * (cells + 1));
      for (let i = 0; i < g.length; i++) g[i] = rnd();
      const sm = (t) => t * t * (3 - 2 * t);                 // smoothstep
      return (x, y) => {
        const fx = x / n * cells, fy = y / n * cells;
        const ix = Math.floor(fx), iy = Math.floor(fy);
        const tx = sm(fx - ix), ty = sm(fy - iy);
        const a = g[iy * (cells + 1) + ix],       b = g[iy * (cells + 1) + ix + 1];
        const c = g[(iy + 1) * (cells + 1) + ix], d = g[(iy + 1) * (cells + 1) + ix + 1];
        return (a + (b - a) * tx) + ((c + (d - c) * tx) - (a + (b - a) * tx)) * ty;
      };
    };
    const o1 = octave(4), o2 = octave(16);
    for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
      const i = y * n + x;
      // 0.55 broad + 0.30 mid + 0.15 fine, centred on mid grey
      const v = 128 + (o1(x, y) - 0.5) * 62 + (o2(x, y) - 0.5) * 34 + (rnd() - 0.5) * 17;
      const c = Math.max(70, Math.min(205, v)) | 0;
      img.data[i * 4] = img.data[i * 4 + 1] = img.data[i * 4 + 2] = c;
      img.data[i * 4 + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    const t = new THREE.CanvasTexture(cv);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.anisotropy = 8;
    // One tile per ~70 m: the broad octave then reads at roughly 17 m, which is
    // a patch you can see from the air and still walk across.
    t.repeat.set(11, 11);
    return t;
  };
  const matGround = new THREE.MeshStandardMaterial({
    map: grainTexture(), color: 0xffffff, vertexColors: true, roughness: 0.97 });

  const R = world.location.radius_m;
  const E = world.elevation || null;
  stats.relief = E ? +(Math.max(...E.z) - Math.min(...E.z)).toFixed(0) : 0;
  if (E) {
    const t = new THREE.Mesh(terrainGeometry(E, world.areas), matGround);
    t.receiveShadow = true; t.castShadow = true; t.name = 'terrain';
    group.add(t); stats.draws++;
    // was omitted — the terrain is the biggest mesh in the scene and was not
    // being counted, so every triangle figure quoted so far was short
    stats.tris += t.geometry.index.count / 3;
    // (no skirt — the terrain mesh itself extends past the sampled grid)
  } else {
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(R * 4, R * 4), matGround);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    ground.name = 'ground_FLAT_no_elevation_data';
    group.add(ground); stats.draws++;
  }

  // Ground cover is PAINTED on the terrain above — no separate area meshes.

  // ── THE LEVEL FIRST, because it decides what is worth building ──────────
  // A location is extracted at a 350-450 m radius; a level is a 432 m ribbon
  // through it, and the runner camera never leaves that ribbon. Everything out
  // of sight of the route is geometry nobody will ever see, paid for on every
  // frame of a phone's budget — so the route has to exist before the city does.
  let level = null, nearRoute = null;
  if (opts.level) {
    level = buildLevel(world, heightAt, E, opts.level === true ? {} : opts.level);
    if (level) {
      stats.level = level.stats;
      if (opts.cull !== false) nearRoute = corridorFilter(level, opts.cullBandM ?? 160);
    }
  }
  // Anything with a footprint is kept if ANY of its points is in the band —
  // a building half in view must not pop out of existence.
  const inBand = (pts) => !nearRoute || pts.some(([x, y]) => nearRoute(x, y));
  const culled = { buildings: 0, props: 0, ways: 0 };

  const widthOf = (w) => (w.lanes ? w.lanes * LANE_M : (CLASS_W[w.kind] ?? 6));
  const roadsIn = world.roads.filter((w) => {
    if (inBand(w.pts)) return true; culled.ways++; return false;
  });
  const carriage = roadsIn.filter((w) => !FOOT_KINDS.has(w.kind));
  const foot = roadsIn.filter((w) => FOOT_KINDS.has(w.kind));
  addMesh(ribbonsGeometry(carriage, () => 0.18, widthOf, E), matRoad, 'roads');
  addMesh(ribbonsGeometry(foot, () => 0.26, widthOf, E), matFoot, 'footways');

  // ── FACADES: one draw call per style, chosen by height ───────────────────
  // Low-rise brick, mid-rise concrete, tall glass. Three wall meshes and one
  // roof mesh for every building in the location.
  const buildingsIn = world.buildings.filter((b) => {
    if (inBand(b.pts)) return true; culled.buildings++; return false;
  });
  stats.surveyed = buildingsIn.filter((b) => b.h != null).length;
  stats.estimated = buildingsIn.filter((b) => b.h == null).length;

  // ── HERO LANDMARKS first, and excluded from the generic pass below ───────
  // A landmark IS its shape, so it gets bespoke geometry on its real footprint
  // rather than an extrusion with a nice texture.
  // HERO LANDMARKS ARE NEVER CULLED. The stadium is why the location exists and
  // it is visible from everywhere; dropping it because its footprint sits
  // outside a 160 m band would delete the level's whole reason for being.
  for (const b of world.buildings) {
    if ((HEROES[`way/${b.id}`] || HEROES[`relation/${b.id}`]) && !buildingsIn.includes(b)) {
      buildingsIn.push(b); culled.buildings--;
    }
  }
  const heroMats = heroMaterials(THREE);
  const heroIds = new Set();
  stats.heroes = 0;
  for (const b of buildingsIn) {
    const hero = HEROES[`way/${b.id}`] || HEROES[`relation/${b.id}`];
    if (!hero) continue;
    heroIds.add(b.id);
    for (const m of hero.build(b, THREE, heroMats)) {
      m.castShadow = true; m.receiveShadow = true;
      m.name = 'hero_' + hero.name.replace(/\s+/g, '_');
      group.add(m);
      stats.draws++;
      stats.tris += (m.geometry.index ? m.geometry.index.count
                                      : m.geometry.attributes.position.count) / 3;
    }
    stats.heroes++;
  }

  const generic = buildingsIn.filter((b) => !heroIds.has(b.id));
  let lo = 0;
  for (const f of FACADES) {
    const band = generic.filter((b) => {
      const h = heightOfB(b);
      return h > lo && h <= f.max;
    });
    lo = f.max;
    if (!band.length) continue;
    const [tw, th] = tileOf(f.file);
    const mat = new THREE.MeshStandardMaterial({
      map: tex(asset('art/facades/' + f.file)), roughness: 0.78, metalness: 0.04 });
    addMesh(wallsGeometry(band, tw, th, E), mat, 'walls_' + f.file.split('_')[0]);
  }
  addMesh(roofsGeometry(generic, E), matRoof, 'roofs');

  // ── street furniture, instanced ──
  const propsIn = (world.props || []).filter((p) => {
    if (!nearRoute || nearRoute(p.p[0], p.p[1])) return true; culled.props++; return false;
  });
  const pr = buildProps(propsIn, heightAt, E);
  if (pr.stats.count) {
    group.add(pr.group);
    stats.draws += pr.stats.draws;
    stats.tris += pr.stats.tris;
    stats.props = pr.stats.count;
    stats.propKinds = pr.stats.kinds;
  } else { stats.props = 0; stats.propKinds = 0; }

  // ── crowds and traffic, instanced and on rails ──
  // Off by default so every measurement of the CITY stays comparable to the
  // ones already recorded; `?life=1` turns it on.
  let life = null;
  if (opts.life) {
    life = buildLife(world, heightAt, E, opts.life === true ? {} : opts.life);
    group.add(life.group);
    stats.draws += life.stats.draws;
    stats.tris += life.stats.tris;
    stats.life = life.stats;
  }

  // ── the level gizmo, drawn last so it sits over the world ───────────────
  if (level && opts.levelGizmo !== false) {
    const gz = levelGizmo(level, heightAt, E);
    group.add(gz);
    stats.draws += gz.children.length;
  }

  stats.culled = culled;
  stats.cullBandM = nearRoute ? nearRoute.bandM : null;

  // candidate route — the longest way in the extract
  let route = null, best = 0;
  for (const w of world.roads) {
    let d = 0;
    for (let i = 1; i < w.pts.length; i++) {
      d += Math.hypot(w.pts[i][0] - w.pts[i - 1][0], w.pts[i][1] - w.pts[i - 1][1]);
    }
    if (d > best) { best = d; route = w; }
  }
  return { group, stats, route, routeLength: best, life, level };
}

/** Sun + sky, sized to the location. */
export function lightRig(scene, R, { azimuth = -0.6, elevation = 0.95 } = {}) {
  // SHADOWS WENT PURE BLACK at eye level with hemisphere alone — the sun's
  // shadow had nothing filling it, so half the frame was a void. Outdoors the
  // sky IS the fill, so the hemisphere carries real intensity and the sun comes
  // down to match. Judge this from the runner camera; from above it looked fine.
  // SKY 0.75 / SUN 3.4, NOT 2.1 / 2.0. At parity the fill was as strong as the
  // key, so shadows landed at roughly half brightness and NOTHING READ AS
  // GROUNDED — the client's words were "thin lines over each other… it doesn't
  // look finished". Shadows were rendering the whole time (proved by diffing
  // castShadow on against off: 11.6% of pixels change); they were simply being
  // washed out. Swept four balances at one camera and measured ground-luminance
  // spread: overhead luma std 60.7 -> 69.7 and the 5th percentile 29 -> 13,
  // which is the difference between a hint and a shadow.
  //
  // 1.0 RATHER THAN LOWER, and the reason is measured: the sweep also watched a
  // street canyon at Apache from the RUNNER camera, which is where the old
  // comment warned a thin sky turns shadow into a void. That canyon sits at
  // ~51% near-black — AND IT ALREADY DID AT 2.1, so the darkness there is not
  // caused by this balance and cannot be fixed by raising the fill; it is a
  // separate problem (unlit north faces in a deep street). Below 1.0 the canyon
  // does start to lose: 0.75 pushed it to 57%. So 1.0 takes most of the shadow
  // structure while leaving the worst-case view no worse than it was.
  // Judge any change to these two numbers from the RUNNER camera, not above.
  scene.add(new THREE.HemisphereLight(0xbcd4ef, 0x6a6354, 1.0));
  const sun = new THREE.DirectionalLight(0xfff2dc, 3.2);
  const d = R * 1.2;
  sun.position.set(Math.cos(azimuth) * d, Math.sin(elevation) * d * 1.3, Math.sin(azimuth) * d);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  // Without a normal bias a 2048 map over a 700 m span self-shadows into acne
  // on every near-flat surface — the terrain most of all.
  sun.shadow.normalBias = 0.6;
  const c = sun.shadow.camera;
  c.left = -R; c.right = R; c.top = R; c.bottom = -R; c.near = 1; c.far = d * 4;
  scene.add(sun);
  return sun;
}
