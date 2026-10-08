// A LOCATION BECOMES A LEVEL — the run route, its corners, its lanes, its climb.
//
// Client, 10-06: "this is gonna be a game so everything should be level
// basically prep this for the runner game." So each Atlanta location stops
// being a place to orbit and becomes a thing you run through, start to finish.
//
// ── WHAT TRANSFERS FROM THE SHIPPED RUNNER IS TIMING, NOT UNITS ────────────
// Royal Runner works in a stylised z-space: `mv = eff*2.4` z per frame with
// `eff = min(11.5, 5.2 + dist*0.0045)`, obstacles spawned at z=1500, and
// `GS.dist += eff/T` with T=32, so a dist-unit is 76.8 z. None of that is
// metres and none of it should be forced onto real geometry. What IS portable
// is the cadence it produces, read straight off the shipped constants:
//
//   far plane .............. 1500 z / (5.2*2.4 z/frame) = 120 frames = 2.00 s
//   obstacle spacing ....... nextZ 330..570+ z          = 0.44..0.77 s
//   jump airtime ........... 2*13.5/0.62                = 43.5 frames = 0.73 s
//   first corner ........... GS.dist > 130              = ~13 s
//   corner spacing ......... sinceTurn > 240            = ~25 s at base speed
//
// Those are the numbers this file plans against. The one place the stylised
// space does NOT survive contact with a real city is the far plane: 2.0 s of
// travel at a human 4.8 m/s is **9.6 m of visible road**, which is fine for an
// abstract corridor and absurd for Atlanta. Flagged in `stats.sightM`, because
// it is a design decision for the client, not something to quietly paper over.
import * as THREE from './vendor/three.module.min.js';
import { manGeometries } from './men.js';
import { findCircuit } from './circuit.js';

// Timing, in seconds, lifted from the shipped runner (see above).
export const BEAT = {
  sight: 2.00,          // s of travel the far plane covers
  obMin: 0.44,          // s between obstacles, fastest
  obMax: 0.77,          // s between obstacles, slowest
  jumpAir: 0.73,        // s she is off the ground
  firstTurn: 13.0,      // s before the first corner
  turnGap: 25.0,        // s between corners at base speed
  turnSwing: 0.50,      // s the corner swing lasts (TURN_LEN 30 frames)
};

// She runs. 4.8 m/s is 17 km/h — a real run, and it is what the shipped jump
// arc implies: 0.73 s of airtime covering the ~3.5 m a running jump covers.
export const RUN_MS = 4.8;

const LANES = 3;              // t3.lane is -1, 0, 1 — do not change without the game
const LANE_M = 1.6;           // metres between lane centres; 3 lanes = 4.8 m corridor

const FOOT_KINDS = new Set(['footway', 'path', 'pedestrian', 'steps', 'cycleway']);
// Too narrow to hold a 4.8 m three-lane corridor. `pedestrian` is excluded on
// purpose — those are plazas and promenades, which are wide.
const NARROW = new Set(['footway', 'path', 'steps', 'cycleway']);

function pathLen(pts) {
  let d = 0;
  for (let i = 1; i < pts.length; i++) d += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
  return d;
}

/** Heading of a way at one of its ends, pointing INTO the way. */
function headingAt(pts, fromStart) {
  const a = fromStart ? pts[0] : pts[pts.length - 1];
  const b = fromStart ? pts[1] : pts[pts.length - 2];
  return Math.atan2(b[1] - a[1], b[0] - a[0]);
}

const wrapPi = (a) => Math.atan2(Math.sin(a), Math.cos(a));

/** Junction table: for each way end, every way that continues from it. */
function adjacency(ways, TOL = 2) {
  const ends = [];
  ways.forEach((w, i) => {
    ends.push({ i, fromStart: true, p: w.pts[0] });
    ends.push({ i, fromStart: false, p: w.pts[w.pts.length - 1] });
  });
  const adj = ways.map(() => [[], []]);          // [out of start, out of end]
  for (const a of ends) {
    for (const b of ends) {
      if (a.i === b.i) continue;
      if (Math.hypot(a.p[0] - b.p[0], a.p[1] - b.p[1]) > TOL) continue;
      // leaving way a at the end OPPOSITE the one we entered by
      adj[a.i][a.fromStart ? 0 : 1].push({ i: b.i, fromStart: b.fromStart });
    }
  }
  return adj;
}

/**
 * Steepest SUSTAINED grade along a leg, as a fraction.
 *
 * THE WINDOW IS THE DEM'S OWN STEP, NEVER FINER. This sampled every 10 m, and
 * the elevation grid is 15.4-23.1 m depending on the location — so it was
 * asking the data for detail between 1.5x and 2.3x finer than the data has,
 * and reading back its own bilinear interpolation as terrain. That is where the
 * "264% grade" at Stone Mountain came from: an artifact, not a cliff. It also
 * rejected whole streets, because one invented 10 m spike condemns a 1.3 km way
 * — which is why three of the four locations came back with NO level at all.
 *
 * It is also the right window physically: a runner feels a sustained slope, not
 * a bump. `window` is max(DEM step, 25 m).
 */
function legGrade(pts, heightAt, E) {
  const win = Math.max(E.step || 20, 25);
  let worst = 0, run = 0, z0 = heightAt(E, pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) {
    run += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    if (run >= win) {
      const z = heightAt(E, pts[i][0], pts[i][1]);
      const g = (z - z0) / run;
      if (Math.abs(g) > Math.abs(worst)) worst = g;
      z0 = z; run = 0;
    }
  }
  return worst;
}

/**
 * The shape of a way, as the runner would experience it.
 *
 * THE OPTIMIZER HAS TO SEE BENDS INSIDE A WAY, not just turns at junctions.
 * Scoring only the junctions let the Stone Mountain search pick a single way
 * that was a **switchback trail: 115 corners, straights as short as 1 m**, and
 * score it as a perfect zero-corner leg. A hiking path up a mountain is exactly
 * what OSM says it is; the search just could not read it.
 */
function legShape(pts) {
  let bends = 0, lastBendAt = 0, minStraight = Infinity, run = 0;
  for (let i = 1; i < pts.length - 1; i++) {
    run += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    const h0 = Math.atan2(pts[i][1] - pts[i - 1][1], pts[i][0] - pts[i - 1][0]);
    const h1 = Math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0]);
    if (Math.abs(wrapPi(h1 - h0)) < 0.35) continue;        // under 20 deg is road curve
    bends++;
    if (run - lastBendAt < minStraight) minStraight = run - lastBendAt;
    lastBendAt = run;
  }
  return { bends, minStraight: minStraight === Infinity ? 1e9 : minStraight };
}

/**
 * SEARCH FOR A ROUTE THAT PLAYS, rather than walking one and hoping.
 *
 * The first version took the straightest continuation at every junction, and
 * the measurement killed it: **zero corners over 756 m at MBS**, because
 * straightest-first is by construction a machine for never turning. Three of
 * the four locations then fell back to a single long way — one leg, no corners,
 * 157-359 seconds of running. A runner level with no corners is a corridor.
 *
 * So the route is chosen by SCORE, over a beam of candidates, against what the
 * shipped game actually wants:
 *
 *   - a corner near a right angle is worth a lot; the shipped turn is a BINARY
 *     left/right swipe, so 90 deg reads as "that was a corner" and 40 deg reads
 *     as an arbitrary demand for the same input
 *   - corners spaced like the spawn table: the shipped gap is ~25 s at base
 *     speed, so they want to be ~100-250 m apart, never 20 m apart
 *   - grade she can actually run. Measured before this existed: the Stone
 *     Mountain route climbed a **264% grade**. That is a cliff face, and the
 *     DEM is right — the mountain has 240 m of relief in a 450 m radius. A
 *     route there has to contour, and only a search will find one that does.
 *   - length that hits the target, because a level is a fixed thing
 */
/** Stitch legs into one polyline and cut it at `targetM`. */
function stitch(legs, targetM, fromM = 0) {
  const pts = [];
  for (const leg of legs) {
    for (let i = 0; i < leg.pts.length; i++) {
      if (pts.length && i === 0) continue;
      pts.push(leg.pts[i]);
    }
  }
  const cum = [0];
  for (let i = 1; i < pts.length; i++) {
    cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  }
  // cut the front
  if (fromM > 0 && fromM < cum[cum.length - 1]) {
    let k = 0; while (k < cum.length - 2 && cum[k + 1] <= fromM) k++;
    const f = (fromM - cum[k]) / ((cum[k + 1] - cum[k]) || 1);
    const a = pts[k], b = pts[k + 1];
    const head = [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f];
    pts.splice(0, k + 1, head);
    cum.length = 0; cum.push(0);
    for (let i = 1; i < pts.length; i++) {
      cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    }
  }
  // cut the tail
  if (targetM && cum[cum.length - 1] > targetM) {
    let k = 1; while (k < cum.length - 1 && cum[k + 1] < targetM) k++;
    const f = (targetM - cum[k]) / ((cum[k + 1] - cum[k]) || 1);
    const a = pts[k], b = pts[k + 1];
    pts.length = k + 1;
    pts.push([a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f]);
    cum.length = k + 1;
    cum.push(targetM);
  }
  return { pts, cum, len: cum[cum.length - 1] };
}

/**
 * SCORE THE ROUTE THE PLAYER WILL ACTUALLY RUN.
 *
 * The beam heuristic scores junction turns, which is cheap and good enough to
 * prune with — but it is NOT what the player meets. A junction turn of 85 deg
 * followed ten metres later by another 85 in the same direction is a hairpin,
 * and the junction scorer sees two decent corners. Measured on the first
 * working build: reported corners of **171, 168 and 160 degrees** on routes the
 * search had scored as clean. So final selection re-stitches each finished
 * candidate and scores the corners the trimmed polyline actually contains.
 */
function routeScore(legs, targetM, fromM = 0) {
  const { pts, cum, len } = stitch(legs.slice(), targetM, fromM);
  const turns = findCorners(pts, cum);
  let sc = 0;
  let prev = 0;
  for (const t of turns) {
    // 60-120 is a corner you read as a corner. Outside it is either a kink that
    // did not need a swipe or a U-turn that reads as a dead end.
    // A HAIRPIN IS A FAILURE, NOT A DEDUCTION. At -45 a 174 deg corner was
    // simply outscored by the length and spacing bonuses around it, so MBS kept
    // shipping one. Over 140 deg the player runs back the way they came, which
    // no single left/right swipe expresses; price it so no amount of other
    // merit buys it.
    if (t.deg > 140) sc -= 400;
    else sc += (t.deg >= 60 && t.deg <= 120) ? 40 : -45;
    const gap = t.s - prev;
    if (gap < 70) sc -= 45;
    else if (gap > 260) sc -= 12;
    prev = t.s;
  }
  // ── THE LEVEL MUST PASS THROUGH ITS LOCATION. A HARD RULE, NOT A WEIGHT. ──
  // This started as a soft penalty on mean distance from the centre and became
  // a tuning fight: at 0.55 it overpowered the corner and length terms (MBS
  // lost both corners, Stone Mountain overshot to 760 m); softened to 0.18 it
  // stopped working and Apache drifted back out to a towpath at the edge of the
  // extract with the city a smudge on the horizon. Seven weighted terms is too
  // many to balance by hand against six locations.
  //
  // So this one is a gate. A level named after a place has to GO THERE: some
  // part of the route must come within 250 m of the location centre. Everything
  // else stays a score; this is a rule.
  let nearest = Infinity;
  for (let i = 0; i < pts.length; i++) {
    const d = Math.hypot(pts[i][0], pts[i][1]);
    if (d < nearest) nearest = d;
  }
  if (nearest > 250) sc -= 500 + (nearest - 250) * 2;

  if (!turns.length) sc -= 60;             // a corridor is not a level
  if (turns.length > 6) sc -= (turns.length - 6) * 20;
  // LENGTH SHORTFALL IS A FAILURE, NOT A DEDUCTION. At a flat 0.08/m a route
  // 179 m short of target lost only 14 points — less than a single corner bonus
  // — so hardening the hairpin rule immediately produced a clean 253 m level
  // where a 432 m one was wanted. Over-length is free (the route is trimmed);
  // under-length is not, because nothing can recover the missing seconds.
  const over = len - targetM;
  sc -= over > 0 ? over * 0.02
                 : Math.abs(over) * 0.10 + Math.max(0, targetM * 0.85 - len) * 0.9;
  return { sc, turns, len };
}

/**
 * How much of a leg runs jammed against a building.
 *
 * THE CORRIDOR IS 4.8 m WIDE (3 lanes at 1.6). A 2 m sidewalk hugging a tower
 * cannot hold it, and the route search had no idea: it scored corners, grade
 * and straight length and nothing about ROOM. Apache picked exactly such a
 * footway, and the play capture came out as a camera grinding along a wall with
 * the hero not even visible. Measured per leg as the fraction of sample points
 * within `NEED` metres of a building footprint.
 *
 * Bounding boxes again, for the same reason as the terrain's contact shading:
 * at a few hundred samples against a hundred buildings it is thousands of tests
 * either way, and a soft penalty does not need polygon precision.
 */
function legClearance(pts, boxes, NEED = 5) {
  if (!boxes || !boxes.length) return 1;
  let near = 0, n = 0;
  for (let i = 1; i < pts.length; i++) {
    const steps = Math.max(1, Math.min(8, Math.round(
      Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]) / 12)));
    for (let k = 0; k < steps; k++) {
      const f = k / steps;
      const x = pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f;
      const y = pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f;
      n++;
      for (let b = 0; b < boxes.length; b++) {
        const bb = boxes[b];
        if (x > bb[0] - NEED && x < bb[2] + NEED && y > bb[1] - NEED && y < bb[3] + NEED) { near++; break; }
      }
    }
  }
  return n ? 1 - near / n : 1;
}

/** A leg the player will feel as twitchy: many bends, or bends packed close. */
function legPenalty(L) {
  let p = 0;
  // ── ROOM, AND STILL IN THE CITY ─────────────────────────────────────────
  // The corridor is 4.8 m (3 lanes x 1.6), so the question is whether the way
  // can HOLD it — which its class already answers. A first attempt scored
  // geometric distance from buildings instead, and that was the wrong
  // quantity: "avoid buildings" became "avoid the city", and Apache's route
  // walked out to empty ground at the edge of the extract where there was
  // nothing to see at all. A city runner should run AMONG buildings, just not
  // pressed against one.
  if (L.narrow) p -= 120;               // footway/path: cannot hold the corridor
  // Only the genuinely jammed case is still refused — a way with buildings on
  // top of it for nearly its whole length.
  if (L.clear !== undefined && L.clear < 0.25) p -= 180;
  // ...and wandering out of the location is its own failure: the level is
  // supposed to be AT the place it is named after.
  if (L.farM !== undefined) p -= Math.max(0, L.farM - 220) * 0.35;
  // 1 bend per 120 m is a street; 1 per 20 m is a switchback.
  const density = L.bends / Math.max(1, L.len / 100);
  return p + -(Math.max(0, density - 1) * 18) - (L.minStraight < 80 ? 20 : 0);
}

function searchRoute(ways, adj, heightAt, E, opt) {
  const { targetM, maxGrade, beam, cornerMin, cornerMax } = opt;
  const searchM = opt.searchM || targetM;
  const legCache = new Map();
  const legOf = (i, fromStart) => {
    const k = i * 2 + (fromStart ? 0 : 1);
    let v = legCache.get(k);
    if (!v) {
      const pts = fromStart ? ways[i].pts : ways[i].pts.slice().reverse();
      const _mid = pts[Math.floor(pts.length / 2)];
      v = { pts, len: pathLen(pts), grade: legGrade(pts, heightAt, E),
            clear: legClearance(pts, opt.boxes),
            narrow: NARROW.has(ways[i].kind),
            farM: Math.hypot(_mid[0], _mid[1]),
            ...legShape(pts),
            inH: headingAt(ways[i].pts, fromStart),
            outH: Math.atan2(pts[pts.length - 1][1] - pts[pts.length - 2][1],
                             pts[pts.length - 1][0] - pts[pts.length - 2][0]) };
      legCache.set(k, v);
    }
    return v;
  };

  let states = [];
  for (let i = 0; i < ways.length; i++) {
    for (const fromStart of [true, false]) {
      const L = legOf(i, fromStart);
      if (Math.abs(L.grade) > maxGrade) continue;
      if (L.minStraight < opt.minStraight) continue;   // a switchback is not a level
      states.push({ legs: [{ i, fromStart }], used: new Set([i]),
                    total: L.len, score: legPenalty(L), corners: [],
                    last: { i, fromStart } });
    }
  }
  if (!states.length) return null;

  const done = [];
  for (let depth = 0; depth < 24 && states.length; depth++) {
    const next = [];
    for (const st of states) {
      if (st.total >= searchM) { done.push(st); continue; }
      const L = legOf(st.last.i, st.last.fromStart);
      const outs = adj[st.last.i][st.last.fromStart ? 0 : 1];
      let extended = false;
      for (const o of outs) {
        if (st.used.has(o.i)) continue;
        const N = legOf(o.i, o.fromStart);
        if (Math.abs(N.grade) > maxGrade) continue;
        if (N.minStraight < opt.minStraight) continue;
        const turn = wrapPi(N.inH - L.outH);
        const deg = Math.abs(turn) * 180 / Math.PI;
        if (deg > 140) continue;                       // a U-turn is not a corner
        let add = 0;
        const isCorner = deg >= 20;
        if (isCorner) {
          add += (deg >= cornerMin && deg <= cornerMax) ? 30 : -35;
          const prev = st.corners.length ? st.corners[st.corners.length - 1] : -Infinity;
          const gap = st.total - prev;
          // too close together is unfair, too far apart is a corridor
          if (gap < 70) add -= 40;
          else if (gap > 260) add -= 10;
        }
        // reward progress, punish wandering out of the location
        add += N.len * 0.02 + legPenalty(N);
        const corners = isCorner ? st.corners.concat(st.total) : st.corners;
        const used = new Set(st.used); used.add(o.i);
        next.push({ legs: st.legs.concat(o), used, total: st.total + N.len,
                    score: st.score + add, corners, last: o });
        extended = true;
      }
      if (!extended && st.total > targetM * 0.5) done.push(st);
    }
    next.sort((a, b) => (b.score + b.total * 0.02) - (a.score + a.total * 0.02));
    states = next.slice(0, beam);
  }
  done.push(...states);
  if (!done.length) return null;
  // Re-score every finished candidate on the polyline it actually produces,
  // then take the best. The in-flight score only ever existed to prune.
  // SLIDE THE LEVEL ALONG THE ROUTE. A 432 m level cut from the front of a
  // route takes whatever happens to be there — and at Stone Mountain the
  // biggest connected component is three ways totalling 2,973 m, so the window
  // always landed INSIDE a single 1 km trail and met no junction at all. The
  // start of a level is a design choice, not a consequence of which way OSM
  // listed first: try every 25 m offset and keep the best stretch.
  for (const st of done) {
    const segs = st.legs.map((l) => ({ pts: legOf(l.i, l.fromStart).pts }));
    let bestSc = -Infinity, bestFrom = 0;
    const slack = Math.max(0, st.total - targetM);
    for (let from = 0; from <= slack; from += 25) {
      const sc = routeScore(segs, targetM, from).sc;
      if (sc > bestSc) { bestSc = sc; bestFrom = from; }
    }
    st.final = bestSc; st.fromM = bestFrom;
  }
  done.sort((a, b) => b.final - a.final);
  const best = done[0];
  return { legs: best.legs.map((l) => ({ idx: l.i, pts: legOf(l.i, l.fromStart).pts,
                                         kind: ways[l.i].kind, name: ways[l.i].name })),
           total: best.total, searched: done.length, finalScore: Math.round(best.final),
           fromM: best.fromM || 0 };
}

/**
 * Corners, as the runner understands them: a single left or right.
 *
 * TWO THRESHOLDS, AND BOTH MATTER. Below `gentle` a bend is just the road
 * curving and the camera's own lean covers it — making the player swipe for a
 * 20 deg kink would feel arbitrary. Above it the shipped turn is a BINARY
 * left/right swipe (`{tp:'turn', dir:+-1}`), so the route wants corners near a
 * right angle; a 45 deg junction is the awkward case, because it demands the
 * same input as a 90 and does not look like it needs one. `stats.awkward`
 * counts them so a level can be judged before it is built.
 */
function findCorners(pts, cum, gentle = 0.52 /* 30 deg */) {
  const turns = [];
  for (let i = 1; i < pts.length - 1; i++) {
    const h0 = Math.atan2(pts[i][1] - pts[i - 1][1], pts[i][0] - pts[i - 1][0]);
    const h1 = Math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0]);
    const d = wrapPi(h1 - h0);
    if (Math.abs(d) < gentle) continue;
    const prev = turns[turns.length - 1];
    // Vertices only a few metres apart are one corner drawn with two nodes —
    // merge them, or a single street corner emits three swipe prompts.
    if (prev && cum[i] - prev.s < 12 && Math.sign(d) === Math.sign(prev.rad)) {
      prev.rad += d; prev.s = (prev.s + cum[i]) / 2;
      prev.deg = Math.round(Math.abs(prev.rad) * 180 / Math.PI);
      continue;
    }
    turns.push({ s: cum[i], rad: d, dir: d > 0 ? -1 : 1,   // +rad is left in x/y; runner dir -1 = left
                 deg: Math.round(Math.abs(d) * 180 / Math.PI) });
  }
  return turns;
}

/**
 * Build the runnable level for a location.
 * Returns route geometry in metres, corners, the climb profile and a beat map.
 */
export function buildLevel(world, heightAt, E, opts = {}) {
  const speed = opts.speed ?? RUN_MS;
  // A LEVEL IS A DURATION, NOT A DISTANCE. Targeting metres gave 157-359
  // seconds of running per location — three to six minutes down one street.
  // 90 s is a promo-game level; at 4.8 m/s that is 432 m, and it is the target
  // because it is what the player experiences, not what the map measures.
  const targetS = opts.targetS ?? 90;
  const targetM = opts.targetM ?? Math.round(speed * targetS);
  // 12% is a hard hill to run up and about the limit of what reads as running
  // rather than scrambling. The unconstrained search picked 264% at Stone
  // Mountain, which is a cliff.
  const maxGrade = (opts.maxGradePct ?? 12) / 100;

  // Candidate ways: streets AND footways. She runs through the place, not down
  // one carriageway, and restricting to roads strands the park and the campus.
  const ways = world.roads.filter((w) => w.pts.length >= 2 && pathLen(w.pts) >= 15);

  // ── A SIGNATURE ROUTE BEATS ANY SEARCH ──────────────────────────────────
  // Some locations ARE one named route, and no scorer should be allowed to
  // argue. Stone Mountain is the Walk-Up Trail: 1,994 m climbing 197 m, which
  // people walk every day. A circuit search there returns a flat ring at -2%
  // grade — technically a lap, and not Stone Mountain. `signature` in
  // locations.json names the way, and the level is the best window of it.
  if (opts.signature && world.roads) {
    const sig = world.roads.filter((w) => w.name === opts.signature && w.pts.length >= 2);
    if (sig.length) {
      // stitch the named ways end to end, nearest-neighbour, since OSM splits a
      // long trail into pieces that are not in route order
      const rem = sig.slice();
      let chain = rem.shift().pts.slice();
      while (rem.length) {
        const tail = chain[chain.length - 1];
        let bi = -1, brev = false, bd = Infinity;
        rem.forEach((w, i) => {
          const d0 = Math.hypot(w.pts[0][0] - tail[0], w.pts[0][1] - tail[1]);
          const d1 = Math.hypot(w.pts[w.pts.length - 1][0] - tail[0], w.pts[w.pts.length - 1][1] - tail[1]);
          if (d0 < bd) { bd = d0; bi = i; brev = false; }
          if (d1 < bd) { bd = d1; bi = i; brev = true; }
        });
        if (bi < 0 || bd > 60) break;             // the next piece is not actually attached
        const nx = rem.splice(bi, 1)[0].pts;
        const seg = brev ? nx.slice().reverse() : nx;
        for (let i = 1; i < seg.length; i++) chain.push(seg[i]);
      }
      const scum = [0];
      for (let i = 1; i < chain.length; i++) {
        scum.push(scum[i - 1] + Math.hypot(chain[i][0] - chain[i - 1][0], chain[i][1] - chain[i - 1][1]));
      }
      if (scum[scum.length - 1] >= targetM) {
        // take the window that CLIMBS the most — on a mountain that is the point
        let bestFrom = 0, bestGain = -Infinity;
        for (let from = 0; from + targetM <= scum[scum.length - 1]; from += 40) {
          let i0 = 0; while (i0 < scum.length - 1 && scum[i0] < from) i0++;
          let i1 = i0; while (i1 < scum.length - 1 && scum[i1] < from + targetM) i1++;
          const g = heightAt(E, chain[i1][0], chain[i1][1]) - heightAt(E, chain[i0][0], chain[i0][1]);
          if (g > bestGain) { bestGain = g; bestFrom = from; }
        }
        const { pts, cum, len } = stitch([{ pts: chain }], targetM, bestFrom);
        const turns = findCorners(pts, cum);
        return finishLevel(world, heightAt, E, pts, cum, len, turns, speed, targetM,
                           { kind: 'signature', closed: false, name: opts.signature,
                             climbM: Math.round(bestGain), fullRouteM: Math.round(scum[scum.length - 1]) });
      }
    }
  }

  // ── A CIRCUIT FIRST, IF THE STREETS CONTAIN ONE ─────────────────────────
  // A closed lap is strictly better than a point-to-point line here: it cannot
  // wander off, it stays in the location, it never crosses a building because
  // streets do not, and it LAPS — so an endless runner reaches the end already
  // at the start, with no seam. The seven-term point-to-point scorer below
  // exists to approximate those properties; a loop just has them.
  // Falls through to that scorer where the extract holds no cycle at all,
  // which measured as DSA, Wade and Stone Mountain — a radius problem, since
  // Wade goes 0 loops at 400 m to 3 at 900 m.
  if (opts.circuit !== false) {
    const circ = findCircuit(world, heightAt, E, { targetM });
    if (circ) {
      const turns = findCorners(circ.pts, circ.cum);
      return finishLevel(world, heightAt, E, circ.pts, circ.cum, circ.len, turns, speed,
                         targetM, { ...circ.stats, kind: 'circuit', closed: true });
    }
  }

  const adj = adjacency(ways);
  // building bounds, for the clearance test
  const boxes = (world.buildings || []).map((b) => {
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    for (const [px, py] of b.pts) {
      if (px < x0) x0 = px; if (px > x1) x1 = px;
      if (py < y0) y0 = py; if (py > y1) y1 = py;
    }
    return [x0, y0, x1, y1];
  });
  // RELAX RATHER THAN RETURN NOTHING. Stone Mountain has only 7 of its 20 ways
  // under 12% — it is a mountain — so a hard cap there means no level at all,
  // which is the worst possible answer. Walk the cap out and report the one
  // actually used, so the constraint stays visible instead of silently ignored.
  // Both constraints walk out together: Stone Mountain is a mountain with
  // switchback trails, so demanding a 12% grade AND 40 m straights there leaves
  // nothing at all, and "no level" is the worst possible answer.
  // EVERY RUNG IS TRIED AND THE BEST ROUTE WINS — the ladder used to stop at
  // the first rung that reached 90% of target length, which is why Stone
  // Mountain shipped a 432 m corridor with ZERO corners: the strictest rung
  // found a long straight way, declared success, and never looked at the rungs
  // where the mountain's actual junctions live. Length is one term in the
  // score, not a gate on the search.
  let found = null, usedCap = maxGrade, usedStraight = 25, bestSc = -Infinity;
  // The straight-length rungs are gentle because the filter is BLUNT: it
  // rejects a whole street for one tight bend. Measured at Stone Mountain, 40 m
  // left 5 of 20 ways standing and none of the 14 junction transitions in the
  // 60-120 deg band were reachable — so the level came back a cornerless
  // corridor. `legPenalty` already prices bend density properly; the hard
  // filter only has to stop genuine switchbacks.
  const LADDER = [[maxGrade, 25], [maxGrade * 1.5, 20], [maxGrade * 2.5, 15],
                  [maxGrade * 4, 12], [99, 8]];
  for (const [cap, ms] of LADDER) {
    const r = searchRoute(ways, adj, heightAt, E, {
      targetM, searchM: targetM * 2, maxGrade: cap, minStraight: ms, boxes,
      beam: opts.beam ?? 96, cornerMin: 60, cornerMax: 120,
    });
    if (!r) continue;
    // A steeper rung has to EARN its win, or every location ends up climbing.
    const penalty = (cap > maxGrade ? 25 : 0) + (ms < 20 ? 15 : 0);
    const sc = r.finalScore - penalty;
    if (sc > bestSc) { bestSc = sc; found = r; usedCap = cap; usedStraight = ms; }
  }
  if (!found) return null;
  const { legs, total, searched } = found;

  // TRIM TO THE TARGET. A level is a fixed thing and ends where the designer
  // says, not where OSM happens to stop drawing a street. Without this a single
  // 1.3 km way became a 273-SECOND level, because any way longer than the
  // target satisfied the search at depth zero and was never cut back.
  // targetM, NOT targetM + fromM: `stitch` cuts the front FIRST and rebuilds the
  // cumulative table from zero, so the tail cut is already measured from the new
  // start. Adding the offset on top left every slid level exactly `fromM` too
  // long — MBS 475 m and Stone Mountain 760 m against a 432 m target, which is
  // 158 seconds of running in a level specced at 90.
  const { pts, cum, len } = stitch(legs, targetM, found.fromM || 0);

  const turns = findCorners(pts, cum);

  return finishLevel(world, heightAt, E, pts, cum, len, turns, speed, targetM,
                     { kind: 'route', closed: false, legs: legs.length,
                       routesSearched: searched, score: found.finalScore,
                       gradeCapUsedPct: usedCap >= 99 ? 'none' : +(usedCap * 100).toFixed(0),
                       minStraightUsedM: usedStraight }, legs);
}

/**
 * PERFORMANCE: keep only what the player can see from the route.
 *
 * A location is built at a 350-450 m radius because that is what the extract
 * covers, but a level is a 432 m ribbon through it and the runner camera never
 * leaves that ribbon. Everything beyond the sight line behind a building is
 * geometry nobody will ever see, paid for on every frame of a phone's budget.
 *
 * Returns a test for "is this near the route", used to filter buildings, props
 * and agents at build time. The band is generous on purpose — the city has to
 * read as a city on the skyline, so this culls the far field, not the view.
 */
export function corridorFilter(level, bandM = 160) {
  // Bucket the route into a coarse grid so the test is O(1) rather than O(route).
  const CELL = bandM;
  const grid = new Map();
  const key = (cx, cy) => cx * 100000 + cy;
  for (let i = 0; i < level.pts.length; i++) {
    const [x, y] = level.pts[i];
    const cx = Math.round(x / CELL), cy = Math.round(y / CELL);
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) {
      grid.set(key(cx + dx, cy + dy), true);
    }
  }
  const near = (x, y) => grid.has(key(Math.round(x / CELL), Math.round(y / CELL)));
  near.bandM = bandM;
  return near;
}

/** Draw the level: corridor, lane lines, corner markers, obstacle slots. */
export function levelGizmo(level, heightAt, E) {
  const g = new THREE.Group();
  g.name = 'level';
  const lift = 0.5;
  const at = (s) => {
    const { pts, cum } = level;
    let lo = 0; while (lo < cum.length - 2 && cum[lo + 1] < s) lo++;
    const f = (s - cum[lo]) / ((cum[lo + 1] - cum[lo]) || 1);
    const a = pts[lo], b = pts[lo + 1] || pts[lo];
    const x = a[0] + (b[0] - a[0]) * f, y = a[1] + (b[1] - a[1]) * f;
    const L = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
    return { x, y, nx: (b[1] - a[1]) / L, ny: -(b[0] - a[0]) / L };
  };

  // lane lines
  for (let l = -1; l <= 1; l++) {
    const v = [];
    for (let s = 0; s <= level.len; s += 2) {
      const p = at(s);
      const x = p.x + p.nx * l * level.laneM, y = p.y + p.ny * l * level.laneM;
      v.push(x, heightAt(E, x, y) + lift, -y);
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(v, 3));
    const line = new THREE.Line(geo, new THREE.LineBasicMaterial({
      color: l === 0 ? 0xffd34d : 0x59b0ff, transparent: true, opacity: l === 0 ? 0.95 : 0.55 }));
    line.name = 'lane_' + l;
    g.add(line);
  }

  // corner markers — a post pair at each turn, coloured by direction
  const postL = new THREE.CylinderGeometry(0.25, 0.25, 5, 6);
  const matL = new THREE.MeshBasicMaterial({ color: 0xff5e7a });
  const matR = new THREE.MeshBasicMaterial({ color: 0x4de08a });
  for (const t of level.turns) {
    const p = at(t.s);
    const m = new THREE.Mesh(postL, t.dir < 0 ? matL : matR);
    m.position.set(p.x, heightAt(E, p.x, p.y) + 2.5, -p.y);
    m.name = `turn_${t.dir < 0 ? 'L' : 'R'}_${t.deg}`;
    g.add(m);
  }

  // ── the obstacles: the three men, and the pickups ───────────────────────
  // Hazards are PEOPLE now, not coloured blocks — the client's redesign. They
  // are modelled standing on the ground rather than floating at a box centre,
  // so the silhouette the readability test measured is the silhouette the
  // player meets. One InstancedMesh per kind, same as everything else here.
  const men = manGeometries();
  const PICKUP = { pw: [0x4ad8c8, 1.2], gem: [0xe8d24a, 1.0], notes: [0x8fd84a, 0.8] };
  const MAN_COL = { low: 0x4a3a52, gate: 0x5c3f63, wall: 0x6b4a73 };
  const byKind = {};
  for (const b of level.beats) (byKind[b.tp] ||= []).push(b);

  for (const k of Object.keys(byKind)) {
    const list = byKind[k];
    const isMan = !!men[k];
    const geo = isMan ? men[k] : new THREE.BoxGeometry(1.2, PICKUP[k][1], 0.5);
    const mat = isMan
      // Lit, not flat: they stand in the world she is running through. The
      // purple range keeps them with the villain the client already has.
      ? new THREE.MeshStandardMaterial({ color: MAN_COL[k], roughness: 0.85, flatShading: true })
      : new THREE.MeshBasicMaterial({ color: PICKUP[k][0], transparent: true, opacity: 0.8 });
    const mesh = new THREE.InstancedMesh(geo, mat, list.length);
    mesh.name = (isMan ? 'man_' : 'slot_') + k;
    mesh.castShadow = isMan;
    mesh.receiveShadow = isMan;
    const d = new THREE.Object3D();
    list.forEach((b, i) => {
      const p = at(b.s);
      const x = p.x + p.nx * b.lane * level.laneM, y = p.y + p.ny * b.lane * level.laneM;
      // Men are authored with their feet at y=0; pickups float at their centre.
      const lift = isMan ? 0 : PICKUP[k][1] / 2 + 0.2;
      d.position.set(x, heightAt(E, x, y) + lift, -y);
      // Facing HER, which is back down the route — they are standing in her way.
      d.rotation.set(0, Math.atan2(-p.nx, -p.ny) + Math.PI / 2, 0);
      d.updateMatrix(); mesh.setMatrixAt(i, d.matrix);
    });
    g.add(mesh);
  }
  return g;
}


/**
 * Everything a level needs once its CENTRELINE exists, shared by both route
 * shapes. A circuit and a point-to-point line differ only in how the polyline
 * is chosen; the climb profile, the beat map, the fairness pass and the stats
 * are identical, and duplicating them is how the two drift apart.
 */
function finishLevel(world, heightAt, E, pts, cum, len, turns, speed, targetM, extra, legs) {
  // ── the climb ────────────────────────────────────────────────────────────
  // Sampled every 10 m. A runner cannot be sent up a 1-in-4; Stone Mountain has
  // 240 m of relief in a 450 m radius, so this is a real constraint there and
  // not a formality.
  const grade = [];
  const gstep = Math.max(E.step || 20, 25);     // never finer than the DEM
  let steepest = 0, climb = 0, drop = 0, prevZ = null;
  for (let s = 0; s <= len; s += gstep) {
    let lo = 0; while (lo < cum.length - 2 && cum[lo + 1] < s) lo++;
    const f = (s - cum[lo]) / ((cum[lo + 1] - cum[lo]) || 1);
    const a = pts[lo], b = pts[lo + 1] || pts[lo];
    const x = a[0] + (b[0] - a[0]) * f, y = a[1] + (b[1] - a[1]) * f;
    const z = heightAt(E, x, y);
    if (prevZ !== null) {
      const g = (z - prevZ) / gstep;
      if (Math.abs(g) > Math.abs(steepest)) steepest = g;
      if (g > 0) climb += z - prevZ; else drop += prevZ - z;
    }
    prevZ = z;
    grade.push(+z.toFixed(2));
  }

  // ── the beat map ─────────────────────────────────────────────────────────
  // Obstacles and note runs laid along `s` at the shipped cadence, converted to
  // metres through the run speed. Corners are kept CLEAR: the shipped game
  // never spawns an obstacle in the same beat as a turn, and a swipe that has
  // to be both a lane change and a corner is not a fair ask.
  const beats = [];
  const clearOf = (s, m) => turns.some((t) => Math.abs(t.s - s) < m);
  let s = speed * BEAT.firstTurn * 0.35, n = 0;   // a little run-up before the first thing
  // SEEDED PER LOCATION. Keyed on the index alone, every level got the SAME
  // beat map — measured: identical impossible sequences at 123 m, 240 m, 327 m
  // and 345 m in all four locations, because the same index produced the same
  // roll everywhere. Four levels sharing one rhythm is four times the same
  // level.
  let seed = 0;
  for (const ch of String(world.location.key || 'x')) seed = Math.imul(seed + ch.charCodeAt(0), 2654435761) | 0;
  const rnd = (i) => {                            // deterministic: a level must replay the same
    let h = Math.imul(i + 1 + seed, 2654435761); h ^= h >>> 15;
    return (Math.imul(h, 2246822519) >>> 0) / 4294967296;
  };
  while (s < len - speed * 2) {
    const r = rnd(n++);
    const gap = speed * (BEAT.obMin + r * (BEAT.obMax - BEAT.obMin));
    s += gap;
    if (clearOf(s, speed * 2.2)) continue;        // leave 2.2 s either side of a corner
    const lane = Math.floor(rnd(n * 7) * LANES) - 1;
    const k = rnd(n * 13);
    // Same mix as the shipped spawn table: low 24%, gate 20%, wall 22%, then
    // power-up, gem and note runs.
    const tp = k < 0.24 ? 'low' : k < 0.44 ? 'gate' : k < 0.66 ? 'wall'
             : k < 0.74 ? 'pw' : k < 0.82 ? 'gem' : 'notes';
    beats.push({ s: +s.toFixed(1), lane, tp });
  }

  // ── FAIRNESS PASS: no sequence the player physically cannot clear ────────
  // Airtime is 0.73 s and a slide is 0.43 s, so two jump obstacles 0.58 s apart
  // in the same lane means she is still airborne when she reaches the second
  // one and lands on it. Measured before this existed: 3-4 such sequences per
  // level. The spawn cadence is lifted from an ENDLESS runner, where the ramp
  // and `adaptF()` keep the density down; a fixed level has to check instead.
  // Preference is to MOVE THE LANE, not delay the beat — delaying erodes the
  // rhythm the cadence exists to produce.
  const RECOVER = { low: BEAT.jumpAir, gate: 0.43, wall: 0.12 };
  const HAZARD = new Set(['low', 'gate', 'wall']);
  let unfair = 0;
  for (let i = 1; i < beats.length; i++) {
    const a = beats[i];
    if (!HAZARD.has(a.tp)) continue;
    let p = null;
    for (let j = i - 1; j >= 0; j--) if (HAZARD.has(beats[j].tp)) { p = beats[j]; break; }
    if (!p) continue;
    const gap = (a.s - p.s) / speed;
    if (gap >= (RECOVER[p.tp] ?? 0.4) || a.lane !== p.lane) continue;
    unfair++;
    // try the other two lanes; a wall still has to leave one lane open
    const alt = [-1, 0, 1].filter((l) => l !== p.lane);
    const taken = new Set(beats.filter((o) => HAZARD.has(o.tp) && Math.abs(o.s - a.s) < speed * 0.4)
                               .map((o) => o.lane));
    const free = alt.find((l) => !taken.has(l));
    if (free !== undefined) a.lane = free;
    else a.s = +(p.s + speed * ((RECOVER[p.tp] ?? 0.4) + 0.05)).toFixed(1);
  }
  beats.sort((x, y) => x.s - y.s);

  const straights = [];
  let last = 0;
  for (const t of turns) { straights.push(t.s - last); last = t.s; }
  straights.push(len - last);

  const stats = {
    lengthM: Math.round(len),
    legs: legs ? legs.length : null,
    runSeconds: +(len / speed).toFixed(1),
    corners: turns.length,
    cornerDegs: turns.map((t) => t.deg),
    // A 45 deg junction asks for the same binary swipe as a 90 and does not
    // look like it needs one. Counted so a level is judged before it is built.
    awkward: turns.filter((t) => t.deg < 60).length,
    nearRight: turns.filter((t) => t.deg >= 60 && t.deg <= 120).length,
    longestStraightM: Math.round(Math.max(...straights)),
    shortestStraightM: Math.round(Math.min(...straights)),
    firstCornerS: turns.length ? +(turns[0].s / speed).toFixed(1) : null,
    maxGradePct: +(steepest * 100).toFixed(1),
    climbM: Math.round(climb),
    dropM: Math.round(drop),
    obstacles: beats.length,
    unfairFixed: unfair,
    targetM,
    corridorM: LANES * LANE_M,
    // THE ONE THAT NEEDS A DECISION: the shipped far plane is 2 s of travel.
    sightM: Math.round(speed * BEAT.sight),
  };

  return { pts, cum, len, turns, grade, beats, legs: legs || null,
           stats: { ...stats, ...extra },
           laneM: LANE_M, lanes: LANES, speed, closed: !!(extra && extra.closed) };
}
