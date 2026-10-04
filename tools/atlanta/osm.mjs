// Overpass fetch helper for the Atlanta world build.
//
// MIRROR CHOICE IS MEASURED, NOT PREFERENCE. From this container the main
// endpoint `overpass-api.de` resets the connection every time, ~7.5s in
// (the proxy logs it as `ws_closed_mid_exchange`). `overpass.kumi.systems`
// answers the same query HTTP 200 — but took **65 seconds**, because Overpass
// queues. So: kumi first, generous timeouts, and never assume a slow reply is
// a dead one.
//
// Everything is cached to disk. Raw OSM is git-ignored (same as the Corner
// Store Dash project does with `drive/osm/`) — it is large, re-fetchable, and
// not ours to vendor.
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const CACHE = path.join(HERE, 'cache');
fs.mkdirSync(CACHE, { recursive: true });

// MEASURED FROM THIS CONTAINER, in the order that actually works:
//   overpass.openstreetmap.fr   0.96s  <- fast and reliable; the one to use
//   overpass.kumi.systems       65s, then 429/504 under any real load
//   overpass.private.coffee     same queuing, then 429
//   overpass-api.de             relay closes the tunnel ~8s in, every time
//   overpass.osm.ch             answers, but returns 0 elements for Atlanta
//                               (regional instance — not a global database)
const MIRRORS = [
  'https://overpass.openstreetmap.fr/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter',
  'https://overpass.private.coffee/api/interpreter',
  'https://overpass-api.de/api/interpreter',
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// SEND A REAL USER-AGENT. The same query that curl got a 200 for came back 403
// from Node's fetch, because fetch sends a bare UA and Overpass instances reject
// anonymous clients. It reads as "this mirror is blocking us" and is nothing of
// the kind. Nominatim's policy asks for the same thing.
const UA = 'jande-once-upon-a-time/1.0 (game world build; contact prodbykctw@gmail.com)';

/** Run an Overpass QL query, with on-disk caching keyed by `name`. */
export async function overpass(name, query, { timeoutMs = 180000, force = false } = {}) {
  // THE QUERY IS PART OF THE CACHE KEY. It was not, and that is a quiet, nasty
  // bug: widening the query to pull bare_rock changed nothing at all, because
  // every location returned its old cached answer and the counts looked
  // identical. A cache keyed on less than its inputs does not fail loudly — it
  // tells you your change did nothing.
  const sig = crypto.createHash('sha1').update(query).digest('hex').slice(0, 8);
  const file = path.join(CACHE, `${name}_${sig}.json`);
  if (!force && fs.existsSync(file)) {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  }
  let lastErr;
  for (const url of MIRRORS) {
    for (let attempt = 1; attempt <= 3; attempt++) {
      const ac = new AbortController();
      const t = setTimeout(() => ac.abort(), timeoutMs);
      const t0 = Date.now();
      try {
        const res = await fetch(url, {
          method: 'POST',
          body: new URLSearchParams({ data: query }),
          headers: { 'User-Agent': UA, Accept: 'application/json' },
          signal: ac.signal,
        });
        clearTimeout(t);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        const secs = ((Date.now() - t0) / 1000).toFixed(1);
        console.log(`  ${name}: ${json.elements?.length ?? 0} elements from ${new URL(url).host} in ${secs}s`);
        fs.writeFileSync(file, JSON.stringify(json));
        return json;
      } catch (e) {
        clearTimeout(t);
        lastErr = e;
        console.log(`  ${name}: ${new URL(url).host} attempt ${attempt} failed — ${e.message}`);
        // 429/503 are load, not refusal: Overpass clears in tens of seconds.
        // 406 is a QUERY SYNTAX ERROR — retrying it is pointless, so bail early.
        if (/HTTP 406/.test(e.message)) { console.log('    (406 = malformed Overpass QL — fix the query, not the retry)'); break; }
        if (/HTTP 403/.test(e.message)) { console.log('    (403 = the mirror refused this client, not this query)'); break; }
        const wait = /HTTP (429|503|504)/.test(e.message) ? 30000 : 4000;
        if (attempt < 3) await sleep(wait);
      }
    }
  }
  throw new Error(`Overpass failed for ${name}: ${lastErr?.message}`);
}

/** Metres-per-degree at a latitude, for the local-metre frame. */
export const scaleAt = (lat) => ({
  kx: 111320 * Math.cos((lat * Math.PI) / 180),
  ky: 110540,
});

/** Centre of an OSM element, handling node / way / relation shapes. */
export function centreOf(el) {
  if (el.type === 'node') return { lat: el.lat, lon: el.lon };
  if (el.center) return { lat: el.center.lat, lon: el.center.lon };
  if (el.bounds) {
    return {
      lat: (el.bounds.minlat + el.bounds.maxlat) / 2,
      lon: (el.bounds.minlon + el.bounds.maxlon) / 2,
    };
  }
  return null;
}
