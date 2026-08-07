// Quick integrity check: every inline <script> parses, and the expected
// asset payloads are actually present in the built index.html.
const fs = require('fs'), vm = require('vm');
const s = fs.readFileSync(__dirname + '/../index.html', 'utf8');

const re = /<script>([\s\S]*?)<\/script>/g;
let m, i = 0, bad = 0;
while ((m = re.exec(s))) {
  i++;
  try { new vm.Script(m[1]); console.log('block', i, 'ok'); }
  catch (e) { bad++; console.log('block', i, 'SYNTAX:', e.message); }
}

const checks = {
  'GLWDATA.wall':  s.includes('wall:"data:'),
  'GLWDATA.ceil':  s.includes('ceil:"data:'),
  'TEXDATA.prince': s.includes('prince:"data:'),
  'TEXDATA.foes':  /foes:['"]data:image/.test(s),
  'obstacle sheets': s.includes('oblow:"data:') && s.includes('obgate:"data:') && s.includes('obwall:"data:'),
  'props 16-cell UV': s.includes('kind/16'),
  'library sun removed': s.includes('sun:[0.5,0.33,0.0,0.0]'),
  'library hall mode': s.includes('hall:1'),
};
for (const [k, v] of Object.entries(checks)) console.log((v ? 'OK   ' : 'FAIL ') + k);
console.log('size KB:', Math.round(s.length / 1024));
process.exit(bad || Object.values(checks).some(v => !v) ? 1 : 0);
