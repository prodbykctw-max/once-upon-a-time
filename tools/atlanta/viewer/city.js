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

/** Extrude many footprints into one merged geometry. */
function buildingsGeometry(list) {
  const geos = [];
  for (const b of list) {
    const pts = cleanRing(b.pts);
    if (!pts) continue;
    const h = b.h != null ? b.h : (EST_H[b.kind] ?? EST_DEFAULT);
    // Shape wants CCW for the outer ring; ExtrudeGeometry triangulates with
    // earcut, which is sign-sensitive the same way bmesh was.
    const ring = ringArea2(pts) < 0 ? pts.slice().reverse() : pts;
    const shape = new THREE.Shape(ring.map(([x, y]) => new THREE.Vector2(x, y)));
    const g = new THREE.ExtrudeGeometry(shape, { depth: h, bevelEnabled: false });
    // world.json is x=east, y=north, z=up. three.js is y-up, so rotate the
    // whole thing once here rather than swizzling every coordinate.
    g.rotateX(-Math.PI / 2);
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
  const idx = vcount > 65535 ? new Uint32Array(icount) : new Uint16Array(icount);
  let vo = 0, io = 0;
  for (const g of geos) {
    const p = g.attributes.position, n = g.attributes.normal;
    pos.set(p.array.subarray(0, p.count * 3), vo * 3);
    if (n) nor.set(n.array.subarray(0, n.count * 3), vo * 3);
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
  out.setIndex(new THREE.BufferAttribute(idx, 1));
  out.computeBoundingSphere();
  return out;
}

/** Flat ribbon along a centreline, at `lift` metres, `w` metres wide. */
function ribbon(pts, w, lift) {
  const hw = w / 2, pos = [], idx = [];
  for (let i = 0; i < pts.length; i++) {
    const [ax, ay] = pts[Math.max(i - 1, 0)];
    const [bx, by] = pts[Math.min(i + 1, pts.length - 1)];
    const dx = bx - ax, dy = by - ay;
    const L = Math.hypot(dx, dy) || 1;
    const nx = -dy / L, ny = dx / L;
    const [x, y] = pts[i];
    pos.push(x + nx * hw, lift, -(y + ny * hw));
    pos.push(x - nx * hw, lift, -(y - ny * hw));
  }
  for (let i = 0; i < pts.length - 1; i++) {
    const a = i * 2;
    idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2);
  }
  return { pos, idx };
}

function ribbonsGeometry(ways, liftFn, widthFn) {
  const POS = [], IDX = [];
  let base = 0;
  for (const w of ways) {
    if (!w.pts || w.pts.length < 2) continue;
    const { pos, idx } = ribbon(w.pts, widthFn(w), liftFn(w));
    POS.push(...pos);
    for (const i of idx) IDX.push(i + base);
    base += pos.length / 3;
  }
  if (!POS.length) return null;
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(POS), 3));
  g.setIndex(base > 65535 ? new THREE.Uint32BufferAttribute(IDX, 1)
                          : new THREE.Uint16BufferAttribute(IDX, 1));
  g.computeVertexNormals();
  g.computeBoundingSphere();
  return g;
}

function areasGeometry(list, lift) {
  const geos = [];
  for (const a of list) {
    const pts = cleanRing(a.pts);
    if (!pts) continue;
    const ring = ringArea2(pts) < 0 ? pts.slice().reverse() : pts;
    const shape = new THREE.Shape(ring.map(([x, y]) => new THREE.Vector2(x, y)));
    const g = new THREE.ShapeGeometry(shape);
    g.rotateX(-Math.PI / 2);
    g.translate(0, lift, 0);
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
  const matSurveyed = new THREE.MeshStandardMaterial({ color: 0x9a978f, roughness: 0.82, metalness: 0.03 });
  const matEstimated = new THREE.MeshStandardMaterial({ color: 0xb4825c, roughness: 0.88, metalness: 0.0 });
  // Asphalt has to read DARK AGAINST THE GROUND, not merge with it. The first
  // pass had ground 0x23231f and road 0x2b2b30 — nearly the same luma — which
  // looked acceptable from above and became a sea of black at eye level, where
  // the game is actually played. Always judge surface contrast from the runner
  // camera, never the overview.
  const matRoad = new THREE.MeshStandardMaterial({ color: 0x24242a, roughness: 0.93, metalness: 0.0 });
  const matFoot = new THREE.MeshStandardMaterial({ color: 0x8d8a85, roughness: 0.95 });
  const matPark = new THREE.MeshStandardMaterial({ color: 0x2f5327, roughness: 0.97 });
  const matWater = new THREE.MeshStandardMaterial({ color: 0x1d3f5c, roughness: 0.12, metalness: 0.5 });
  const matGround = new THREE.MeshStandardMaterial({ color: 0x4a4740, roughness: 0.98 });

  const R = world.location.radius_m;
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(R * 4, R * 4), matGround);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  ground.name = 'ground_FLAT_no_elevation_data';
  group.add(ground); stats.draws++;

  addMesh(areasGeometry(world.areas.filter((a) => a.kind !== 'water'), 0.04), matPark, 'areas_green');
  addMesh(areasGeometry(world.areas.filter((a) => a.kind === 'water'), 0.05), matWater, 'areas_water');

  const widthOf = (w) => (w.lanes ? w.lanes * LANE_M : (CLASS_W[w.kind] ?? 6));
  const carriage = world.roads.filter((w) => !FOOT_KINDS.has(w.kind));
  const foot = world.roads.filter((w) => FOOT_KINDS.has(w.kind));
  addMesh(ribbonsGeometry(carriage, () => 0.08, widthOf), matRoad, 'roads');
  addMesh(ribbonsGeometry(foot, () => 0.13, widthOf), matFoot, 'footways');

  const surveyed = world.buildings.filter((b) => b.h != null);
  const estimated = world.buildings.filter((b) => b.h == null);
  stats.surveyed = surveyed.length;
  stats.estimated = estimated.length;
  addMesh(buildingsGeometry(surveyed), matSurveyed, 'buildings_surveyed');
  addMesh(buildingsGeometry(estimated), matEstimated, 'buildings_estimated');

  // candidate route — the longest way in the extract
  let route = null, best = 0;
  for (const w of world.roads) {
    let d = 0;
    for (let i = 1; i < w.pts.length; i++) {
      d += Math.hypot(w.pts[i][0] - w.pts[i - 1][0], w.pts[i][1] - w.pts[i - 1][1]);
    }
    if (d > best) { best = d; route = w; }
  }
  return { group, stats, route, routeLength: best };
}

/** Sun + sky, sized to the location. */
export function lightRig(scene, R, { azimuth = -0.6, elevation = 0.95 } = {}) {
  // SHADOWS WENT PURE BLACK at eye level with hemisphere alone — the sun's
  // shadow had nothing filling it, so half the frame was a void. Outdoors the
  // sky IS the fill, so the hemisphere carries real intensity and the sun comes
  // down to match. Judge this from the runner camera; from above it looked fine.
  scene.add(new THREE.HemisphereLight(0xbcd4ef, 0x6a6354, 2.1));
  const sun = new THREE.DirectionalLight(0xfff2dc, 2.0);
  const d = R * 1.2;
  sun.position.set(Math.cos(azimuth) * d, Math.sin(elevation) * d * 1.3, Math.sin(azimuth) * d);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  const c = sun.shadow.camera;
  c.left = -R; c.right = R; c.top = R; c.bottom = -R; c.near = 1; c.far = d * 4;
  scene.add(sun);
  return sun;
}
