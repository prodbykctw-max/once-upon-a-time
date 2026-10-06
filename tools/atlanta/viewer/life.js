// CROWDS AND TRAFFIC — the thing that makes it Atlanta rather than a model of Atlanta.
//
// Client, 10-06: "can we put procedural crowds and all that shit in the game
// traffic?" This is the measured answer. Both come free from data already in
// `world.json` and thrown away until now: the footway network (16.5 km at MBS)
// and the drivable network (12.8 km, 155 ways).
//
// ── THE BUDGET IS DRAW CALLS, NOT AGENTS ───────────────────────────────────
// The carried budget is 150 draw calls / 500k visible triangles / 60fps on a
// mid-range phone. A Mesh per pedestrian would blow the draw budget at 150
// people and the whole city would have to fit in what was left. One
// InstancedMesh per TYPE means the agent count is free in draw calls and costs
// only triangles and a per-frame matrix write — so the ceiling is set by what
// looks right, not by what the renderer can address.
//
// ── ANIMATION IS A VERTEX SHADER, NOT A SKELETON ───────────────────────────
// Skinned instancing needs a bone texture and a custom pipeline. A walk cycle
// does not: tag each vertex with the limb it belongs to (`aPart`) and swing
// that limb about its joint by `sin(time*rate + aPhase)`, where `aPhase` is a
// per-instance attribute. Zero CPU per limb, no skeleton, and the crowd stops
// reading as sliding chess pieces — which is the entire difference between
// "there are people" and "there are person-shaped objects".
import * as THREE from './vendor/three.module.min.js';

const FOOT_KINDS = new Set(['footway', 'path', 'pedestrian', 'steps', 'cycleway']);
const DRIVE_SKIP = new Set([...FOOT_KINDS, 'track', 'bridleway', 'construction', 'proposed']);

/**
 * Deterministic hash → [0,1). A crowd that reshuffles every load cannot be judged.
 *
 * EVERY STEP MUST STAY IN int32, hence `Math.imul`. The obvious spelling,
 * `h = (h ^ (h >> 13)) * 1274126177`, silently leaves int32: the product is
 * ~9.6e17, a double, and the low bits are gone to float precision before
 * `>>> 0` ever runs. Measured over 20,000 samples, that version returns
 * **min 0.00000, max 0.49997 — it can never exceed a half.** It does not throw,
 * it does not look wrong, and every caller quietly gets the bottom half of the
 * range it asked for. This one measures 0.00000..0.99997, flat across all ten
 * deciles.
 */
function rnd(i, salt) {
  let h = (Math.imul(i, 374761393) + Math.imul(salt, 668265263)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}

/** Cumulative-length table for a polyline, so position along it is O(log n). */
function pathOf(pts) {
  const cum = [0];
  for (let i = 1; i < pts.length; i++) {
    cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  }
  return { pts, cum, len: cum[cum.length - 1] };
}

/**
 * THE NETWORK, OR EVERY AGENT TELEPORTS.
 *
 * An OSM way is a fragment, not a route — MBS has 155 drivable ways averaging
 * 83 m. Wrapping `s` modulo the way's length is the obvious thing and it means
 * a car reaching the end of a block instantly reappears at its start. Measured:
 * at 6-13 m/s that is a pop roughly every 8 seconds PER AGENT, so with 140
 * vehicles something teleports several times a second.
 *
 * OSM ways already share endpoint coordinates where they meet, so the junctions
 * are in the data — they just have to be looked up. Link each way's ends to
 * every other way end within `TOL` and an agent leaving one way continues onto
 * a connected one. That is a turn, not a jump.
 *
 * O(n^2) over ways and done once at load: 155 ways is 24k distance tests.
 *
 * TOL IS SMALL ON PURPOSE, and the number came from the data. Measured over
 * MBS's 312 drivable and 638 foot endpoints, the nearest other endpoint is
 * within half a metre for 66% / 78% of them — OSM genuinely shares junction
 * coordinates. Widening the tolerance from 0.5 m to 9 m buys only 5% / 11%
 * more connections, and every one of those costs a hop that displaces the
 * agent by up to nine metres in a single frame, which is the exact pop this
 * function exists to remove. 2 m keeps 66% / 81% and bounds the jump.
 */
function linkNetwork(paths, TOL = 2) {
  const end = (p, which) => (which ? p.pts[p.pts.length - 1] : p.pts[0]);
  for (const p of paths) p.next = [[], []];   // [arriving at start, arriving at end]
  for (let i = 0; i < paths.length; i++) {
    for (let j = 0; j < paths.length; j++) {
      if (i === j) continue;
      for (const mine of [0, 1]) {
        const a = end(paths[i], mine);
        for (const theirs of [0, 1]) {
          const b = end(paths[j], theirs);
          if (Math.hypot(a[0] - b[0], a[1] - b[1]) <= TOL) {
            // entering path j at `theirs`: travel forward from a start,
            // backward from an end.
            paths[i].next[mine].push({ p: paths[j], fwd: theirs === 0 });
          }
        }
      }
    }
  }
  let linked = 0;
  for (const p of paths) if (p.next[0].length || p.next[1].length) linked++;
  return linked;
}

/**
 * Advance an agent along its path, turning onto a connected way at a junction
 * rather than wrapping. Falls back to the modulo wrap only where the way is an
 * isolated stub with nothing joined to it.
 */
export const EV = { hop: 0, deadEnd: 0, wrap: 0, maxHop: 0, hopSum: 0, hopN: 0,
                    deadSum: 0, deadN: 0 };

const _b4 = { x: 0, y: 0, h: 0 }, _af = { x: 0, y: 0, h: 0 };

function advance(a, dt) {
  a.s += a.v * dt;
  // EASE ACROSS THE LANE, DO NOT SNAP. Turning round at a dead end, or picking
  // the other side of a junction, flips the lateral offset — and snapping it is
  // a sideways jump of twice the offset, measured at up to 16.5 m on the widest
  // multi-lane road at MBS. It is the last visible discontinuity left once the
  // wrap is gone. 4 m/s of lateral drift crosses any lane in well under a
  // second and reads as a lane change, which is what it is.
  // Start the corner BEFORE it: inside the last 12 m of a way, steer toward
  // the centreline so the perpendicular flip at the junction costs nothing.
  // Snapping to 0 AT the junction merely moved the discontinuity from 16.5 m to
  // 8.3 m — the offset itself. 8 m/s of lateral over 12 m of approach is 7.4 m
  // of travel at the fastest road speed here, more than the widest lane offset
  // (4.95 m), so the agent is always on the centreline by the time it turns.
  const toEnd = a.v > 0 ? a.p.len - a.s : a.s;
  const want = toEnd < 12 ? 0 : a.ot;
  if (a.o !== want) {
    const step = 8 * dt, d = want - a.o;
    a.o = Math.abs(d) <= step ? want : a.o + Math.sign(d) * step;
  }
  for (let guard = 0; guard < 4; guard++) {    // a junction can be a short stub
    const p = a.p;
    if (a.s >= 0 && a.s <= p.len) return;
    // Sample the exit point with `s` CLAMPED, not as-is: `at()` wraps an
    // out-of-range `s` by design, so sampling it raw reports the far end of the
    // way the agent is leaving and makes every junction look like a 40 m
    // teleport. That measurement bug cost an hour of hunting a fault in a link
    // table that turned out to be exact (every junction gap 0.000 m).
    at(p, a.s > p.len ? p.len : 0, a.o, _b4);   // safe: `at` clamps, not wraps
    const leavingAt = a.s > p.len ? 1 : 0;     // which end we ran off
    const opts = p.next ? p.next[leavingAt] : null;
    if (!opts || !opts.length) {
      // A DEAD END REVERSES, IT DOES NOT WRAP. 29% of drivable way-ends have
      // nothing joined to them — cul-de-sacs, and ways cut by the edge of the
      // extract. Wrapping those to the far end of the same way is a jump of the
      // whole way length; measured at MBS that alone was most of 41 teleports a
      // second, the worst of them 451 m. Turning round is what a person or a
      // car actually does at a dead end, and it displaces nothing.
      a.s = leavingAt ? p.len : 0;
      a.v = -a.v;
      a.ot = -a.ot;                            // stay on your own side of the way
      at(p, a.s, a.o, _af);
      EV.deadEnd++;
      EV.deadSum += Math.hypot(_af.x - _b4.x, _af.y - _b4.y); EV.deadN++;
      return;
    }
    EV.hop++;
    const over = leavingAt ? a.s - p.len : -a.s;
    const n = opts[Math.floor(a.turn() * opts.length) % opts.length];
    a.p = n.p;
    // keep travelling in the same real-world direction: entering at the far
    // end means counting down, so the sign of `v` flips with it.
    if (n.fwd) { a.s = over; a.v = Math.abs(a.v); }
    else { a.s = n.p.len - over; a.v = -Math.abs(a.v); }
    a.ot = Math.abs(a.ot) * (a.v < 0 ? -1 : 1) * a.side;
    // GO THROUGH THE CORNER ON THE CENTRELINE. Two linked ways share their
    // junction coordinate exactly — measured, every gap is 0.000 m — but an
    // agent is drawn at `offset x perpendicular`, and the perpendicular swings
    // with the heading. Where the ways meet at a sharp angle that flips, so a
    // car in an outside lane jumps twice its offset sideways: 16.5 m on the
    // widest road at MBS, the last discontinuity left after the wrap was fixed.
    // At offset 0 both ways evaluate to the same point, so the corner is
    // continuous by construction and the agent eases back into its lane — which
    // is also what cutting a corner looks like.
    at(a.p, a.s, a.o, _af);
    const d = Math.hypot(_af.x - _b4.x, _af.y - _b4.y);
    if (d > EV.maxHop) EV.maxHop = d;
    EV.hopSum += d; EV.hopN++;
  }
  // fell out of the guard loop still off the end of a way
  EV.wrap++;
}

/** Point + heading at distance `s` along a path, with a lateral offset `o`. */
function at(path, s, o, out) {
  const { pts, cum, len } = path;
  // CLAMP, DO NOT WRAP. This used to be `((s % len) + len) % len`, which maps
  // s === len to **0** — the far end of the way. `advance` sets exactly that
  // value when an agent turns round at a dead end, so every one of those
  // reversals teleported the agent the whole length of its way: measured at
  // MBS, 85 of them in 10 seconds, the worst a 345 m jump. `advance` now owns
  // wrap-around entirely, so `at` only has to stay in bounds.
  s = s < 0 ? 0 : s > len ? len : s;
  let lo = 0, hi = cum.length - 1;
  while (lo < hi - 1) { const m = (lo + hi) >> 1; if (cum[m] <= s) lo = m; else hi = m; }
  const a = pts[lo], b = pts[lo + 1] || pts[lo];
  const seg = cum[lo + 1] - cum[lo] || 1;
  const f = (s - cum[lo]) / seg;
  let dx = (b[0] - a[0]) / seg, dy = (b[1] - a[1]) / seg;
  if (!Number.isFinite(dx)) { dx = 1; dy = 0; }
  // offset is to the RIGHT of travel: (dy, -dx) in the x/y (east/north) frame
  out.x = a[0] + (b[0] - a[0]) * f + dy * o;
  out.y = a[1] + (b[1] - a[1]) * f - dx * o;
  out.h = Math.atan2(dx, dy);           // heading, for a +Z-forward model
  return out;
}

// ── geometry helpers ───────────────────────────────────────────────────────
function box(w, h, d, x, y, z, part) {
  const g = new THREE.BoxGeometry(w, h, d);
  g.translate(x, y, z);
  const n = g.attributes.position.count;
  g.setAttribute('aPart', new THREE.BufferAttribute(new Float32Array(n).fill(part), 1));
  // the joint this part pivots about, in model space — a limb swings from the
  // hip or the shoulder, never from the floor
  const j = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { j[i * 3] = x; j[i * 3 + 1] = y + h / 2; j[i * 3 + 2] = z; }
  g.setAttribute('aJoint', new THREE.BufferAttribute(j, 3));
  return g;
}

function mergeTagged(parts) {
  const pos = [], nor = [], par = [], joi = [], idx = [];
  let base = 0;
  for (const g of parts) {
    const p = g.attributes.position, n = g.attributes.normal,
          a = g.attributes.aPart, j = g.attributes.aJoint;
    for (let i = 0; i < p.count; i++) {
      pos.push(p.getX(i), p.getY(i), p.getZ(i));
      nor.push(n.getX(i), n.getY(i), n.getZ(i));
      par.push(a.getX(i));
      joi.push(j.getX(i), j.getY(i), j.getZ(i));
    }
    // NOT every three.js primitive is indexed — the same trap props.js hit.
    if (g.index) for (let i = 0; i < g.index.count; i++) idx.push(g.index.array[i] + base);
    else for (let i = 0; i < p.count; i++) idx.push(i + base);
    base += p.count;
    g.dispose();
  }
  const out = new THREE.BufferGeometry();
  out.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3));
  out.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(nor), 3));
  out.setAttribute('aPart', new THREE.BufferAttribute(new Float32Array(par), 1));
  out.setAttribute('aJoint', new THREE.BufferAttribute(new Float32Array(joi), 3));
  out.setIndex(idx);
  out.computeBoundingSphere();
  return out;
}

// A walking figure at 1.0 m — scaled per instance to real heights. Parts:
// 0 torso+head (still) · 1/2 legs · 3/4 arms.
function personGeometry() {
  return mergeTagged([
    box(0.30, 0.42, 0.17, 0, 0.74, 0, 0),      // torso
    box(0.19, 0.19, 0.19, 0, 1.03, 0, 0),      // head
    box(0.11, 0.52, 0.13, -0.075, 0.27, 0, 1), // left leg
    box(0.11, 0.52, 0.13, 0.075, 0.27, 0, 2),  // right leg
    box(0.085, 0.40, 0.10, -0.195, 0.72, 0, 3),// left arm
    box(0.085, 0.40, 0.10, 0.195, 0.72, 0, 4), // right arm
  ]);
}

const VEHICLES = {
  sedan:  () => mergeTagged([box(1.80, 0.62, 4.40, 0, 0.62, 0, 0), box(1.62, 0.52, 2.30, 0, 1.18, -0.20, 0)]),
  suv:    () => mergeTagged([box(1.95, 0.85, 4.80, 0, 0.72, 0, 0), box(1.80, 0.70, 2.90, 0, 1.48, -0.10, 0)]),
  van:    () => mergeTagged([box(2.05, 1.55, 5.60, 0, 1.12, 0, 0), box(1.95, 0.55, 1.60, 0, 1.00, 2.10, 0)]),
  bus:    () => mergeTagged([box(2.55, 2.10, 11.0, 0, 1.55, 0, 0)]),
  pickup: () => mergeTagged([box(1.95, 0.78, 5.20, 0, 0.70, 0, 0), box(1.85, 0.66, 2.10, 0, 1.42, -0.95, 0)]),
};

// ── THE WALK, AS A SHADER PATCH ────────────────────────────────────────────
// `onBeforeCompile` keeps MeshStandardMaterial's lighting, shadows and the
// scene environment — rewriting the material from scratch would mean
// reimplementing all of it to get a leg to move.
function animateLimbs(mat, { rate = 1.0, swing = 0.85 } = {}) {
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uTime = { value: 0 };
    sh.uniforms.uRate = { value: rate };
    sh.uniforms.uSwing = { value: swing };
    mat.userData.sh = sh;
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', `#include <common>
        attribute float aPart;
        attribute vec3 aJoint;
        attribute float aPhase;
        attribute float aSpeed;
        uniform float uTime, uRate, uSwing;
        vec3 swingAbout(vec3 p, vec3 j, float ang){
          vec3 d = p - j;
          float c = cos(ang), s = sin(ang);
          // rotate in the model's YZ plane: a leg swings forward and back
          return j + vec3(d.x, d.y*c - d.z*s, d.y*s + d.z*c);
        }`)
      .replace('#include <begin_vertex>', `#include <begin_vertex>
        if (aPart > 0.5) {
          // Legs and arms oppose; left and right oppose. One sin, four phases.
          // ARMS SWING LESS THAN LEGS. Measured against the render at close
          // range: a single amplitude for both put the arms near horizontal —
          // the figure reads as sprinting or waving, not walking. Real gait is
          // roughly 25 deg at the hip and 20 at the shoulder, so the arms take
          // 0.55 of the leg's.
          float side = (aPart == 1.0 || aPart == 4.0) ? 1.0 : -1.0;
          float limb = (aPart >= 3.0) ? 0.55 : 1.0;
          float a = sin(uTime * uRate * aSpeed + aPhase) * uSwing * side * aSpeed * limb;
          transformed = swingAbout(transformed, aJoint, a);
        }`);
  };
  mat.customProgramCacheKey = () => 'limbs' + rate;
  return mat;
}

/**
 * Populate a location with pedestrians and traffic.
 * Returns { group, stats, update(dt) } — `update` is the per-frame cost.
 */
export function buildLife(world, heightAt, E, opts = {}) {
  const group = new THREE.Group();
  const PEDS = opts.peds ?? 260;
  const CARS = opts.cars ?? 90;
  const stats = { draws: 0, tris: 0, peds: 0, cars: 0, carMs: 0, pedMs: 0 };

  // ── paths ────────────────────────────────────────────────────────────────
  const footPaths = [], drivePaths = [];
  for (const w of world.roads) {
    if (w.pts.length < 2) continue;
    const p = pathOf(w.pts);
    if (p.len < 12) continue;                  // a 12 m stub is not a route
    if (FOOT_KINDS.has(w.kind) || w.foot) footPaths.push(p);
    else if (!DRIVE_SKIP.has(w.kind)) {
      // Capped at 4: OSM tags up to 8 lanes downtown, and `lanes/2` lane slots
      // put a car 11.5 m off the centreline, which is wider than the road is
      // drawn and makes every corner a sidestep.
      p.lanes = Math.min(4, w.lanes || (w.kind === 'service' ? 1 : 2));
      p.oneway = !!w.oneway;
      p.fast = /motorway|trunk|primary/.test(w.kind);
      drivePaths.push(p);
    }
  }
  // Pedestrians belong on footways; where a location has almost none, the
  // carriageway shoulder is where people actually walk anyway.
  const walkOn = footPaths.length ? footPaths : drivePaths;
  stats.footJunctions = linkNetwork(footPaths);
  stats.driveJunctions = linkNetwork(drivePaths);
  stats.footKm = +(footPaths.reduce((s, p) => s + p.len, 0) / 1000).toFixed(2);
  stats.driveKm = +(drivePaths.reduce((s, p) => s + p.len, 0) / 1000).toFixed(2);

  const dummy = new THREE.Object3D();
  const cur = { x: 0, y: 0, h: 0 };

  // ── PEDESTRIANS ──────────────────────────────────────────────────────────
  const peds = [];
  let pedMesh = null;
  if (walkOn.length && PEDS > 0) {
    const geo = personGeometry();
    // Palette, not one colour: a crowd in a single shirt reads as a clone army.
    // Per-instance colour is free — it rides the same InstancedMesh.
    const mat = animateLimbs(new THREE.MeshStandardMaterial({
      roughness: 0.82, metalness: 0.0, flatShading: true, vertexColors: false,
      // 0.44 rad is 25 deg at the hip — a walk. 0.80 was 46 deg and read as a
      // sprint, with the arms thrown out near horizontal.
    }), { rate: 4.6, swing: 0.44 });
    pedMesh = new THREE.InstancedMesh(geo, mat, PEDS);
    pedMesh.name = 'crowd';
    pedMesh.castShadow = true;
    pedMesh.receiveShadow = true;
    pedMesh.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(PEDS * 3), 3);
    const phase = new Float32Array(PEDS), speedA = new Float32Array(PEDS);
    const SHIRTS = [0x2f3d55, 0x7a3b33, 0x3d5742, 0xb0a48c, 0x45324a, 0x8f6b3f,
                    0x27516b, 0x6b2f45, 0xd2cdc2, 0x3a3a40];
    const c = new THREE.Color();
    for (let i = 0; i < PEDS; i++) {
      const p = walkOn[Math.floor(rnd(i, 3) * walkOn.length)];
      // Both sides of the path, both directions — a one-way crowd is a parade.
      const side = rnd(i, 5) < 0.5 ? 1 : -1;
      const v0 = (1.05 + rnd(i, 11) * 0.55) * (rnd(i, 13) < 0.5 ? 1 : -1);
      let turnN = i;
      const o0 = side * (0.6 + rnd(i, 9) * 1.1);
      peds.push({ p, s: rnd(i, 7) * p.len, side, o: o0, ot: o0,
                  v: v0, hgt: 1.58 + rnd(i, 17) * 0.30,
                  // which way they go at a junction: deterministic per agent
                  // per turn, so a reload reproduces the same city exactly.
                  turn: () => rnd(++turnN, 101) });
      phase[i] = rnd(i, 19) * Math.PI * 2;
      speedA[i] = 0.82 + rnd(i, 23) * 0.4;
      c.setHex(SHIRTS[Math.floor(rnd(i, 29) * SHIRTS.length)]);
      pedMesh.setColorAt(i, c);
    }
    geo.setAttribute('aPhase', new THREE.InstancedBufferAttribute(phase, 1));
    geo.setAttribute('aSpeed', new THREE.InstancedBufferAttribute(speedA, 1));
    group.add(pedMesh);
    stats.draws++;
    stats.tris += (geo.index.count / 3) * PEDS;
    stats.peds = PEDS;
  }

  // ── TRAFFIC ──────────────────────────────────────────────────────────────
  // One InstancedMesh per vehicle type. Five types = five draw calls for any
  // number of cars.
  const kinds = Object.keys(VEHICLES);
  const carMeshes = [], cars = [];
  if (drivePaths.length && CARS > 0) {
    const PAINT = [0x9fa3a8, 0x1c1f24, 0xb4b8bd, 0x2b3a52, 0x6e2b2b, 0xe4e6e8,
                   0x30463a, 0x5a5f66, 0x7d6a46, 0x24303d];
    const bucket = kinds.map(() => []);
    for (let i = 0; i < CARS; i++) {
      const r = rnd(i, 31);
      // A street is mostly cars. Buses are rare and read as transit when they
      // are rare; one in six and it is a depot.
      const k = r < 0.40 ? 0 : r < 0.68 ? 1 : r < 0.82 ? 4 : r < 0.95 ? 2 : 3;
      const p = drivePaths[Math.floor(rnd(i, 37) * drivePaths.length)];
      const dir = p.oneway ? 1 : (rnd(i, 41) < 0.5 ? 1 : -1);
      const laneW = 3.3;
      // Right-hand traffic: keep right of the centreline, in your own lane.
      const lane = Math.floor(rnd(i, 43) * Math.max(1, Math.floor(p.lanes / 2)));
      let turnN = i;
      bucket[k].push({
        p, s: rnd(i, 47) * p.len, dir, side: dir,
        o: dir * (laneW * 0.5 + lane * laneW),
        ot: dir * (laneW * 0.5 + lane * laneW),
        v: dir * (p.fast ? 13 + rnd(i, 53) * 6 : 6 + rnd(i, 59) * 5),
        col: PAINT[Math.floor(rnd(i, 61) * PAINT.length)],
        turn: () => rnd(++turnN, 103),
      });
    }
    const col = new THREE.Color();
    for (let k = 0; k < kinds.length; k++) {
      const list = bucket[k];
      if (!list.length) continue;
      const geo = VEHICLES[kinds[k]]();
      const mat = new THREE.MeshStandardMaterial({ roughness: 0.42, metalness: 0.42 });
      const mesh = new THREE.InstancedMesh(geo, mat, list.length);
      mesh.name = 'traffic_' + kinds[k];
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      mesh.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(list.length * 3), 3);
      for (let i = 0; i < list.length; i++) { col.setHex(list[i].col); mesh.setColorAt(i, col); }
      group.add(mesh);
      carMeshes.push({ mesh, list });
      cars.push(...list);
      stats.draws++;
      stats.tris += (geo.index.count / 3) * list.length;
    }
    stats.cars = cars.length;
    stats.carKinds = carMeshes.length;
  }

  // ── per-frame ────────────────────────────────────────────────────────────
  // THE ONLY PER-AGENT COST. One path lookup, one terrain sample, one matrix
  // compose, per agent per frame. No physics, no steering, no collision — they
  // are on rails, and at runner speed nobody can tell.
  let tSec = 0;
  function update(dt) {
    tSec += dt;
    if (pedMesh) {
      const t0 = performance.now();
      for (let i = 0; i < peds.length; i++) {
        const a = peds[i];
        advance(a, dt);
        at(a.p, a.s, a.o, cur);
        dummy.position.set(cur.x, heightAt(E, cur.x, cur.y), -cur.y);
        dummy.rotation.set(0, cur.h + (a.v < 0 ? Math.PI : 0), 0);
        dummy.scale.setScalar(a.hgt);
        dummy.updateMatrix();
        pedMesh.setMatrixAt(i, dummy.matrix);
      }
      pedMesh.instanceMatrix.needsUpdate = true;
      const sh = pedMesh.material.userData.sh;
      if (sh) sh.uniforms.uTime.value = tSec;
      stats.pedMs = performance.now() - t0;
    }
    const t1 = performance.now();
    for (const { mesh, list } of carMeshes) {
      for (let i = 0; i < list.length; i++) {
        const a = list[i];
        advance(a, dt);
        at(a.p, a.s, a.o, cur);
        dummy.position.set(cur.x, heightAt(E, cur.x, cur.y) + 0.22, -cur.y);
        dummy.rotation.set(0, cur.h + (a.v < 0 ? Math.PI : 0), 0);
        dummy.scale.setScalar(1);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
      }
      mesh.instanceMatrix.needsUpdate = true;
    }
    stats.carMs = performance.now() - t1;
  }
  update(0);

  return { group, stats, update };
}
