// RPG VIEW — the side-scroll camera, in the Atlanta world. One worker.
//
//   node tools/atlanta/present/rpg.cjs mbs apache
//
// Same cost model as render.cjs: ~3 workers is the useful ceiling, because the
// software rasteriser already spreads one render across all four cores.
const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const fs=require('fs');
const {execFileSync, execSync}=require('child_process');
const FF=execSync("python3 -c \"import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())\"").toString().trim();
const OUT='/home/user/once-upon-a-time/presentation/video';
fs.mkdirSync(OUT,{recursive:true});
const W=960,H=540,FPS=24,SECS=10;
const KEYS=process.argv.slice(2);
if(!KEYS.length){ console.error('usage: rpg.cjs <loc> [loc...]'); process.exit(1); }

async function shoot(b,key){
  const out=`${OUT}/${key}_rpg.mp4`;
  if (fs.existsSync(out)) { console.log(`  ${key}/rpg already rendered`); return; }
  const TMP=`/tmp/fr_${key}_rpg`;
  fs.rmSync(TMP,{recursive:true,force:true}); fs.mkdirSync(TMP,{recursive:true});
  const N=FPS*SECS;
  const pg=await b.newPage({viewport:{width:W,height:H}});
  await pg.goto(`http://localhost:8000/tools/atlanta/viewer/index.html?loc=${key}&life=1&peds=420&cars=140&giz=0`,{waitUntil:'load'});
  await pg.waitForFunction(()=>window.__preview&&window.__preview.ready,{timeout:180000}).catch(()=>{});
  await pg.waitForTimeout(4000);
  await pg.addStyleTag({content:'#hud,#pick,#keys,#bar,#att,#pad,#run{display:none !important}'});
  await pg.evaluate(()=>{ __preview.run.reset(); __preview.setMode('rpg'); });
  // Roll forward before recording so the clip opens with her already running
  // rather than standing on the start line.
  for(let i=0;i<48;i++) await pg.evaluate(()=>{ __preview.run.update(1/24,{});
    if(__preview.life) __preview.life.update(1/24); });
  const t0=Date.now();
  for(let i=0;i<N;i++){
    await pg.evaluate(()=>{ __preview.run.update(1/24,{});
      if(__preview.life) __preview.life.update(1/24); });
    await pg.screenshot({path:`${TMP}/f${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:90});
  }
  await pg.close();
  execFileSync(FF,['-y','-framerate',String(FPS),'-i',`${TMP}/f%04d.jpg`,
    '-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',out],
    {stdio:['ignore','ignore','pipe']});
  fs.rmSync(TMP,{recursive:true,force:true});
  console.log(`  ${key}/rpg  ${((Date.now()-t0)/60000).toFixed(1)} min -> ${(fs.statSync(out).size/1024).toFixed(0)} KB`);
}
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',
    args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  for (const k of KEYS) await shoot(b,k);
  await b.close();
})().catch(e=>{console.error('FAIL',e.message);process.exit(1)});
