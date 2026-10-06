const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const fs=require('fs');
const FF='/opt/pw-browsers/ffmpeg-1011/ffmpeg-linux';
const {execFileSync}=require('child_process');
const OUT='/home/user/once-upon-a-time/presentation/video';
const TMP='/tmp/flyframes';
const W=960,H=540,FPS=24,SECS=15,N=FPS*SECS;

const LOCS=[
  ['mbs','Mercedes-Benz Stadium'],['apache','Old Apache Kafe'],
  ['dsa','DeKalb School of the Arts'],['track','Track & Field'],
  ['wade','Wade Walker Park'],['stonemtn','Stone Mountain Park'],
];
// ease so the move settles rather than stopping dead
const ease = t => t<0.5 ? 2*t*t : 1-Math.pow(-2*t+2,2)/2;

(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',
    args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  for (const [key,label] of LOCS){
    fs.rmSync(TMP,{recursive:true,force:true}); fs.mkdirSync(TMP,{recursive:true});
    const pg=await b.newPage({viewport:{width:W,height:H}});
    await pg.goto(`http://localhost:8000/tools/atlanta/viewer/index.html?loc=${key}&life=1&peds=420&cars=140&giz=0`,{waitUntil:'load'});
    await pg.waitForFunction(()=>window.__preview&&window.__preview.ready,{timeout:90000}).catch(()=>{});
    await pg.waitForTimeout(4000);
    await pg.addStyleTag({content:'#hud,#pick,#keys,#bar,#att,#pad,#run{display:none !important}'});
    await pg.evaluate(()=>__preview.setMode('overview'));
    const t0=Date.now();
    for(let i=0;i<N;i++){
      const u=i/(N-1), e=ease(u);
      // ONE full revolution while descending and closing in: the "skyview that
      // zooms into a tour" the client asked for. Yaw is linear so the spin is
      // even; pitch and distance are eased so the descent settles.
      const yaw = 0.6 + u*Math.PI*2;
      const pitch = 0.88 - e*0.66;          // 0.88 overhead -> 0.22 near-ground
      const dist  = 2.00 - e*1.55;          // 2.0R -> 0.45R
      await pg.evaluate(a=>__preview.setOrbit(a[0],a[1],a[2]), [yaw,pitch,dist]);
      await pg.screenshot({path:`${TMP}/f${String(i).padStart(4,'0')}.jpg`, type:'jpeg', quality:90});
    }
    await pg.close();
    const mins=((Date.now()-t0)/60000).toFixed(1);
    execFileSync(FF,['-y','-framerate',String(FPS),'-i',`${TMP}/f%04d.jpg`,
      '-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',
      `${OUT}/${key}_flyover.mp4`],{stdio:'ignore'});
    const kb=(fs.statSync(`${OUT}/${key}_flyover.mp4`).size/1024).toFixed(0);
    console.log(`  ${label.padEnd(26)} ${N} frames in ${mins} min -> ${key}_flyover.mp4 (${kb} KB)`);
  }
  await b.close();
  fs.rmSync(TMP,{recursive:true,force:true});
})().catch(e=>{console.error('FAIL',e.message);process.exit(1)});
