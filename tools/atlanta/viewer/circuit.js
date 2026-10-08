// A CIRCUIT — a closed lap of real streets, instead of a line through nowhere.
//
// Client: "how to figure out a circuit to wire this into the game so she's not
// just running all over the place through buildings and through nothing."
//
// ── WHY A LOOP IS THE RIGHT SHAPE, AND NOT JUST A NICER ONE ────────────────
// The point-to-point route search needed SEVEN weighted terms to behave —
// corner angle, corner spacing, grade, straight length, width, clearance,
// locality — and balancing them by hand against six locations was a losing
// game: tightening one sent another location somewhere stupid. Four separate
// rounds of that produced a route down a 2 m sidewalk, then a towpath at the
// edge of the extract, then a level 760 m long against a 432 m target.
//
// A circuit deletes most of those terms by construction:
//
//   it cannot wander off, because it comes back
//   it stays in the location, because a loop has a bounded extent
//   it never crosses a building, because STREETS DO NOT CROSS BUILDINGS —
//     the geometry is surveyed, so this is free rather than enforced
//   it laps, which is what an endless runner wants: reach the end and you are
//     already at the start, with no teleport and no seam
//
// What is left to score is only what a designer would actually argue about:
// are the corners good, is it the right length, is the surface wide enough.
//
// ── FEASIBILITY, MEASURED BEFORE ANY OF THIS WAS WRITTEN ───────────────────
// Independent loops in each extract (edges - nodes + components):
//   Apache 38 · MBS 21 · Track 4 · Stone Mtn 4 · DSA 2 · Wade 1
// and actual closed cycles of 260-760 m found by the search below:
//   Apache 168 · MBS 152 · Track 4 · DSA 0 · Wade 0 · Stone Mtn 0
//
// So this works where the street grid is dense and finds NOTHING in a park or
// on a campus — which is a radius problem, not a dead end. Measured: Wade at
// 400 m has 0 loops and at 900 m has 3; DSA at 300 m has 1 and at 800 m has 13.
// A location with no circuit has to be extracted wider, or fall back to the
// point-to-point route.
import * as THREE from './vendor/three.module.min.js';

const FOOT = new Set(['footway', 'path', 'steps', 'cycleway']);
const wrapPi = (a) => Math.atan2(Math.sin(a), Math.cos(a));
const pathLen = (p) => {
  let d = 0;
  for (let i = 1; i < p.length; i++) d += Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]);
  return d;
};

/**
 * Snap way endpoints into shared nodes and build an undirected graph.
 *
 * TOLERANCE IS 3 m. OSM genuinely shares junction coordinates — measured over
 * MBS, two thirds of way ends sit within half a metre of another — but not
 * always exactly, and a loop that fails to close because two ends are 1.4 m
 * apart is a loop you never find.
 */
function graphOf(ways, TOL = 3) {
  const nodes = [];
  const nid = (p) => {
    for (let i = 0; i < nodes.length; i++) {
      if (Math.hypot(nodes[i][0] - p[0], nodes[i][1] - p[1]) <= TOL) return i;
    }
    nodes.push(p);
    return nodes.length - 1;
  };
  const edges = [];
  for (const w of ways) {
    const a = nid(w.pts[0]), b = nid(w.pts[w.pts.length - 1]);
    if (a === b) continue;                       // a way that already loops on itself
    edges.push({ a, b, pts: w.pts, len: pathLen(w.pts), narrow: FOOT.has(w.kind), kind: w.kind });
  }
  const adj = {};
  edges.forEach((e, i) => {
    (adj[e.a] = adj[e.a] || []).push({ e: i, to: e.b, fwd: true });
    (adj[e.b] = adj[e.b] || []).push({ e: i, to: e.a, fwd: false });
  });
  return { nodes, edges, adj };
}

/** Stitch a cycle's edges into one closed polyline, oriented head to tail. */
function stitchCycle(cycle, edges) {
  const pts = [];
  for (const { i, fwd } of cycle) {
    const p = fwd ? edges[i].pts : edges[i].pts.slice().reverse();
    for (let j = 0; j < p.length; j++) {
      if (pts.length && j === 0) continue;       // drop the duplicated junction vertex
      pts.push(p[j]);
    }
  }
  return pts;
}

/**
 * Find the best closed circuit near the origin.
 *
 * DFS from the busiest junctions, bounded by length rather than depth, keeping
 * every simple cycle that comes back to its start within the length window.
 * The search is capped because a dense grid has a combinatorial number of
 * cycles and we only need a good one, not all of them.
 */
export function findCircuit(world, heightAt, E, opts = {}) {
  const target = opts.targetM ?? 432;
  const LO = opts.minM ?? target * 0.6;
  const HI = opts.maxM ?? target * 1.75;
  const CAP = opts.cap ?? 4000;

  const ways = (world.roads || []).filter((w) => w.pts.length >= 2 && pathLen(w.pts) >= 12);
  const { edges, adj } = graphOf(ways);

  // Start from the busiest junctions: a cycle has to pass through one, and a
  // degree-2 node only ever extends a path.
  const starts = Object.keys(adj).map(Number)
    .filter((n) => adj[n].length >= 3)
    .sort((a, b) => adj[b].length - adj[a].length)
    .slice(0, 40);

  const found = [];

  // ── A WAY THAT IS ALREADY A CIRCLE IS THE BEST CIRCUIT THERE IS ─────────
  // `graphOf` drops these: a closed way has a === b, and a self-loop breaks a
  // junction walk. But a park loop trail, a cul-de-sac ring or a stadium
  // concourse is mapped in OSM as ONE closed way — exactly the lap we are
  // hunting for, thrown away before the search began.
  // Measured once the filter was questioned: Wade holds a 550 m closed
  // residential ring and MBS three pedestrian loops of 278, 585 and 637 m,
  // and the graph search had reported ZERO cycles at both even with the length
  // window opened to 2.6 km. Wade had been falling back to an open route the
  // whole time with a perfect circuit sitting in its own extract.
  for (const w of ways) {
    if (w.pts.length <= 3) continue;
    const a = w.pts[0], z = w.pts[w.pts.length - 1];
    if (Math.hypot(a[0] - z[0], a[1] - z[1]) > 3) continue;
    const L = pathLen(w.pts);
    if (L < LO || L > HI) continue;
    found.push({ len: L, selfClosed: w, edges: [] });
  }

  for (const s of starts) {
    const stack = [{ node: s, used: new Set(), path: [], len: 0 }];
    while (stack.length && found.length < CAP) {
      const st = stack.pop();
      if (st.path.length > 9) continue;          // a lap of ten streets is not a lap
      for (const nb of adj[st.node]) {
        if (st.used.has(nb.e)) continue;
        const nl = st.len + edges[nb.e].len;
        if (nl > HI) continue;
        if (nb.to === s && st.path.length >= 2 && nl >= LO) {
          found.push({ len: nl, edges: [...st.path, { i: nb.e, fwd: nb.fwd }] });
          continue;
        }
        const used = new Set(st.used); used.add(nb.e);
        stack.push({ node: nb.to, used, path: [...st.path, { i: nb.e, fwd: nb.fwd }], len: nl });
      }
    }
  }
  if (!found.length) return null;

  // ── score what is actually left to argue about ──────────────────────────
  const scored = found.map((c) => {
    const pts = c.selfClosed ? c.selfClosed.pts.slice() : stitchCycle(c.edges, edges);
    let corners = 0, good = 0, far = 0;
    for (let j = 1; j < pts.length - 1; j++) {
      const h0 = Math.atan2(pts[j][1] - pts[j - 1][1], pts[j][0] - pts[j - 1][0]);
      const h1 = Math.atan2(pts[j + 1][1] - pts[j][1], pts[j + 1][0] - pts[j][0]);
      const d = Math.abs(wrapPi(h1 - h0)) * 180 / Math.PI;
      if (d >= 20) { corners++; if (d >= 60 && d <= 120) good++; }
    }
    for (const p of pts) far = Math.max(far, Math.hypot(p[0], p[1]));
    const narrow = c.selfClosed ? (FOOT.has(c.selfClosed.kind) ? 1 : 0)
                                : c.edges.filter((x) => edges[x.i].narrow).length / c.edges.length;
    const s = good * 40
            - (corners - good) * 25               // a kink that is not a corner
            - Math.abs(c.len - target) * 0.15
            - narrow * 80                         // the corridor is 4.8 m wide
            - Math.max(0, far - 300) * 0.30;      // stay at the place it is named after
    return { ...c, pts, corners, good, far: Math.round(far), narrow: +narrow.toFixed(2), score: s };
  }).sort((a, b) => b.score - a.score);

  const best = scored[0];

  // A LOOP HAS NO END, so `cum` runs once round and the runner wraps on it.
  const cum = [0];
  for (let i = 1; i < best.pts.length; i++) {
    cum.push(cum[i - 1] + Math.hypot(best.pts[i][0] - best.pts[i - 1][0],
                                     best.pts[i][1] - best.pts[i - 1][1]));
  }
  return {
    pts: best.pts, cum, len: cum[cum.length - 1], closed: true,
    stats: {
      lengthM: Math.round(best.len), edges: best.edges.length || 1,
      selfClosed: !!best.selfClosed,
      corners: best.corners, nearRight: best.good,
      maxFromCentreM: best.far, narrowFraction: best.narrow,
      candidates: found.length,
    },
  };
}

/** Draw the circuit as a closed ribbon marker, for the overview. */
export function circuitGizmo(circuit, heightAt, E) {
  const v = [];
  for (const [x, y] of circuit.pts) v.push(x, heightAt(E, x, y) + 0.6, -y);
  // close it visually too — a lap that looks open is a lap you mistrust
  v.push(v[0], v[1], v[2]);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(v, 3));
  const line = new THREE.Line(g, new THREE.LineBasicMaterial({ color: 0xffd34d }));
  line.name = 'circuit';
  return line;
}
