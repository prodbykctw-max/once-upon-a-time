const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const OUT='/home/user/once-upon-a-time/presentation/stills';
// Six locations, each with three framings: an establishing hero shot, a
// street-level look, and the runner's own eye — the view the game is actually
// played from.
const LOCS=[
  ['mbs',      'Mercedes-Benz Stadium', [2.05,0.30,1.15],[1.10,0.10,0.42]],
  ['apache',   'Old Apache Kafe',       [1.60,0.26,0.95],[2.40,0.09,0.38]],
  ['dsa',      'DeKalb School of the Arts',[1.20,0.30,1.00],[0.60,0.10,0.40]],
  ['track',    'Track & Field',         [2.30,0.42,0.95],[1.70,0.11,0.40]],
  ['wade',     'Wade Walker Park',      [2.60,0.28,1.00],[0.90,0.10,0.42]],
  ['stonemtn', 'Stone Mountain Park',   [1.50,0.24,1.20],[2.10,0.10,0.45]],
];
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',
    args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  for (const [key,label,hero,street] of LOCS){
    const pg=await b.newPage({viewport:{width:1600,height:900}});
    const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
    await pg.goto(`http://localhost:8000/tools/atlanta/viewer/index.html?loc=${key}&life=1&peds=420&cars=140&giz=0`,{waitUntil:'load'});
    await pg.waitForFunction(()=>window.__preview&&window.__preview.ready,{timeout:90000}).catch(()=>{});
    await pg.waitForTimeout(4000);
    // hide the dev chrome — these are for a client, not a debug session
    await pg.addStyleTag({content:'#hud,#pick,#keys,#bar,#att,#pad,#run{display:none !important}'});
    await pg.evaluate(o=>{__preview.setMode('overview');__preview.setOrbit(o[0],o[1],o[2]);}, hero);
    await pg.waitForTimeout(1400);
    await pg.screenshot({path:`${OUT}/${key}_1_establishing.jpg`, type:'jpeg', quality:92});
    await pg.evaluate(o=>__preview.setOrbit(o[0],o[1],o[2]), street);
    await pg.waitForTimeout(1400);
    await pg.screenshot({path:`${OUT}/${key}_2_street.jpg`, type:'jpeg', quality:92});
    await pg.evaluate(()=>{__preview.run.reset(); __preview.run.s=Math.min(40,__preview.level.len*0.12); __preview.setMode('play');});
    await pg.waitForTimeout(1600);
    await pg.screenshot({path:`${OUT}/${key}_3_runner.jpg`, type:'jpeg', quality:92});
    const st=await pg.evaluate(()=>__preview.stats);
    console.log(`  ${label.padEnd(26)} ${st.level.lengthM} m / ${st.level.runSeconds}s · ${st.draws} draws · ${Math.round(st.tris).toLocaleString()} tris`, errs.length?('ERR '+errs[0]):'');
    await pg.close();
  }
  await b.close();
})().catch(e=>{console.error('FAIL',e.message);process.exit(1)});
