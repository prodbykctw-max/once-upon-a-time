/**
 * Jandé — Once Upon A Time · global leaderboard Worker
 *
 * Endpoints:
 *   GET  /top?mode=all|side|temple&n=20   → { ok, mode, runs:[{n,d,s,m,t}] }
 *   POST /submit  { name, dist, score, mode, dur }  → { ok, rank }
 *   POST /registry { name?, email }                → { ok }   (Queen's Registry sign-up)
 *   GET  /registry/export  (Authorization: Bearer <REGISTRY_EXPORT_KEY>) → { ok, count, signups }
 *
 * CORS is granted only to the game's own origin (ALLOWED_ORIGIN). A POST
 * /submit from any other Origin (or with none) is refused with 403.
 * Submissions are rate limited per client IP (binding SUBMIT_LIMIT, optional)
 * and must pass the plausibility caps below, which are derived from the game
 * code in index.html (see the comments on each constant).
 *
 * Storage: one KV blob per board ("lb:all"/"lb:side"/"lb:temple"), each a JSON
 * array sorted by distance then score, deduped to each name's best, capped 100.
 * Bind the KV namespace as `LB` (see wrangler.toml).
 *
 * Registry sign-ups live in the same namespace under "registry:<lowercased
 * email>" (so a repeat sign-up overwrites instead of duplicating). The record
 * is also stored as KV metadata so the export needs one list() call per 1000
 * sign-ups, not one get() each. No IP address or location is stored.
 * GET /registry/export answers 404 unless the Worker secret REGISTRY_EXPORT_KEY
 * is set AND the request carries it as a Bearer token.
 */
const ALLOWED_ORIGIN = 'https://prodbykctw-max.github.io';
const MODES = ['side', 'temple'];
const CAP = 100;

// ── Plausibility caps (all derived from index.html, with margin) ─────────────
// Physics runs on a fixed 60Hz step; one metre = one tile (T = 32 px).
// ROYAL RUNNER ('temple'):
//   speed = min(11.5, 5.2 + dist*0.0045) px/step, ×1.7 while CRESCENDO boost
//   → at most 11.5*1.7*60/32 = 36.7 m/s of wall-clock time.
//   Points per metre = 12 × runMult(); runMult ≤ misMult (1 + 0.5 × 10
//   missions = 6) × 2 (×2 SCORE) = 12 → 144/m. The richest single spawn is a
//   tier-3 coin row (6 × 3 × 70 × 12 = 15,120) or ENCORE (70 × 15 × 12 =
//   12,600); spawn spacing is ≥ (330 + speed*30) × adaptF × diffF z-units with
//   adaptF ≥ 0.9, diffF ≥ 0.7 (hard) and 76.8 z-units per metre, i.e. ≥ ~4.5 m.
//   Worst case ≈ 3,300 points per metre; cap at 5,000/m + 100,000 for the
//   per-run extras (trophies at 250 each, turns, gems, near-misses).
const TEMPLE_MAX_MPS = 40;
const TEMPLE_PTS_PER_M = 5000;
const TEMPLE_PTS_BASE = 100000;
const TEMPLE_MAX_DIST = 200000;
// ACTION RPG ('side'): `dist` is the CURRENT stage's furthest column (initGS
// resets it each stage) — a stage is ~330 columns + a 30-column boss arena —
// while score carries across all nine stages and up to 5 continues. So score
// is bounded by run time, not by distance:
//   foe kill ≤ 160 × 12 × 3 (combo cap) = 5,760; boss hit 550 per 16 steps;
//   boss kill 7,000; Grace Note 70 × 12 = 840; stage tally ≤ ~70,000.
//   Cap: 30,000 points per second + 100,000, and 15,000,000 absolute
//   (≈ 14 stage attempts × ~770k, the most a stage can pay out).
const SIDE_MAX_DIST = 600;
const SIDE_PTS_PER_S = 30000;
const SIDE_PTS_BASE = 100000;
const SIDE_MAX_SCORE = 15000000;
// Run duration (seconds of wall-clock time, sent by the client).
const MAX_DUR = 6 * 3600;

/** Returns null when the run is plausible, otherwise a short reason code. */
export function implausible(run) {
  const { m, d, s, dur } = run;
  if (!MODES.includes(m)) return 'mode';
  for (const v of [d, s, dur]) if (!Number.isInteger(v) || v < 0) return 'type';
  if (dur < 1 || dur > MAX_DUR) return 'dur';
  if (d === 0 && s === 0) return 'empty';
  if (m === 'temple') {
    if (d > TEMPLE_MAX_DIST) return 'dist';
    if (d > TEMPLE_MAX_MPS * dur + 25) return 'speed';
    if (s > TEMPLE_PTS_PER_M * d + TEMPLE_PTS_BASE) return 'score';
  } else {
    if (d > SIDE_MAX_DIST) return 'dist';
    if (s > SIDE_MAX_SCORE) return 'score';
    if (s > SIDE_PTS_PER_S * dur + SIDE_PTS_BASE) return 'rate';
  }
  return null;
}

const corsFor = (req) => {
  const o = req.headers.get('Origin');
  const h = { Vary: 'Origin' };
  if (o === ALLOWED_ORIGIN) {
    h['Access-Control-Allow-Origin'] = o;
    h['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS';
    h['Access-Control-Allow-Headers'] = 'Content-Type';
    h['Access-Control-Max-Age'] = '86400';
  }
  return h;
};

const json = (req, o, status = 200) =>
  new Response(JSON.stringify(o), { status, headers: { ...corsFor(req), 'Content-Type': 'application/json' } });

const clampInt = (v, min, max) => {
  v = Math.floor(Number(v));
  if (!isFinite(v)) return min;
  return Math.max(min, Math.min(max, v));
};

// Strict numeric parse: only JSON numbers (no strings), finite and >= 0, floored.
const asInt = (v) => (typeof v === 'number' && Number.isFinite(v) && v >= 0 ? Math.floor(v) : -1);

const cleanName = (n) => {
  const s = String(n == null ? '' : n).replace(/[^\p{L}\p{N} .!'\-]/gu, '').trim().slice(0, 16);
  return s || 'JANDÉ FAN';
};

// ── Queen's Registry (fan email sign-ups) ────────────────────────────────────
// Deliberately loose: never refuse a real fan. Only "has an @" and sane maxima.
const REG_MAX_BODY = 2048;
const REG_MAX_EMAIL = 254;
const REG_MAX_NAME = 80;
const regKey = (email) => 'registry:' + email.toLowerCase();
const cleanText = (v, max) => String(v == null ? '' : v).replace(/[\u0000-\u001f\u007f]/g, '').trim().slice(0, max);

/** Constant-time string compare (digests are equal length, XOR-accumulated). */
async function safeEqual(a, b) {
  const enc = new TextEncoder();
  const [da, db] = await Promise.all([
    crypto.subtle.digest('SHA-256', enc.encode(String(a))),
    crypto.subtle.digest('SHA-256', enc.encode(String(b))),
  ]);
  const x = new Uint8Array(da), y = new Uint8Array(db);
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

const sortRuns = (a, b) => b.d - a.d || b.s - a.s || a.t - b.t;

function dedupeTrim(list) {
  const seen = new Set(), out = [];
  for (const r of list) {
    const k = r.n.toLowerCase();
    if (seen.has(k)) continue;
    seen.add(k);
    out.push(r);
    if (out.length >= CAP) break;
  }
  return out;
}

const getList = async (env, key) => {
  const s = await env.LB.get('lb:' + key);
  return s ? JSON.parse(s) : [];
};
const putList = (env, key, list) => env.LB.put('lb:' + key, JSON.stringify(list.slice(0, CAP)));

export default {
  async fetch(req, env) {
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: corsFor(req) });
    const url = new URL(req.url);
    try {
      if (url.pathname === '/top' && req.method === 'GET') {
        const q = url.searchParams.get('mode');
        const mode = MODES.includes(q) ? q : 'all';
        const n = clampInt(url.searchParams.get('n') || 20, 1, 50);
        const list = await getList(env, mode);
        return json(req, { ok: true, mode, runs: list.slice(0, n) });
      }

      if (url.pathname === '/submit' && req.method === 'POST') {
        if (req.headers.get('Origin') !== ALLOWED_ORIGIN) return json(req, { ok: false, err: 'forbidden' }, 403);
        if (env.SUBMIT_LIMIT) {
          const ip = req.headers.get('CF-Connecting-IP') || 'unknown';
          const { success } = await env.SUBMIT_LIMIT.limit({ key: ip });
          if (!success) return json(req, { ok: false, err: 'slow down' }, 429);
        }
        const b = await req.json().catch(() => ({}));
        const run = {
          n: cleanName(b && b.name),
          d: asInt(b && b.dist),
          s: asInt(b && b.score),
          m: b && b.mode,
          dur: asInt(b && b.dur),
        };
        const why = implausible(run);
        if (why) return json(req, { ok: false, err: 'rejected' }, 400);
        const mode = run.m;
        const entry = { n: run.n, d: run.d, s: run.s, m: mode, t: Date.now() };

        let rank = 0;
        for (const key of [mode, 'all']) {
          const list = dedupeTrim([...(await getList(env, key)), entry].sort(sortRuns));
          await putList(env, key, list);
          if (key === mode) {
            const i = list.findIndex((r) => r.t === entry.t && r.n === entry.n);
            rank = i >= 0 ? i + 1 : 0;
          }
        }
        return json(req, { ok: true, rank });
      }

      if (url.pathname === '/registry' && req.method === 'POST') {
        if (req.headers.get('Origin') !== ALLOWED_ORIGIN) return json(req, { ok: false, err: 'forbidden' }, 403);
        const declared = Number(req.headers.get('Content-Length') || 0);
        if (declared > REG_MAX_BODY) return json(req, { ok: false, err: 'too large' }, 413);
        const raw = await req.text();
        if (raw.length > REG_MAX_BODY) return json(req, { ok: false, err: 'too large' }, 413);
        let b = {};
        try { b = JSON.parse(raw); } catch (e) { b = {}; }
        const email = cleanText(b && b.email, REG_MAX_EMAIL + 1);
        if (!email || email.length > REG_MAX_EMAIL || email.indexOf('@') < 1) {
          return json(req, { ok: false, err: 'rejected' }, 400);
        }
        const rec = { n: cleanText(b && b.name, REG_MAX_NAME), e: email, t: new Date().toISOString() };
        await env.LB.put(regKey(email), JSON.stringify(rec), { metadata: rec });
        return json(req, { ok: true });
      }

      if (url.pathname === '/registry/export' && req.method === 'GET') {
        const secret = env.REGISTRY_EXPORT_KEY;
        const m = /^Bearer (.+)$/.exec(req.headers.get('Authorization') || '');
        // Same 404 for "no secret configured", "no header" and "wrong key".
        if (!secret || !m || !(await safeEqual(m[1], secret))) return json(req, { ok: false, err: 'not found' }, 404);
        const signups = [];
        let cursor;
        do {
          const page = await env.LB.list({ prefix: 'registry:', cursor });
          for (const k of page.keys) {
            let r = k.metadata;
            if (!r || !r.e) { const v = await env.LB.get(k.name); r = v ? JSON.parse(v) : null; }
            if (r && r.e) signups.push({ name: r.n, email: r.e, time: r.t });
          }
          cursor = page.list_complete ? undefined : page.cursor;
        } while (cursor);
        signups.sort((a, b) => (a.time < b.time ? -1 : a.time > b.time ? 1 : 0));
        return json(req, { ok: true, count: signups.length, signups });
      }

      return json(req, { ok: false, err: 'not found' }, 404);
    } catch (e) {
      return json(req, { ok: false, err: 'server error' }, 500);
    }
  },
};
