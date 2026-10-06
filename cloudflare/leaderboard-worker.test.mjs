// node --test cloudflare/leaderboard-worker.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import worker, { implausible } from './leaderboard-worker.js';
const ALLOWED_ORIGIN = 'https://prodbykctw-max.github.io';

const kv = () => {
  const m = new Map();
  return { get: async (k) => m.get(k) ?? null, put: async (k, v) => void m.set(k, v), m };
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
