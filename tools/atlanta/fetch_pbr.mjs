// Download the CC0 PBR sets the Atlanta world uses, from Poly Haven.
//
//   node tools/atlanta/fetch_pbr.mjs
//
// -> tools/atlanta/art/pbr/<id>/{diff,nor,rough}.jpg
//
// 1k is plenty: these tile across walls and roads seen at speed, and the
// download budget for the whole level is 8 MB compressed. Everything here is
// CC0 — no attribution required, though Poly Haven is credited anyway because
// it costs nothing to.
//
// `art/pbr/` is git-ignored: re-fetchable, and not ours to vendor.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, 'art', 'pbr');
const UA = 'jande-once-upon-a-time/1.0 (game world build; contact prodbykctw@gmail.com)';

const SETS = {
  red_brick_03:      'low-rise walls',
  concrete_wall_008: 'mid-rise walls',
  asphalt_02:        'roads',
  concrete_pavement: 'sidewalks',
  rough_concrete:    'flat roofs',
};
const MAPS = { diff: ['Diffuse', 'diffuse'], nor: ['nor_gl'], rough: ['Rough', 'rough'] };
const RES = '1k';

for (const [id, why] of Object.entries(SETS)) {
  const dir = path.join(OUT, id);
  fs.mkdirSync(dir, { recursive: true });
  let files;
  try {
    const r = await fetch(`https://api.polyhaven.com/files/${id}`, { headers: { 'User-Agent': UA } });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    files = await r.json();
  } catch (e) {
    console.log(`  ${id}: index failed — ${e.message}`);
    continue;
  }
  for (const [out, keys] of Object.entries(MAPS)) {
    const dest = path.join(dir, `${out}.jpg`);
    if (fs.existsSync(dest)) { console.log(`  ${id}/${out} cached`); continue; }
    const key = keys.find((k) => files[k]);
    const url = key && files[key][RES]?.jpg?.url;
    if (!url) { console.log(`  ${id}/${out}: no ${RES} jpg`); continue; }
    try {
      const r = await fetch(url, { headers: { 'User-Agent': UA } });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const buf = Buffer.from(await r.arrayBuffer());
      fs.writeFileSync(dest, buf);
      console.log(`  ${id}/${out}  ${(buf.length / 1024).toFixed(0)} KB   (${why})`);
    } catch (e) {
      console.log(`  ${id}/${out}: ${e.message}`);
    }
  }
}
console.log('\n  CC0 — Poly Haven (https://polyhaven.com). No attribution required; credited anyway.');
