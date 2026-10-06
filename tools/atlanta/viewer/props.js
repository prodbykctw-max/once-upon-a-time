// Street furniture, instanced — the thing that turns a massing model into a place.
//
// All of it comes free from OSM, which carries this as tagged nodes: around
// Mercedes-Benz Stadium alone there are 96 trees, 19 gates, 8 traffic signals,
// flagpoles and hydrants. Nothing here is bought, licensed or modelled from
// scratch; it is data that was already in the extract and was being thrown away.
//
// ONE InstancedMesh PER TYPE, so 96 trees cost ONE draw call. The budget is 150
// draw calls for the whole scene, and a mesh per tree would spend two thirds of
// it on foliage.
import * as THREE from './vendor/three.module.min.js';

/**
 * Deterministic hash → [0,1). Props must not reshuffle between loads.
 *
 * `Math.imul` is load-bearing. Written as a plain `*`, the product is ~9.6e17 —
 * a double — and the low bits are lost to float precision before `>>> 0` runs.
 * Measured over 20,000 samples that version returns a max of **0.49997**: it
 * cannot exceed a half. It shipped that way, so every tree was rotated within
 * 0..PI instead of 0..2PI and scaled in the bottom half of its range — a crowd
 * of trees all facing the same way, which reads as "instanced" and is exactly
 * what the variation is here to avoid. Fixed 10-06.
 */
function rnd(i, salt) {
  let h = (Math.imul(i, 374761393) + Math.imul(salt, 668265263)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}

function merge(parts) {
  const geos = [];
  for (const [g, tx] of parts) { g.applyMatrix4(tx); geos.push(g); }
  const pos = [], nor = [], idx = [];
  let base = 0;
  for (const g of geos) {
    const p = g.attributes.position, n = g.attributes.normal;
    for (let i = 0; i < p.count; i++) {
      pos.push(p.getX(i), p.getY(i), p.getZ(i));
      nor.push(n.getX(i), n.getY(i), n.getZ(i));
    }
    // NOT every three.js primitive is indexed — IcosahedronGeometry is not, and
    // assuming an index here threw "cannot read properties of null" at load,
    // which looks like a data problem and is a geometry-API one.
    if (g.index) {
      for (let i = 0; i < g.index.count; i++) idx.push(g.index.array[i] + base);
    } else {
      for (let i = 0; i < p.count; i++) idx.push(i + base);
    }
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

const T = (x, y, z) => new THREE.Matrix4().makeTranslation(x, y, z);

// ── prop shapes. Deliberately simple: at runner speed a tree is a trunk and a
//    mass of leaves, and anything more is triangles spent where nobody looks.
const SHAPES = {
  tree: () => merge([
    [new THREE.CylinderGeometry(0.22, 0.34, 4.2, 6), T(0, 2.1, 0)],
    [new THREE.IcosahedronGeometry(2.5, 0), T(0, 5.6, 0)],
    [new THREE.IcosahedronGeometry(1.8, 0), T(0.9, 7.2, 0.4)],
    [new THREE.IcosahedronGeometry(1.5, 0), T(-0.8, 6.9, -0.5)],
  ]),
  street_lamp: () => merge([
    [new THREE.CylinderGeometry(0.11, 0.15, 8, 6), T(0, 4, 0)],
    [new THREE.BoxGeometry(1.4, 0.18, 0.4), T(0.6, 8, 0)],
  ]),
  traffic_signals: () => merge([
    [new THREE.CylinderGeometry(0.12, 0.16, 6.2, 6), T(0, 3.1, 0)],
    [new THREE.BoxGeometry(0.44, 1.2, 0.3), T(0, 5.4, 0.2)],
  ]),
  bollard: () => merge([[new THREE.CylinderGeometry(0.11, 0.13, 1.0, 6), T(0, 0.5, 0)]]),
  gate: () => merge([
    [new THREE.CylinderGeometry(0.09, 0.09, 1.3, 5), T(-1.4, 0.65, 0)],
    [new THREE.CylinderGeometry(0.09, 0.09, 1.3, 5), T(1.4, 0.65, 0)],
    [new THREE.BoxGeometry(2.8, 0.1, 0.07), T(0, 1.0, 0)],
  ]),
  fire_hydrant: () => merge([
    [new THREE.CylinderGeometry(0.16, 0.2, 0.75, 6), T(0, 0.38, 0)],
    [new THREE.SphereGeometry(0.17, 6, 4), T(0, 0.8, 0)],
  ]),
  bench: () => merge([
    [new THREE.BoxGeometry(1.8, 0.09, 0.5), T(0, 0.45, 0)],
    [new THREE.BoxGeometry(1.8, 0.5, 0.08), T(0, 0.7, -0.22)],
    [new THREE.BoxGeometry(0.1, 0.45, 0.45), T(-0.75, 0.22, 0)],
    [new THREE.BoxGeometry(0.1, 0.45, 0.45), T(0.75, 0.22, 0)],
  ]),
  bus_stop: () => merge([
    [new THREE.BoxGeometry(3.2, 0.12, 1.5), T(0, 2.5, 0)],
    [new THREE.CylinderGeometry(0.07, 0.07, 2.5, 5), T(-1.5, 1.25, -0.6)],
    [new THREE.CylinderGeometry(0.07, 0.07, 2.5, 5), T(1.5, 1.25, -0.6)],
    [new THREE.BoxGeometry(3.2, 1.8, 0.06), T(0, 1.4, -0.72)],
  ]),
  flagpole: () => merge([[new THREE.CylinderGeometry(0.08, 0.13, 14, 6), T(0, 7, 0)]]),
  mast: () => merge([[new THREE.CylinderGeometry(0.2, 0.42, 26, 6), T(0, 13, 0)]]),
  waste_basket: () => merge([[new THREE.CylinderGeometry(0.28, 0.23, 0.85, 7), T(0, 0.42, 0)]]),
  billboard: () => merge([
    [new THREE.CylinderGeometry(0.2, 0.2, 5, 6), T(0, 2.5, 0)],
    [new THREE.BoxGeometry(6, 3, 0.2), T(0, 6.4, 0)],
  ]),
  fountain: () => merge([
    [new THREE.CylinderGeometry(2.2, 2.4, 0.6, 12), T(0, 0.3, 0)],
    [new THREE.CylinderGeometry(0.25, 0.35, 1.6, 8), T(0, 1.1, 0)],
  ]),
};

// OSM has many tags for one shape; map the rest onto the nearest match.
const ALIAS = {
  stop: 'traffic_signals', give_way: 'traffic_signals', lift_gate: 'gate',
  drinking_water: 'waste_basket', bicycle_parking: 'bollard',
  water_tower: 'mast', artwork: 'bollard', taxi: 'street_lamp',
};

const MAT = (THREE_) => ({
  tree:            new THREE.MeshStandardMaterial({ color: 0x3f5a2c, roughness: 0.95, flatShading: true }),
  street_lamp:     new THREE.MeshStandardMaterial({ color: 0x4a4e55, roughness: 0.6, metalness: 0.5 }),
  traffic_signals: new THREE.MeshStandardMaterial({ color: 0x33383f, roughness: 0.6, metalness: 0.4 }),
  bollard:         new THREE.MeshStandardMaterial({ color: 0x5a5f66, roughness: 0.7, metalness: 0.3 }),
  gate:            new THREE.MeshStandardMaterial({ color: 0x6b7078, roughness: 0.7, metalness: 0.3 }),
  fire_hydrant:    new THREE.MeshStandardMaterial({ color: 0xa8342c, roughness: 0.7 }),
  bench:           new THREE.MeshStandardMaterial({ color: 0x6b5338, roughness: 0.9 }),
  bus_stop:        new THREE.MeshStandardMaterial({ color: 0x8d9298, roughness: 0.5, metalness: 0.4 }),
  flagpole:        new THREE.MeshStandardMaterial({ color: 0xc9cdd2, roughness: 0.45, metalness: 0.6 }),
  mast:            new THREE.MeshStandardMaterial({ color: 0x8a8f96, roughness: 0.6, metalness: 0.5 }),
  waste_basket:    new THREE.MeshStandardMaterial({ color: 0x3f444a, roughness: 0.85 }),
  billboard:       new THREE.MeshStandardMaterial({ color: 0x6f757c, roughness: 0.7 }),
  fountain:        new THREE.MeshStandardMaterial({ color: 0x8d8880, roughness: 0.9 }),
});

/** Build every prop type as one InstancedMesh each. */
export function buildProps(props, heightAt, E) {
  const group = new THREE.Group();
  const stats = { draws: 0, tris: 0, count: 0, kinds: 0 };
  if (!props || !props.length) return { group, stats };

  const mats = MAT(THREE);
  const byKind = new Map();
  for (const p of props) {
    const k = SHAPES[p.k] ? p.k : (ALIAS[p.k] || null);
    if (!k) continue;
    if (!byKind.has(k)) byKind.set(k, []);
    byKind.get(k).push(p.p);
  }

  const dummy = new THREE.Object3D();
  for (const [kind, pts] of byKind) {
    const geo = SHAPES[kind]();
    const mesh = new THREE.InstancedMesh(geo, mats[kind], pts.length);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.name = 'props_' + kind;
    for (let i = 0; i < pts.length; i++) {
      const [x, y] = pts[i];
      dummy.position.set(x, heightAt(E, x, y), -y);
      // deterministic variation: a street of identical trees reads as wallpaper
      dummy.rotation.set(0, rnd(i, 7) * Math.PI * 2, 0);
      const s = kind === 'tree' ? 0.72 + rnd(i, 11) * 0.62 : 0.92 + rnd(i, 13) * 0.18;
      dummy.scale.set(s, kind === 'tree' ? 0.8 + rnd(i, 17) * 0.55 : s, s);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
    group.add(mesh);
    stats.draws++;
    stats.tris += (geo.index.count / 3) * pts.length;
    stats.count += pts.length;
  }
  stats.kinds = byKind.size;
  return { group, stats };
}
