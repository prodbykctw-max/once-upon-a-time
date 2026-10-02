// Resolve the client's Atlanta location list to real OSM features.
//
//   node tools/atlanta/resolve_locations.mjs
//
// Writes tools/atlanta/locations.json — the coordinates and extents every later
// step reads.
//
// GEOCODE WITH NOMINATIM, NOT OVERPASS. Measured from this container: a
// name-regex search across a metro bbox on Overpass is slow and rate-limited
// (65s when it worked, then HTTP 429), while Nominatim answers the same question
// in **0.76s** and hands back the OSM id and a bounding box. Overpass is for
// pulling geometry once you know where you are; Nominatim is for finding out.
// Their usage policy is 1 request/second with a real User-Agent — respected below.
//
// NOTHING IS GUESSED. Every place prints its OSM id and display name so the match
// can be checked. Anything that does not resolve is reported as unresolved rather
// than approximated.
//
// HOME IS DELIBERATELY NOT LOOKED UP. Client: "we're not gonna use our real
// house, because we don't want her actual personal information given out like
// that." It is a fictional house on a representative street — the same move
// Corner Store Dash makes by putting a fictional storefront row on a real block.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const UA = 'jande-once-upon-a-time/1.0 (game world build; contact prodbykctw@gmail.com)';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const WANTED = [
  { key: 'home', label: 'Home', fictional: true,
    note: 'Fictional house on a representative DeKalb residential street — never her real address.' },
  { key: 'wade',     label: 'Wade Walker Park',          q: 'Wade Walker Park, Stone Mountain, Georgia' },
  { key: 'stonemtn', label: 'Stone Mountain Park',       q: 'Stone Mountain Park, Georgia' },
  { key: 'dsa',      label: 'DeKalb School of the Arts', q: 'DeKalb School of the Arts, Georgia' },
  { key: 'track', label: 'Track & Field', ambiguous: true,
    note: 'Which track? Needs the client to name it — likely a school or park track.' },
  { key: 'mbs',    label: 'Mercedes-Benz Stadium', q: 'Mercedes-Benz Stadium, Atlanta, Georgia' },
  // "Old Apache Kafe" — the client's own "old" is the clue. Apache Cafe was a
  // real Atlanta music venue that has since closed, so it may no longer carry a
  // name in OSM. Several spellings are tried before giving up.
  { key: 'apache', label: 'Old Apache Kafe',
    q: ['Apache Cafe, Atlanta, Georgia', 'Apache Kafe, Atlanta',
        'Apache Cafe, 64 3rd Street NW, Atlanta', 'Apache, Peachtree, Atlanta, Georgia'] },
  { key: 'church', label: 'Church', ambiguous: true,
    note: 'Which church? Needs the client. Treat as sensitive if it is hers — same question as Home.' },
];

async function geocode(q) {
  const url = `https://nominatim.openstreetmap.org/search?${new URLSearchParams({
    q, format: 'jsonv2', limit: '1', polygon_geojson: '0',
  })}`;
  const res = await fetch(url, { headers: { 'User-Agent': UA } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const j = await res.json();
  return j[0] || null;
}

const out = {}, report = [];
for (const want of WANTED) {
  if (want.fictional || want.ambiguous) {
    out[want.key] = { label: want.label, resolved: false,
      fictional: !!want.fictional, ambiguous: !!want.ambiguous, note: want.note };
    report.push([want.label, want.fictional ? 'FICTIONAL by design' : 'NEEDS CLIENT', want.note]);
    continue;
  }
  let hit = null, err = null;
  for (const q of [].concat(want.q)) {                // try each spelling in turn
    try { hit = await geocode(q); } catch (e) { err = e.message; }
    await sleep(1100);                                // Nominatim policy: 1 req/sec
    if (hit) break;
  }
  if (!hit) {
    out[want.key] = { label: want.label, resolved: false, note: err || 'no Nominatim match' };
    report.push([want.label, 'UNRESOLVED', err || 'no match']);
    continue;
  }
  const bb = hit.boundingbox.map(Number);             // [minlat, maxlat, minlon, maxlon]
  out[want.key] = {
    label: want.label, resolved: true,
    osm: `${hit.osm_type}/${hit.osm_id}`,
    name: hit.name, display: hit.display_name,
    lat: Number(hit.lat), lon: Number(hit.lon),
    bbox: { minlat: bb[0], maxlat: bb[1], minlon: bb[2], maxlon: bb[3] },
    kind: `${hit.category}/${hit.type}`,
  };
  const spanM = Math.round((bb[1] - bb[0]) * 110540);
  report.push([want.label, `${hit.osm_type}/${hit.osm_id}`,
    `${hit.name} @ ${Number(hit.lat).toFixed(5)}, ${Number(hit.lon).toFixed(5)} · ${hit.category}/${hit.type} · ~${spanM} m tall`]);
}

out._meta = {
  attribution: 'Data © OpenStreetMap contributors, ODbL 1.0 — https://osm.org/copyright',
  geocoder: 'Nominatim', generated: new Date().toISOString().slice(0, 10),
  note: 'A 9th location is still outstanding (client: "we will have a 9th soon").',
};
fs.writeFileSync(path.join(HERE, 'locations.json'), JSON.stringify(out, null, 2));

// Node's console.log has no width specifiers — pad by hand.
const col = (a, b, c) => console.log('  ' + String(a).padEnd(26) + String(b).padEnd(20) + (c || ''));
console.log('');
col('LOCATION', 'OSM', 'DETAIL');
for (const [a, b, c] of report) col(a, b, c);
const n = Object.values(out).filter((v) => v && v.resolved).length;
console.log(`\n  ${n} of ${WANTED.length} resolved · 2 need the client · 1 fictional by design · a 9th still to come`);
