const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage();
  await p.emulateMedia({ media: 'print', colorScheme: 'dark' });
  await p.goto('http://127.0.0.1:8421/index.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: '/home/user/once-upon-a-time/presentation/characters/JANDE-RPG-CAST.pdf',
    format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
