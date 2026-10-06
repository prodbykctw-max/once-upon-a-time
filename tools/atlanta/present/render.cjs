// One worker. Renders BOTH videos for each location named on the command line:
//
//   node tools/atlanta/present/render.cjs mbs apache
//
// WHY WORKERS, AND WHY ONLY THREE OF THEM.
// Measured on this container (4 cores, SwiftShader, no GPU):
//   1 process   4034 ms/frame        -> 0.248 frames/sec
//   3 parallel  7687 ms/frame each   -> 0.390 frames/sec combined = 1.57x
// Not 3x, because the software rasteriser ALREADY uses all four cores inside a
// single render — the parallelism is in the rasteriser, not between renders. So
// fanning out wider than ~3 buys context switching and nothing else. 1.57x on a
// 90-minute job is still half an hour, which is worth having.
const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const fs=require('fs');
const {execFileSync, execSync}=require('child_process');
const FF=execSync("python3 -c \"import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())\"").toString().trim();
const OUT='/home/user/once-upon-a-time/presentation/video';
const W=960,H=540,FPS=24;
const ease = t => t<0.5 ? 2*t*t : 1-Math.pow(-2*t+2,2)/2;
const KEYS=process.argv.slice(2);
if(!KEYS.length){ console.error('usage: render.cjs <loc> [loc...]'); process.exit(1); }

async function shoot(b, key, kind){
  const out=`${OUT}/${key}_${kind}.mp4`;
  if (fs.existsSync(out)) { console.log(`  ${key}/${kind} already rendered, skipping`); return; }
  const TMP=`/tmp/fr_${key}_${kind}`;
  fs.rmSync(TMP,{recursive:true,force:true}); fs.mkdirSync(TMP,{recursive:true});
  const N = kind==='flyover' ? FPS*15 : FPS*12;
  const pg=await b.newPage({viewport:{width:W,height:H}});
  await pg.goto(`http://localhost:8000/tools/atlanta/viewer/index.html?loc=${key}&life=1&peds=420&cars=140&giz=0`,{waitUntil:'load'});
  await pg.waitForFunction(()=>window.__preview&&window.__preview.ready,{timeout:120000}).catch(()=>{});
  await pg.waitForTimeout(4000);
  await pg.addStyleTag({content:'#hud,#pick,#keys,#bar,#att,#pad,#run{display:none !important}'});
  if (kind==='play') await pg.evaluate(()=>{ __preview.run.reset(); __preview.setMode('play'); });
  else await pg.evaluate(()=>__preview.setMode('overview'));
  const t0=Date.now();
  for(let i=0;i<N;i++){
    if (kind==='flyover'){
      const u=i/(N-1), e=ease(u);
      await pg.evaluate(a=>__preview.setOrbit(a[0],a[1],a[2]),
        [0.6+u*Math.PI*2, 0.52-e*0.33, 1.30-e*0.72]);
    } else {
      await pg.evaluate(()=>{ __preview.run.update(1/24,{});
        if(__preview.life) __preview.life.update(1/24); });
    }
    await pg.screenshot({path:`${TMP}/f${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:90});
  }
  await pg.close();
  execFileSync(FF,['-y','-framerate',String(FPS),'-i',`${TMP}/f%04d.jpg`,
    '-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',out],
    {stdio:['ignore','ignore','pipe']});
  fs.rmSync(TMP,{recursive:true,force:true});
  console.log(`  ${key}/${kind}  ${((Date.now()-t0)/60000).toFixed(1)} min -> ${(fs.statSync(out).size/1024).toFixed(0)} KB`);
}

(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',
    args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  for (const k of KEYS){ await shoot(b,k,'play'); await shoot(b,k,'flyover'); }
  await b.close();
})().catch(e=>{console.error('FAIL',e.message);process.exit(1)});
