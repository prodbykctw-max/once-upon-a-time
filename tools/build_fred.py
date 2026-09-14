#!/usr/bin/env python3
"""Build the FRÉDÉRIC EDITION as its own file, from the shipped game.

WHY THIS EXISTS. The edition is a showcase link to hand one person: every stage,
both modes, nothing that can end a run. The first version put that code inside
the public `index.html`, dormant behind a URL flag. It was provably inert — the
public title screen rendered identically — but the client's point stands: the
live game should not carry it at all.

So the public `index.html` is the ONLY source of truth and is never edited for
this. The edition is GENERATED from it, at deploy time, into `fred/index.html`.
One source, no drift: whatever ships to everyone is what Frédéric plays, plus
the patch below and nothing else.

Run by tools/deploy.sh. Output is git-ignored — it is a build artifact.
"""
import io, os, re, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
SRC  = os.path.join(REPO, 'index.html')
OUTD = os.path.join(REPO, 'fred')
OUT  = os.path.join(OUTD, 'index.html')


def burst_free_scroll():
    """The proclamation scroll, as SVG geometry.

    Drawn, never a Unicode star or emoji — the no-stock-glyphs rule applies to
    the edition too. Lettering is SVG <text> in the SAME viewBox as the scroll
    so it scales with it, and every line is pinned with textLength so it FITS on
    whatever font his phone falls back to. The first attempt sized the text with
    CSS percentages, which size against the INHERITED FONT rather than the box,
    and the words came out about 9px.
    """
    return '''  <div id="edSticker" aria-hidden="true">
    <svg viewBox="0 0 320 164" preserveAspectRatio="xMidYMid meet">
      <defs>
        <linearGradient id="edPar" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#FBEFCF"/><stop offset=".45" stop-color="#F3E0B0"/>
          <stop offset="1" stop-color="#E4C98C"/>
        </linearGradient>
        <linearGradient id="edRoll" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#F4E2B4"/><stop offset=".5" stop-color="#DCBB7C"/>
          <stop offset="1" stop-color="#B98F4E"/>
        </linearGradient>
      </defs>
      <path d="M26 30 Q160 22 294 30 L294 134 Q160 142 26 134 Z"
            fill="url(#edPar)" stroke="#9C7434" stroke-width="1.6"/>
      <rect x="8"   y="18" width="30" height="128" rx="15" fill="url(#edRoll)" stroke="#8A6428" stroke-width="1.8"/>
      <rect x="282" y="18" width="30" height="128" rx="15" fill="url(#edRoll)" stroke="#8A6428" stroke-width="1.8"/>
      <rect x="19"  y="26" width="7" height="112" rx="3.5" fill="#A87F3C" opacity=".55"/>
      <rect x="294" y="26" width="7" height="112" rx="3.5" fill="#A87F3C" opacity=".55"/>
      <text class="ed-1" x="160" y="76"  text-anchor="middle" textLength="196" lengthAdjust="spacingAndGlyphs">FRÉDÉRIC</text>
      <rect x="72" y="84" width="176" height="2.2" rx="1.1" fill="#5A3310" opacity=".45"/>
      <rect x="72" y="89" width="176" height="1.2" rx=".6"  fill="#5A3310" opacity=".3"/>
      <text class="ed-2" x="160" y="110" text-anchor="middle" textLength="150" lengthAdjust="spacingAndGlyphs">EDITION</text>
      <text class="ed-3" x="160" y="127" text-anchor="middle" textLength="150" lengthAdjust="spacingAndGlyphs">ALL STAGES — BOTH MODES</text>
    </svg>
  </div>
'''


CSS = '''
/* ── FRÉDÉRIC EDITION ───────────────────────────────────────────────────────
   A castle proclamation across the top of the title screen, glowing and
   flashing on a slow beat. Body face, not Storyboo: the wordmark is this
   screen's one display heading. Animation off under body.rm. */
#edSticker{position:absolute;top:9.5%;left:50%;width:clamp(230px,74vw,330px);aspect-ratio:320/164;
  margin-left:min(-115px,-37vw);z-index:6;pointer-events:none;transform:rotate(-4deg)}
#edSticker svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
#edSticker text{font-family:var(--body),system-ui,sans-serif;fill:#4A2410}
#edSticker .ed-1{font-weight:900;font-size:34px}
#edSticker .ed-2{font-weight:800;font-size:21px}
#edSticker .ed-3{font-weight:700;font-size:11px;opacity:.72}
@keyframes edGlow{
  0%,62%,100%{filter:drop-shadow(0 5px 12px rgba(0,0,0,.55)) drop-shadow(0 0 9px rgba(255,206,96,.55)) drop-shadow(0 0 26px rgba(255,180,60,.30));transform:rotate(-4deg) scale(1)}
  72%        {filter:drop-shadow(0 5px 12px rgba(0,0,0,.55)) drop-shadow(0 0 16px rgba(255,232,150,.95)) drop-shadow(0 0 48px rgba(255,196,74,.72));transform:rotate(-3.2deg) scale(1.035)}
  84%        {filter:drop-shadow(0 5px 12px rgba(0,0,0,.55)) drop-shadow(0 0 10px rgba(255,214,110,.6))  drop-shadow(0 0 30px rgba(255,180,60,.38));transform:rotate(-4deg) scale(1.008)}
}
#edSticker{animation:edGlow 3.6s ease-in-out infinite;
  filter:drop-shadow(0 5px 12px rgba(0,0,0,.55)) drop-shadow(0 0 9px rgba(255,206,96,.55))}
body.rm #edSticker{animation:none}
/* in-run chip: under the chapter track, clear of the HUD and well above
   CTRL_TOP, so it never lands on the touch pads */
#edHud{position:absolute;top:58px;left:50%;transform:translateX(-50%);z-index:7;
  display:flex;align-items:center;gap:8px;padding:5px 6px 5px 11px;border-radius:999px;
  background:rgba(18,6,26,.82);border:1px solid rgba(255,216,74,.55);pointer-events:auto}
#edHud .ed-lab{font-family:var(--body),system-ui,sans-serif;font-weight:800;font-size:9.5px;
  letter-spacing:.14em;color:#FFD84A;white-space:nowrap}
#edHud .ed-next{font-family:var(--body),system-ui,sans-serif;font-weight:800;font-size:9.5px;
  letter-spacing:.1em;color:#2A0E33;background:#FFD84A;border:0;border-radius:999px;
  padding:6px 12px;cursor:pointer;touch-action:manipulation}
@media (orientation:landscape) and (max-height:560px){
  #edSticker{width:clamp(190px,34vw,260px);margin-left:min(-95px,-17vw);top:5%}
  #edHud{top:44px}}
'''

# Every path that can reduce masks or end a run. Enumerated from the source, not
# guessed — all six, plus proof that nothing else reaches them.
GUARDS = [
    ("else if(p.inv===0&&GS.shieldT<=0){GS.masks--;p.inv=75;p.vy=-6;p.vx=fdx>0?-7:7;updateHUD();",
     "else if(p.inv===0&&GS.shieldT<=0&&!FRED){GS.masks--;p.inv=75;p.vy=-6;p.vx=fdx>0?-7:7;updateHUD();",
     'RPG foe contact'),
    ("""    if(BGVIEW){ // viewer: a pit lifts her back onto the floor instead of ending the look
      p.y=(FLOOR_R-3)*T; p.vy=0; return; }""",
     """    if(BGVIEW||FRED){ // viewer/showcase: a pit lifts her back out instead of ending it
      p.y=(FLOOR_R-3)*T; p.vy=0; return; }""",
     'RPG death plane'),
    ("else if(p.inv===0){GS.masks--;p.inv=75;p.vy=-6;sfx('hurt');ptcl(p.x+PW/2,p.y+30,'hurt');",
     "else if(p.inv===0&&!FRED){GS.masks--;p.inv=75;p.vy=-6;sfx('hurt');ptcl(p.x+PW/2,p.y+30,'hurt');",
     'RPG hazard'),
    ("function hurtP(p){if(p.inv>0||BGVIEW)return;",
     "function hurtP(p){if(p.inv>0||BGVIEW||FRED)return;",
     'hurtP — bosses and melee'),
    ("function stumbleT(){var t3=GS.t3,p=GS.p;\n  if(GS.shieldT>0||GS.boostT>0||p.inv>0)return;",
     "function stumbleT(){var t3=GS.t3,p=GS.p;\n  if(FRED)return;\n  if(GS.shieldT>0||GS.boostT>0||p.inv>0)return;",
     'runner stumble'),
    ("function caughtT(){var p=GS.p;sfx('death');",
     "function caughtT(){var p=GS.p;if(FRED)return;\n  sfx('death');",
     'runner caught — chaser and corners'),
]


def main():
    s = io.open(SRC, encoding='utf-8').read()
    n = 0

    def sub(old, new, label, required=True):
        nonlocal s, n
        c = s.count(old)
        if c != 1:
            print('  FAIL %-32s found %d times' % (label, c), file=sys.stderr)
            sys.exit(1)
        s = s.replace(old, new)
        n += 1
        print('  ok   %s' % label)

    # 1. the flag, FIRST — `var` hoists the declaration without the value and the
    #    guards read it from inside update(). This project has shipped that bug
    #    twice already (_amb, _rm). Hardcoded true: this file IS the edition.
    sub("<script>\n// baked pixel-art world pack",
        "<script>\nvar FRED=true;   // this build IS the Frédéric edition\n"
        "// baked pixel-art world pack",
        'FRED flag, declared first')

    # 2. nothing can end the run
    for old, new, label in GUARDS:
        sub(old, new, label)

    # 3. every stage reachable, WITHOUT writing to storage — a normal run on the
    #    same device keeps its real progress
    sub("function clearsOwned(){try{return JSON.parse(localStorage.getItem('jande_clears')||'{}');}catch(x){return{};}}",
        "function clearsOwned(){\n  if(FRED)return {0:1,1:1,2:1,3:1,4:1,5:1,6:1,7:1,8:1};\n"
        "  try{return JSON.parse(localStorage.getItem('jande_clears')||'{}');}catch(x){return{};}}",
        'all stages unlocked')

    # 4. hop stages from inside a run. The modes advance completely differently —
    #    the RPG rebuilds a level, the runner shifts theme — so dispatch rather
    #    than pretend there is one mechanism. Wraps at the last stage.
    sub("function startGame(){",
        """function fredNext(){
  try{
    if(MODE==='temple'){ themeShift(); return; }
    if(GS.ai>=STAGES.length-1){ setZoom(BASEZ); initGS(0); CHECKPOINT=0; CHECKPOINT_X=0;
      updateHUD(); showLevelCard(0,function(){}); return; }
    nextStage();
  }catch(_fn){}
}
function startGame(){""",
        'fredNext')

    # 5. the scroll + the in-run chip
    sub("""  <div class="tw-press btn-tav" id="tPress">— BEGIN —</div>
  </div>""",
        """  <div class="tw-press btn-tav" id="tPress">— BEGIN —</div>
  </div>
""" + burst_free_scroll().rstrip('\n'),
        'title scroll')

    sub(".tw-press{font-size:clamp(13px,2.2vw,17px);margin-top:36px;pointer-events:auto;padding:15px 46px}",
        ".tw-press{font-size:clamp(13px,2.2vw,17px);margin-top:36px;pointer-events:auto;padding:15px 46px}" + CSS,
        'edition CSS')

    sub("""  try{ if(/[?&]bg=1/.test(location.search)) setTimeout(bgViewer,60); }catch(_bv){}""",
        """  try{ if(/[?&]bg=1/.test(location.search)) setTimeout(bgViewer,60); }catch(_bv){}
  try{
    var bar=document.createElement('div'); bar.id='edHud';
    var lab=document.createElement('span'); lab.className='ed-lab';
    lab.textContent='FRÉDÉRIC EDITION'; bar.appendChild(lab);
    var nb=document.createElement('button'); nb.className='ed-next';
    nb.textContent='NEXT STAGE'; bar.appendChild(nb);
    nb.onclick=function(e){e.preventDefault();e.stopPropagation();fredNext();};
    document.getElementById('gameWrap').appendChild(bar);
  }catch(_fw){}""",
        'in-run chip')

    # 6. the edition lives one folder down and SHARES the published web/ assets,
    #    so it costs one HTML file rather than a second copy of every texture.
    before = len(re.findall(r'(?<![./\w])web/', s))
    s = re.sub(r'(?<![./\w])web/', '../web/', s)
    after = len(re.findall(r'\.\./web/', s))
    print('  ok   asset paths rewritten to ../web/ (%d refs)' % after)
    if before != after:
        print('  FAIL asset rewrite lost refs: %d -> %d' % (before, after), file=sys.stderr)
        sys.exit(1)

    # icons and the manifest sit at the ROOT, not under web/, so the web/ rewrite
    # above misses them and the edition 404s on /fred/icon-192.png.
    root = ['apple-touch-icon.png', 'icon-192.png', 'icon-512.png', 'manifest.webmanifest']
    for f in root:
        s = s.replace('"%s"' % f, '"../%s"' % f)
    print('  ok   root icons/manifest pointed at ../')

    os.makedirs(OUTD, exist_ok=True)
    io.open(OUT, 'w', encoding='utf-8').write(s)
    print('%d edits -> fred/index.html (%.0f KB)' % (n, len(s.encode()) / 1024))


if __name__ == '__main__':
    main()
