// A RUN YOU CAN ACTUALLY FAIL — lanes, jump, slide, collision.
//
// Until this existed the obstacle slots were drawn and nothing touched them,
// which meant the level data had never been tested by the only thing that can
// test it: running the level. Everything here matches the shipped Royal Runner's
// model so the Atlanta levels drop into the game rather than beside it.
//
//   lanes ........ t3.lane is -1 / 0 / 1, eased by `(lane - laneX) * 0.28`
//   jump ......... 0.73 s of airtime (2*13.5/0.62 frames)
//   slide ........ t3.slid = 26 frames = 0.43 s
//   obstacles .... 'low' jump it · 'gate' slide under · 'wall' change lane
//
// GRAVITY IS NOT 9.81. Keeping the shipped 0.73 s airtime under real gravity
// gives an apex of 0.65 m, and the 'low' obstacle is 0.9 m tall — she would
// clear nothing. A runner's jump is a game feel, not ballistics: apex 1.2 m in
// 0.73 s needs g = 8h/t^2 = 18 m/s^2, which is 1.8g and is what the shipped
// arc is already doing in its own units.
const JUMP_APEX = 1.2;          // m
const JUMP_AIR = 0.73;          // s, from the shipped sheet
const GRAV = (8 * JUMP_APEX) / (JUMP_AIR * JUMP_AIR);
const JUMP_V0 = GRAV * JUMP_AIR / 2;
const SLIDE_T = 0.43;           // s
const LANE_EASE = 0.28;         // per 60 Hz frame, as shipped

// How tall she is standing and sliding — these decide what she clears.
const BODY_H = 1.70, SLIDE_H = 0.80;
// Hit box along the route. The shipped window is +-34 of a 1500 z far plane;
// in metres, half a stride.
const HIT_S = 0.7, HIT_D = 0.75;

/** What each obstacle demands, and the space it occupies. */
const OB = {
  low:   { h: 0.90, needs: 'jump',  blocks: (st) => st.y < 0.90 },
  gate:  { h: 1.90, needs: 'slide', blocks: (st) => st.height > 1.20 },
  wall:  { h: 2.40, needs: 'lane',  blocks: () => true },
  pw:    { pickup: true },
  gem:   { pickup: true },
  notes: { pickup: true },
};

export function createRun(level, heightAt, E) {
  const st = {
    s: 0, lane: 0, laneX: 0, y: 0, vy: 0, slide: 0,
    height: BODY_H, speed: level.speed,
    hits: 0, picked: 0, done: false, lastHit: null, t: 0,
    // every slot starts live; a slot is consumed once resolved either way
    slots: level.beats.map((b) => ({ ...b, used: false })),
  };

  /** Point, heading and ground height at distance `s` along the route. */
  function at(s) {
    const { pts, cum } = level;
    let lo = 0, hi = cum.length - 1;
    while (lo < hi - 1) { const m = (lo + hi) >> 1; if (cum[m] <= s) lo = m; else hi = m; }
    const a = pts[lo], b = pts[lo + 1] || pts[lo];
    const seg = (cum[lo + 1] - cum[lo]) || 1;
    const f = Math.max(0, Math.min(1, (s - cum[lo]) / seg));
    const x = a[0] + (b[0] - a[0]) * f, y = a[1] + (b[1] - a[1]) * f;
    const dx = (b[0] - a[0]) / seg, dy = (b[1] - a[1]) / seg;
    return { x, y, dx, dy, nx: dy, ny: -dx, h: Math.atan2(dx, dy) };
  }
  st.at = at;

  /** Her world position, including lane offset and jump height. */
  st.pose = () => {
    const p = at(st.s);
    const x = p.x + p.nx * st.laneX * level.laneM;
    const y = p.y + p.ny * st.laneX * level.laneM;
    return { x, y, z: heightAt(E, x, y) + st.y, head: p.h };
  };

  /** input: {left, right, jump, slide} — edge-triggered by the caller. */
  st.update = (dt, input = {}) => {
    if (st.done) return st;
    st.t += dt;

    if (input.left && st.lane > -1) st.lane--;
    if (input.right && st.lane < 1) st.lane++;
    // The shipped ease is per 60 Hz frame; make it frame-rate independent or a
    // 120 Hz phone changes lanes twice as fast as a 60 Hz one.
    st.laneX += (st.lane - st.laneX) * (1 - Math.pow(1 - LANE_EASE, dt * 60));

    if (input.jump && st.y <= 0 && st.slide <= 0) st.vy = JUMP_V0;
    if (st.vy !== 0 || st.y > 0) {
      st.vy -= GRAV * dt; st.y += st.vy * dt;
      if (st.y <= 0) { st.y = 0; st.vy = 0; }
    }
    if (input.slide && st.y <= 0 && st.slide <= 0) st.slide = SLIDE_T;
    if (st.slide > 0) st.slide = Math.max(0, st.slide - dt);
    st.height = st.slide > 0 ? SLIDE_H : BODY_H;

    st.s += st.speed * dt;
    if (st.s >= level.len) { st.s = level.len; st.done = true; }

    // ── collision ─────────────────────────────────────────────────────────
    // Only slots within the hit window are tested, and the list is sorted by
    // `s`, so this is a short scan rather than a pass over every slot.
    for (const o of st.slots) {
      if (o.used) continue;
      if (o.s < st.s - HIT_S) { o.used = true; continue; }   // passed it
      if (o.s > st.s + HIT_S) break;                          // not there yet
      if (Math.abs(o.lane - st.laneX) > HIT_D) continue;      // different lane
      const def = OB[o.tp];
      if (!def) { o.used = true; continue; }
      o.used = true;
      if (def.pickup) { st.picked++; o.got = true; continue; }
      if (def.blocks(st)) { st.hits++; st.lastHit = { tp: o.tp, s: o.s, t: st.t }; o.hit = true; }
      else o.cleared = true;
    }
    return st;
  };

  /**
   * How far ahead the next obstacle is, in metres and in SECONDS OF REACTION.
   *
   * This is the number the "10 m sight line" was really about. The shipped
   * runner spawns obstacles at a far plane 2.0 s of travel away, and 2.0 s is a
   * fine reaction window — but in an endless runner that is also the moment the
   * obstacle appears, so in a real city it would POP into existence 10 m in
   * front of her. In a LEVEL the obstacles are placed along the route and drawn
   * from as far as the camera can see; only the DECISION point is 2 s out.
   * Draw distance and reaction window are different numbers, and conflating
   * them is what made 10 m look like a problem.
   */
  st.lookahead = () => {
    for (const o of st.slots) {
      if (o.used || o.s < st.s) continue;
      if (OB[o.tp] && OB[o.tp].pickup) continue;
      return { m: +(o.s - st.s).toFixed(1), s: +((o.s - st.s) / st.speed).toFixed(2), tp: o.tp, lane: o.lane };
    }
    return null;
  };

  st.reset = () => {
    st.s = 0; st.lane = 0; st.laneX = 0; st.y = 0; st.vy = 0; st.slide = 0;
    st.hits = 0; st.picked = 0; st.done = false; st.lastHit = null; st.t = 0;
    for (const o of st.slots) { o.used = o.hit = o.got = o.cleared = false; }
    return st;
  };

  return st;
}

export const PLAY = { JUMP_APEX, JUMP_AIR, GRAV, SLIDE_T, BODY_H, SLIDE_H, HIT_S, HIT_D };
