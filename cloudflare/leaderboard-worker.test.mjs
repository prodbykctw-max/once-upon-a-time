// node --test cloudflare/leaderboard-worker.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import worker, { implausible } from './leaderboard-worker.js';
const ALLOWED_ORIGIN = 'https://prodbykctw-max.github.io';

const kv = () => {
  const m = new Map(), meta = new Map();
  return {
    get: async (k) => m.get(k) ?? null,
    put: async (k, v, o) => { m.set(k, v); if (o && o.metadata) meta.set(k, o.metadata); },
    list: async ({ prefix = '' } = {}) => ({
      keys: [...m.keys()].filter((k) => k.startsWith(prefix)).map((name) => ({ name, metadata: meta.get(name) })),
      list_complete: true,
    }),
    m,
  };
};
const limiter = (n) => { let c = 0; return { limit: async () => ({ success: ++c <= n }) }; };
const BASE = 'https://jande-leaderboard.example';
const post = (body, origin = ALLOWED_ORIGIN, ip = '1.2.3.4') =>
  new Request(BASE + '/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(origin ? { Origin: origin } : {}), 'CF-Connecting-IP': ip },
    body: JSON.stringify(body),
  });
const good = { name: 'Fan', dist: 1200, score: 60000, mode: 'temple', dur: 90 };

test('honest runs pass', () => {
  assert.equal(implausible({ m: 'temple', d: 1200, s: 60000, dur: 90 }), null);
  // runner at top boost the whole time, max score per metre
  assert.equal(implausible({ m: 'temple', d: 3600, s: 3300 * 3600, dur: 100 }), null);
  // RPG: dist is the current stage only, score carries across stages
  assert.equal(implausible({ m: 'side', d: 40, s: 900000, dur: 900 }), null);
  assert.equal(implausible({ m: 'side', d: 360, s: 4500, dur: 30 }), null);
});

test('implausible runs are rejected', () => {
  assert.equal(implausible({ m: 'temple', d: 999999, s: 1, dur: 99999 }), 'dur');
  assert.equal(implausible({ m: 'temple', d: 5000, s: 1, dur: 60 }), 'speed');
  assert.equal(implausible({ m: 'temple', d: 100, s: 100000000, dur: 60 }), 'score');
  assert.equal(implausible({ m: 'side', d: 5000, s: 1, dur: 60 }), 'dist');
  assert.equal(implausible({ m: 'side', d: 100, s: 5000000, dur: 30 }), 'rate');
  assert.equal(implausible({ m: 'side', d: 100, s: 99000000, dur: 21000 }), 'score');
  assert.equal(implausible({ m: 'side', d: 0, s: 0, dur: 5 }), 'empty');
  assert.equal(implausible({ m: 'side', d: 10, s: 10, dur: -1 }), 'type');
  assert.equal(implausible({ m: 'boss', d: 10, s: 10, dur: 5 }), 'mode');
});

test('submit: allowed origin stores the run and echoes CORS', async () => {
  const env = { LB: kv(), SUBMIT_LIMIT: limiter(5) };
  const r = await worker.fetch(post(good), env);
  assert.equal(r.status, 200);
  assert.equal(r.headers.get('Access-Control-Allow-Origin'), ALLOWED_ORIGIN);
  assert.deepEqual(await r.json(), { ok: true, rank: 1 });
  const top = await worker.fetch(new Request(BASE + '/top?mode=temple', { headers: { Origin: ALLOWED_ORIGIN } }), env);
  const j = await top.json();
  assert.equal(j.runs.length, 1);
  assert.equal(j.runs[0].d, 1200);
  assert.equal(j.runs[0].dur, undefined, 'dur is not stored');
});

test('submit: foreign or missing Origin is 403 and writes nothing', async () => {
  const env = { LB: kv() };
  for (const o of ['https://evil.example', null, 'https://prodbykctw-max.github.io.evil.example']) {
    const r = await worker.fetch(post(good, o), env);
    assert.equal(r.status, 403);
    assert.equal(r.headers.get('Access-Control-Allow-Origin'), null);
  }
  assert.equal(env.LB.m.size, 0);
});

test('submit: implausible and malformed bodies are 400 without detail', async () => {
  const env = { LB: kv() };
  for (const b of [
    { ...good, score: 1e9 },
    { ...good, dist: '1200' },
    { ...good, dur: undefined },
    { ...good, mode: 'all' },
  ]) {
    const r = await worker.fetch(post(b), env);
    assert.equal(r.status, 400);
    assert.deepEqual(await r.json(), { ok: false, err: 'rejected' });
  }
  assert.equal(env.LB.m.size, 0);
});

test('submit: rate limit returns 429 after 5', async () => {
  const env = { LB: kv(), SUBMIT_LIMIT: limiter(5) };
  const codes = [];
  for (let i = 0; i < 7; i++) codes.push((await worker.fetch(post({ ...good, name: 'P' + i }), env)).status);
  assert.deepEqual(codes, [200, 200, 200, 200, 200, 429, 429]);
});

test('existing board data is kept', async () => {
  const env = { LB: kv() };
  const old = [{ n: 'Legacy', d: 5000, s: 1, m: 'temple', t: 1 }];
  await env.LB.put('lb:temple', JSON.stringify(old));
  await worker.fetch(post(good), env);
  const list = JSON.parse(await env.LB.get('lb:temple'));
  assert.deepEqual(list.map((r) => r.n), ['Legacy', 'Fan']);
});

test('500 never leaks the error message', async () => {
  const env = { LB: { get: async () => { throw new Error('KV secret detail'); }, put: async () => {} } };
  const r = await worker.fetch(new Request(BASE + '/top'), env);
  assert.equal(r.status, 500);
  assert.deepEqual(await r.json(), { ok: false, err: 'server error' });
});

test('preflight: only the game origin gets CORS', async () => {
  const ok = await worker.fetch(new Request(BASE + '/submit', { method: 'OPTIONS', headers: { Origin: ALLOWED_ORIGIN } }), {});
  assert.equal(ok.headers.get('Access-Control-Allow-Origin'), ALLOWED_ORIGIN);
  const bad = await worker.fetch(new Request(BASE + '/submit', { method: 'OPTIONS', headers: { Origin: 'https://x.example' } }), {});
  assert.equal(bad.headers.get('Access-Control-Allow-Origin'), null);
});

// ── Queen's Registry ─────────────────────────────────────────────────────────
const reg = (body, origin = ALLOWED_ORIGIN) =>
  new Request(BASE + '/registry', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(origin ? { Origin: origin } : {}) },
    body: typeof body === 'string' ? body : JSON.stringify(body),
  });
const exp = (key) =>
  new Request(BASE + '/registry/export', { headers: key === undefined ? {} : { Authorization: 'Bearer ' + key } });
const regKeys = (env) => [...env.LB.m.keys()].filter((k) => k.startsWith('registry:'));

test('registry: saves a sign-up with a server timestamp and echoes CORS', async () => {
  const env = { LB: kv(), REGISTRY_EXPORT_KEY: 'k1' };
  const r = await worker.fetch(reg({ name: 'Test Fan', email: 'fan@example.test' }), env);
  assert.equal(r.status, 200);
  assert.equal(r.headers.get('Access-Control-Allow-Origin'), ALLOWED_ORIGIN);
  assert.deepEqual(await r.json(), { ok: true });
  assert.deepEqual(regKeys(env), ['registry:fan@example.test']);
  const rec = JSON.parse(env.LB.m.get('registry:fan@example.test'));
  assert.deepEqual(Object.keys(rec).sort(), ['e', 'n', 't'], 'only name, email, timestamp are stored');
  assert.equal(rec.e, 'fan@example.test');
  assert.ok(Math.abs(Date.parse(rec.t) - Date.now()) < 5000);
});

test('registry: same email twice overwrites (case-insensitive), no duplicate', async () => {
  const env = { LB: kv(), REGISTRY_EXPORT_KEY: 'k1' };
  await worker.fetch(reg({ name: 'First', email: 'Fan@Example.test' }), env);
  await worker.fetch(reg({ name: 'Second', email: 'fan@example.test' }), env);
  assert.equal(regKeys(env).length, 1);
  const j = await (await worker.fetch(exp('k1'), env)).json();
  assert.equal(j.count, 1);
  assert.equal(j.signups[0].name, 'Second');
});

test('registry: name is optional; loose checks accept real fans, refuse non-emails', async () => {
  const env = { LB: kv() };
  assert.equal((await worker.fetch(reg({ email: 'a@b' }), env)).status, 200);
  assert.equal((await worker.fetch(reg({ name: 'ÉmilieÅ 王', email: ' x+tag@sub.example.test ' }), env)).status, 200);
  for (const b of [{ email: '' }, { email: 'no-at-sign' }, { name: 'x' }, { email: 5 }, '{not json', { email: 'a@' + 'b'.repeat(300) }]) {
    const r = await worker.fetch(reg(b), env);
    assert.equal(r.status, 400);
    assert.deepEqual(await r.json(), { ok: false, err: 'rejected' });
  }
  assert.equal(regKeys(env).length, 2);
});

test('registry: oversized body is 413 and long names are trimmed, not refused', async () => {
  const env = { LB: kv() };
  const big = await worker.fetch(reg({ email: 'a@b.test', name: 'x'.repeat(5000) }), env);
  assert.equal(big.status, 413);
  const ok = await worker.fetch(reg({ email: 'a@b.test', name: 'y'.repeat(300) }), env);
  assert.equal(ok.status, 200);
  assert.equal(JSON.parse(env.LB.m.get('registry:a@b.test')).n.length, 80);
});

test('registry: foreign or missing Origin is 403 and writes nothing', async () => {
  const env = { LB: kv() };
  for (const o of ['https://evil.example', null, 'https://prodbykctw-max.github.io.evil.example']) {
    const r = await worker.fetch(reg({ email: 'a@b.test' }, o), env);
    assert.equal(r.status, 403);
    assert.equal(r.headers.get('Access-Control-Allow-Origin'), null);
  }
  assert.equal(env.LB.m.size, 0);
});

test('registry: preflight from the game origin is allowed', async () => {
  const r = await worker.fetch(new Request(BASE + '/registry', { method: 'OPTIONS', headers: { Origin: ALLOWED_ORIGIN } }), {});
  assert.equal(r.status, 204);
  assert.equal(r.headers.get('Access-Control-Allow-Origin'), ALLOWED_ORIGIN);
});

test('registry export: 404 without key, wrong key, or when the secret is unset', async () => {
  const withSecret = { LB: kv(), REGISTRY_EXPORT_KEY: 'right-key' };
  await worker.fetch(reg({ email: 'a@b.test' }), withSecret);
  for (const k of [undefined, 'wrong-key', '', 'right-keY']) {
    const r = await worker.fetch(exp(k), withSecret);
    assert.equal(r.status, 404);
    assert.deepEqual(await r.json(), { ok: false, err: 'not found' });
  }
  const noSecret = { LB: kv() };
  await worker.fetch(reg({ email: 'a@b.test' }), noSecret);
  for (const k of [undefined, 'right-key', 'undefined', '']) assert.equal((await worker.fetch(exp(k), noSecret)).status, 404);
  // a non-Bearer scheme with the right key is refused too
  const basic = new Request(BASE + '/registry/export', { headers: { Authorization: 'Basic right-key' } });
  assert.equal((await worker.fetch(basic, withSecret)).status, 404);
});

test('registry export: right key returns every sign-up, oldest first, no extra fields', async () => {
  const env = { LB: kv(), REGISTRY_EXPORT_KEY: 'right-key' };
  await worker.fetch(reg({ name: 'A', email: 'a@x.test' }), env);
  await new Promise((r) => setTimeout(r, 5));
  await worker.fetch(reg({ name: 'B', email: 'b@x.test' }), env);
  const r = await worker.fetch(exp('right-key'), env);
  assert.equal(r.status, 200);
  const j = await r.json();
  assert.equal(j.ok, true);
  assert.equal(j.count, 2);
  assert.deepEqual(j.signups.map((s) => s.email), ['a@x.test', 'b@x.test']);
  assert.deepEqual(Object.keys(j.signups[0]).sort(), ['email', 'name', 'time']);
});

test('registry does not touch the leaderboard: boards unchanged, board data not exported', async () => {
  const env = { LB: kv(), SUBMIT_LIMIT: limiter(5), REGISTRY_EXPORT_KEY: 'k' };
  await worker.fetch(post(good), env);
  const before = env.LB.m.get('lb:temple');
  await worker.fetch(reg({ name: 'Fan', email: 'f@x.test' }), env);
  assert.equal(env.LB.m.get('lb:temple'), before);
  assert.equal(env.LB.m.has('lb:all'), true);
  const top = await (await worker.fetch(new Request(BASE + '/top?mode=temple'), env)).json();
  assert.equal(top.runs.length, 1);
  const j = await (await worker.fetch(exp('k'), env)).json();
  assert.equal(j.count, 1);
  // sign-ups never use the rate-limit binding that guards score submits
  const tight = { LB: kv(), SUBMIT_LIMIT: limiter(0) };
  assert.equal((await worker.fetch(reg({ email: 'a@b.test' }), tight)).status, 200);
});
