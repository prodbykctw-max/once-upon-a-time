/**
 * Jandé — Once Upon A Time · global leaderboard Worker
 *
 * Endpoints (CORS open — public promo game):
 *   GET  /top?mode=all|side|temple&n=20   → { ok, mode, runs:[{n,d,s,m,t}] }
 *   POST /submit  { name, dist, score, mode }  → { ok, rank }
 *
 * Storage: one KV blob per board ("lb:all"/"lb:side"/"lb:temple"), each a JSON
 * array sorted by distance then score, deduped to each name's best, capped 100.
 * Bind the KV namespace as `LB` (see wrangler.toml).
 */
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Max-Age': '86400',
};
const MODES = ['side', 'temple'];
const CAP = 100;

const json = (o, status = 200) =>
  new Response(JSON.stringify(o), { status, headers: { ...CORS, 'Content-Type': 'application/json' } });

const clampInt = (v, min, max) => {
  v = Math.floor(Number(v));
  if (!isFinite(v)) return min;
  return Math.max(min, Math.min(max, v));
};

const cleanName = (n) => {
  const s = String(n == null ? '' : n).replace(/[^\p{L}\p{N} .!'\-]/gu, '').trim().slice(0, 16);
  return s || 'JANDÉ FAN';
};

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
    if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });
    const url = new URL(req.url);
    try {
      if (url.pathname === '/top' && req.method === 'GET') {
        const q = url.searchParams.get('mode');
        const mode = MODES.includes(q) ? q : 'all';
        const n = clampInt(url.searchParams.get('n') || 20, 1, 50);
        const list = await getList(env, mode);
        return json({ ok: true, mode, runs: list.slice(0, n) });
      }

      if (url.pathname === '/submit' && req.method === 'POST') {
        const b = await req.json().catch(() => ({}));
        const mode = MODES.includes(b.mode) ? b.mode : 'side';
        const run = {
          n: cleanName(b.name),
          d: clampInt(b.dist, 0, 1000000),
          s: clampInt(b.score, 0, 100000000),
          m: mode,
          t: Date.now(),
        };
        if (run.d === 0 && run.s === 0) return json({ ok: false, err: 'empty run' }, 400);

        let rank = 0;
        for (const key of [mode, 'all']) {
          const list = dedupeTrim([...(await getList(env, key)), run].sort(sortRuns));
          await putList(env, key, list);
          if (key === mode) {
            const i = list.findIndex((r) => r.t === run.t && r.n === run.n);
            rank = i >= 0 ? i + 1 : 0;
          }
        }
        return json({ ok: true, rank });
      }

      return json({ ok: false, err: 'not found' }, 404);
    } catch (e) {
      return json({ ok: false, err: String((e && e.message) || e) }, 500);
    }
  },
};
