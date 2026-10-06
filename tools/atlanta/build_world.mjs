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
  // stadium and sports_centre matter as much as track here: the DSA track
  // resolved to Napoleon B. Cobb Stadium, which OSM tags leisure=stadium with
  // sport=running;american_football. Without them the location's whole reason
  // for existing -- the running surface -- is absent from the extract and the
  // level gets built on blank ground.
  // (No backticks in this comment: it lives inside a JS template literal, and
  // a backtick here terminates the query string mid-sentence.)
  way(${bbox})["leisure"~"^(park|pitch|track|garden|playground|stadium|sports_centre)$"];
  // bare_rock matters: it is what Stone Mountain's dome actually IS, and
  // without it the landmark renders as a dirt mound.
  way(${bbox})["natural"~"^(water|wood|bare_rock|scrub|grassland|sand)$"];
  // URBAN LAND USE, not just the green stuff. The old filter pulled grass,
  // forest, meadow, recreation_ground and cemetery only — so around
  // Mercedes-Benz Stadium it discarded SIXTEEN PARKING LOTS plus residential,
  // retail, commercial, construction and brownfield. Those are the big
  // polygons that break up open ground, and without them the world renders as
  // one flat tan plane with thin road ribbons drawn on it. Client, on the
  // flyover: "thin lines over each other... it doesn't look finished."
  way(${bbox})["landuse"~"^(grass|forest|meadow|recreation_ground|cemetery|residential|retail|commercial|industrial|construction|brownfield|railway|farmland|military|quarry)$"];
  way(${bbox})["amenity"~"^(parking|school|university|hospital|place_of_worship)$"];
  // Pedestrian plazas mapped as areas rather than lines.
  way(${bbox})["area:highway"];
  way(${bbox})["man_made"="bridge"];
  // STREET FURNITURE. OSM carries this as nodes and it is free — around the
  // stadium alone: 102 trees, 9 traffic signals, bollards, hydrants, bus stops,
  // flagpoles, a billboard. It is the difference between a massing model and a
  // place, and none of it needs buying or modelling from scratch.
  node(${bbox})["natural"="tree"];
  node(${bbox})["highway"~"^(street_lamp|traffic_signals|bus_stop|stop|give_way)$"];
  node(${bbox})["amenity"~"^(bench|waste_basket|bicycle_parking|drinking_water|fountain|taxi)$"];
  node(${bbox})["barrier"~"^(bollard|gate|lift_gate)$"];
  node(${bbox})["emergency"="fire_hydrant"];
  node(${bbox})["man_made"~"^(flagpole|mast|water_tower)$"];
  node(${bbox})["advertising"="billboard"];
  node(${bbox})["tourism"="artwork"];
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

const buildings = [], roads = [], areas = [], props = [];
const PROP_KEYS = ['natural', 'highway', 'amenity', 'barrier', 'emergency', 'man_made',
                   'advertising', 'tourism'];
for (const el of data.elements || []) {
  // ── point props ──
  if (el.type === 'node') {
    const t = el.tags || {};
    let kind = null;
    for (const k of PROP_KEYS) if (t[k]) { kind = t[k]; break; }
    if (!kind) continue;
    const [x, y] = toXY(el);
    if (Math.hypot(x, y) > RADIUS) continue;
    props.push({ k: kind, p: [x, y] });
    continue;
  }
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
    areas.push({ id: el.id, pts,
                 kind: t.leisure || t.natural || t.landuse
                       || (t.amenity ? 'amenity_' + t.amenity : null)
                       || (t['area:highway'] ? 'plaza' : null)
                       || (t.man_made === 'bridge' ? 'bridge' : null),
                 name: t.name || undefined });
  }
}

// ── ELEVATION GRID (Open-Meteo, Copernicus DEM) ─────────────────────────────
// The flat plate had to go. Three probe points across Stone Mountain came back
// 510 m, 379 m and 290 m — 220 m of real relief inside one extract — so a flat
// ground plane there is not a simplification, it deletes the landmark.
// Free, no key, ~0.75 s a call. Batched because the API takes coordinate lists,
// and cached to disk because this is the slow part of a build.
// 40x40 = 1600 points = 16 requests. Open-Meteo is free and rate-limits by the
// minute, so the grid is sized to stay polite rather than to be as dense as
// possible — 23 m spacing over a 450 m radius still resolves a mountain.
const GRID = Number(process.env.ELEV_GRID || 40);
async function elevation() {
  const file = path.join(HERE, 'cache', `${key}_elev${GRID}_r${RADIUS}.json`);
  if (fs.existsSync(file)) return JSON.parse(fs.readFileSync(file, 'utf8'));
  const pts = [];
  for (let j = 0; j < GRID; j++) {
    for (let i = 0; i < GRID; i++) {
      const fx = -RADIUS + (2 * RADIUS * i) / (GRID - 1);
      const fy = -RADIUS + (2 * RADIUS * j) / (GRID - 1);
      pts.push([lat + fy / ky, lon + fx / kx]);
    }
  }
  const z = [];
  const CH = 100;                                   // coords per request
  for (let i = 0; i < pts.length; i += CH) {
    const c = pts.slice(i, i + CH);
    const u = `https://api.open-meteo.com/v1/elevation?latitude=${c.map((p) => p[0].toFixed(6))}&longitude=${c.map((p) => p[1].toFixed(6))}`;
    let ok = false;
    for (let a = 0; a < 3 && !ok; a++) {
      try {
        const r = await fetch(u, { headers: { 'User-Agent': 'jande-once-upon-a-time/1.0 (contact prodbykctw@gmail.com)' } });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        z.push(...(await r.json()).elevation);
        ok = true;
      } catch (e) {
        if (a === 2) throw new Error(`elevation: ${e.message}`);
        // 429 here is per-MINUTE pacing, not a daily cap — it clears quickly.
        await new Promise((s2) => setTimeout(s2, /429/.test(e.message) ? 25000 : 3000));
      }
    }
    process.stdout.write(`\r  elevation ${Math.min(i + CH, pts.length)}/${pts.length}`);
    await new Promise((s2) => setTimeout(s2, 1200));   // stay under the rate limit
  }
  // Heights are relative to the CENTRE of the extract, so the frame stays local
  // metres with z=0 at the origin — same convention as x and y.
  const mid = z[Math.floor(z.length / 2)];
  const out = { grid: GRID, step: (2 * RADIUS) / (GRID - 1), x0: -RADIUS, y0: -RADIUS,
                datum_m: mid, z: z.map((v) => +(v - mid).toFixed(2)) };
  fs.writeFileSync(file, JSON.stringify(out));
  process.stdout.write('\r');
  return out;
}
const elev = await elevation();
const zs = elev.z;
const relief = Math.max(...zs) - Math.min(...zs);

const withH = buildings.filter((b) => b.h != null);
const world = {
  location: { key, label: loc.label, osm: loc.osm, lat, lon, radius_m: RADIUS },
  frame: { origin: 'location centre', units: 'metres', x: 'east', y: 'north' },
  attribution: 'Map data © OpenStreetMap contributors (ODbL) — https://osm.org/copyright',
  generated: new Date().toISOString().slice(0, 10),
  buildings, roads, areas, props, elevation: elev,
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
const pk = {};
for (const p2 of props) pk[p2.k] = (pk[p2.k] || 0) + 1;
const topProps = Object.entries(pk).sort((a, b) => b[1] - a[1]).slice(0, 6)
  .map(([k, v]) => `${k} ${v}`).join(', ');
console.log(`  props     ${props.length} (${topProps})`);
console.log(`  elevation ${elev.grid}x${elev.grid} grid, ${elev.step.toFixed(0)} m spacing, ${relief.toFixed(0)} m of relief`);
console.log(`  -> ${path.relative(process.cwd(), out)}  ${(fs.statSync(out).size / 1024).toFixed(0)} KB`);
