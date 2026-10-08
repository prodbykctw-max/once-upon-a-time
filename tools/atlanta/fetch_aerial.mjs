// REAL AERIAL IMAGERY AS THE GROUND — public domain, commercially safe.
//
//   node tools/atlanta/fetch_aerial.mjs [key ...]
//
// Client, 10-08: "you're missing the power that you have... use images,
// pictures and photos of these locations as well. Combine those with OSM data
// and you're gonna come up with the best realistic layout."
//
// He is right, and this is the single biggest thing left. OSM gives TOPOLOGY —
// where the streets run, what the footprints are, how high the buildings are.
// It does not give APPEARANCE, and that gap is exactly what he saw in the first
// flyover: "thin lines over each other… it doesn't look finished." The roads
// had detail because OSM describes roads; the ground had none because OSM does
// not describe dirt.
//
// An aerial photo describes the dirt. Parking bays, pitch markings, worn grass,
// tree canopy, the colour concrete actually is in Georgia — none of which has
// to be invented or tuned.
//
// ── SOURCE AND LICENCE, WHICH IS THE WHOLE REASON THIS ONE ────────────────
// USGS National Map, NAIP (National Agriculture Imagery Program). It is a
// product of the US Department of Agriculture: a work of the US federal
// government, PUBLIC DOMAIN, free for commercial use with no attribution
// obligation. That matters here — this is a paid deliverable and the repo is
// public. Esri's basemap, Google and Bing imagery are all licensed in ways that
// forbid exactly this, however easy they are to fetch.
//
// Resolution measured at Cobb Stadium: 840 m across 1024 px = 0.82 m/px — the
// running track, the pitch markings and individual parking bays are all legible.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { scaleAt } from './osm.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const LOCS = JSON.parse(fs.readFileSync(path.join(HERE, 'locations.json'), 'utf8'));
const OUT = path.join(HERE, 'art', 'aerial');
fs.mkdirSync(OUT, { recursive: true });

const UA = 'jande-once-upon-a-time/1.0 (game world build; contact prodbykctw@gmail.com)';
const BASE = 'https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPImagery/ImageServer/exportImage';

const keys = process.argv.slice(2).length
  ? process.argv.slice(2)
  : Object.keys(LOCS).filter((k) => k[0] !== '_' && LOCS[k].resolved);

for (const key of keys) {
  const loc = LOCS[key];
  if (!loc || !loc.resolved) { console.log(`  ${key}: not resolved, skipping`); continue; }

  const worldFile = path.join(HERE, 'world', `${key}.json`);
  if (!fs.existsSync(worldFile)) { console.log(`  ${key}: no world file, build it first`); continue; }
  const world = JSON.parse(fs.readFileSync(worldFile, 'utf8'));
  const E = world.elevation;

  // COVER THE WHOLE TERRAIN MESH, not just the extract radius. The ground is
  // meshed out to span * EXT with EXT = 2.2, so an image sized to the radius
  // would leave the outer ring bare — and the outer ring is most of what a
  // drone shot actually sees.
  const span = E.step * (E.grid - 1) * 2.2;
  const half = span / 2;
  const { kx, ky } = scaleAt(loc.lat);
  const dLat = half / ky, dLon = half / kx;

  // 2048 is the practical ceiling: the service caps a request and anything
  // larger costs memory on a phone for detail below one pixel per metre.
  const PX = 2048;
  const url = `${BASE}?bbox=${loc.lon - dLon},${loc.lat - dLat},${loc.lon + dLon},${loc.lat + dLat}`
            + `&bboxSR=4326&size=${PX},${PX}&format=jpgpng&f=image`;

  const dest = path.join(OUT, `${key}.jpg`);
  if (fs.existsSync(dest) && !process.env.FORCE) {
    console.log(`  ${key}: already fetched (FORCE=1 to refetch)`);
    continue;
  }
  try {
    const res = await fetch(url, { headers: { 'User-Agent': UA } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const buf = Buffer.from(await res.arrayBuffer());
    if (buf.length < 8000) throw new Error(`suspiciously small (${buf.length} B) — probably an error tile`);
    fs.writeFileSync(dest, buf);
    // The georeference has to travel WITH the image or nothing downstream can
    // place it: the terrain samples this by world metres, not by pixel.
    fs.writeFileSync(path.join(OUT, `${key}.json`), JSON.stringify({
      source: 'USGS NAIP (US Dept. of Agriculture) — public domain',
      key, px: PX, spanM: +span.toFixed(1),
      metresPerPixel: +(span / PX).toFixed(3),
      bbox: { minlon: loc.lon - dLon, minlat: loc.lat - dLat, maxlon: loc.lon + dLon, maxlat: loc.lat + dLat },
      // local-metre frame, same convention as world.json: origin at the centre
      x0: -half, y0: -half, x1: half, y1: half,
    }, null, 2));
    console.log(`  ${key}: ${(buf.length / 1024).toFixed(0)} KB · ${span.toFixed(0)} m across at ${PX} px = ${(span / PX).toFixed(2)} m/px`);
  } catch (e) {
    console.log(`  ${key}: FAILED — ${e.message}`);
  }
}
