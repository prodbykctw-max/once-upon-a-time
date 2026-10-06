// PLAY-LEVEL FOOTAGE — the view the game is actually experienced from.
// A drone shot shows the world; this shows the GAME. Jandé running the real
// route, meeting the real obstacles, at the real speed.
const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const fs=require('fs');
const {execFileSync}=require('child_process');
const FF=require('child_process')
  .execSync("python3 -c \"import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())\"")
  .toString().trim();
const OUT='/home/user/once-upon-a-time/presentation/video';
const TMP='/tmp/playframes';
const W=960,H=540,FPS=24,SECS=12,N=FPS*SECS;
const LOCS=[['mbs','Mercedes-Benz Stadium'],['apache','Old Apache Kafe'],
            ['dsa','DeKalb School of the Arts'],['track','Track & Field'],
            ['wade','Wade Walker Park'],['stonemtn','Stone Mountain Park']];
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',
    args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  for (const [key,label] of LOCS){
    if (fs.existsSync(`${OUT}/${key}_play.mp4`)) { console.log(`  ${label.padEnd(26)} already rendered, skipping`); continue; }
    fs.rmSync(TMP,{recursive:true,force:true}); fs.mkdirSync(TMP,{recursive:true});
    const pg=await b.newPage({viewport:{width:W,height:H}});
    await pg.goto(`http://localhost:8000/tools/atlanta/viewer/index.html?loc=${key}&life=1&peds=420&cars=140&giz=0`,{waitUntil:'load'});
    await pg.waitForFunction(()=>window.__preview&&window.__preview.ready,{timeout:90000}).catch(()=>{});
    await pg.waitForTimeout(4000);
    await pg.addStyleTag({content:'#hud,#pick,#keys,#bar,#att,#pad,#run{display:none !important}'});
    await pg.evaluate(()=>{ __preview.run.reset(); __preview.setMode('play'); });
    const t0=Date.now();
    for(let i=0;i<N;i++){
      // Step the run by exactly one frame of game time and shoot it. Driving
      // the real update() means the real route, the real obstacles and the real
      // speed — not a camera flown along the line pretending to be gameplay.
      await pg.evaluate(()=>{ const R=__preview.run;
        R.update(1/24, {});
        if (__preview.life) __preview.life.update(1/24);
      });
      await pg.screenshot({path:`${TMP}/f${String(i).padStart(4,'0')}.jpg`, type:'jpeg', quality:90});
    }
    await pg.close();
    execFileSync(FF,['-y','-framerate',String(FPS),'-i',`${TMP}/f%04d.jpg`,
      '-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',
      `${OUT}/${key}_play.mp4`],{stdio:['ignore','ignore','pipe']});
    const kb=(fs.statSync(`${OUT}/${key}_play.mp4`).size/1024).toFixed(0);
    console.log(`  ${label.padEnd(26)} ${((Date.now()-t0)/60000).toFixed(1)} min -> ${key}_play.mp4 (${kb} KB)`);
  }
  await b.close();
  fs.rmSync(TMP,{recursive:true,force:true});
})().catch(e=>{console.error('FAIL',e.message);process.exit(1)});
