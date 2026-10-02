// OSM extract → world.json in LOCAL METRES, one file per Atlanta location.
//
//   node tools/atlanta/build_world.mjs mbs [radius_m]
//
// Adapted from EBT-PRESENTS-CORNER-STORE-DASH's drive/tools/build_world.mjs,
// whose key idea is the one worth copying: **one source of truth that both the
// Blender build and the game engine read.** Geometry is emitted in metres from a
// local origin, so nothing downstream ever handles latitude and longitude again.
//
// Frame: origin = the location centre, +x east, +y north, metres.
//
// This is the step that is engine-agnostic. Whatever renders Game II —
// three.js per the 10-02 decision — consumes this, and so does Blender.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { overpass, scaleAt } from './osm.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const LOCS = JSON.parse(fs.readFileSync(path.join(HERE, 'locations.json'), 'utf8'));

const key = process.argv[2];
const RADIUS = Number(process.argv[3] || 350);        // metres around the centre
const loc = LOCS[key];
if (!loc) { console.error(`unknown location "${key}" — have: ${Object.keys(LOCS).filter(k => k[0] !== '_').join(', ')}`); process.exit(1); }
if (!loc.resolved) { console.error(`"${loc.label}" is not resolved: ${loc.note || ''}`); process.exit(1); }

const { lat, lon } = loc;
const { kx, ky } = scaleAt(lat);
const toXY = (n) => [ +((n.lon - lon) * kx).toFixed(2), +((n.lat - lat) * ky).toFixed(2) ];

// One bbox query for everything, so it is a single Overpass hit rather than
// several — the mirrors rate-limit aggressively (HTTP 429 after two queries).
const dLat = RADIUS / ky, dLon = RADIUS / kx;
const bbox = `${(lat - dLat).toFixed(6)},${(lon - dLon).toFixed(6)},${(lat + dLat).toFixed(6)},${(lon + dLon).toFixed(6)}`;
const q = `[out:json][timeout:180];
(
  way(${bbox})["building"];
  way(${bbox})["highway"];
  way(${bbox})["leisure"~"^(park|pitch|track|garden)$"];
  way(${bbox})["natural"~"^(water|wood)$"];
);
out geom;`;
// `out geom;` already carries tags. `out geom tags;` is a SYNTAX ERROR, and
// Overpass answers it with HTTP 406 — which reads like a server fault and is
// not one. Cost an hour of blaming the mirrors; measured, not guessed.

console.log(`${loc.label} — ${RADIUS} m around ${lat.toFixed(5)}, ${lon.toFixed(5)}`);
const data = await overpass(`${key}_r${RADIUS}`, q);

// ── metres per storey, for buildings that give levels but not height ──
const LEVEL_M = 3.2;
const heightOf = (t) => {
  const h = parseFloat(t['height'] || t['building:height']);
  if (Number.isFinite(h)) return h;
  const lv = parseFloat(t['building:levels'] || t['levels']);
  if (Number.isFinite(lv)) return lv * LEVEL_M;
  return null;                                        // unknown — leave it null, do not invent
};

const buildings = [], roads = [], areas = [];
for (const el of data.elements || []) {
  if (!el.geometry || el.geometry.length < 2) continue;
  const t = el.tags || {};
  const pts = el.geometry.map(toXY);
  // drop anything entirely outside the radius
  if (!pts.some(([x, y]) => Math.hypot(x, y) <= RADIUS)) continue;

  if (t.building) {
    buildings.push({ id: el.id, pts, h: heightOf(t), kind: t.building, name: t.name || undefined });
  } else if (t.highway) {
    roads.push({ id: el.id, pts, kind: t.highway, name: t.name || undefined,
                 lanes: t.lanes ? Number(t.lanes) : undefined,
                 oneway: t.oneway === 'yes' || undefined,
                 foot: (t.highway === 'footway' || t.highway === 'path') || undefined });
  } else {
    areas.push({ id: el.id, pts, kind: t.leisure || t.natural, name: t.name || undefined });
  }
}

const withH = buildings.filter((b) => b.h != null);
const world = {
  location: { key, label: loc.label, osm: loc.osm, lat, lon, radius_m: RADIUS },
  frame: { origin: 'location centre', units: 'metres', x: 'east', y: 'north' },
  attribution: 'Map data © OpenStreetMap contributors (ODbL) — https://osm.org/copyright',
  generated: new Date().toISOString().slice(0, 10),
  buildings, roads, areas,
};
const out = path.join(HERE, 'world', `${key}.json`);
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, JSON.stringify(world));

const km = (roads.reduce((s, r) => {
  let d = 0; for (let i = 1; i < r.pts.length; i++) d += Math.hypot(r.pts[i][0] - r.pts[i-1][0], r.pts[i][1] - r.pts[i-1][1]);
  return s + d;
}, 0) / 1000).toFixed(2);

console.log(`  buildings ${buildings.length} (${withH.length} with a real height, ${buildings.length - withH.length} unknown)`);
console.log(`  roads     ${roads.length} ways, ${km} km total`);
console.log(`  areas     ${areas.length} (parks, pitches, water)`);
console.log(`  -> ${path.relative(process.cwd(), out)}  ${(fs.statSync(out).size / 1024).toFixed(0)} KB`);
