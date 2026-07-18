#!/usr/bin/env python3
"""WHIMSICAL PRINCESS asset kit — 9 reimagined rooms, bright fairytale palette.
Walls 72x96 -> x2 (144x192, same cells as current game), floors 48x48 -> x2,
ambient strip (fairy/bird/sparkle) for the overlay particle system.
Rooms: Sunlit Library, Rose Courtyard, Blossom Promenade, Princess Ballroom,
Fountain Plaza, Starlight Conservatory, Swan Lake Terrace, Gallery of Dreams,
Sunset Stage (outdoor concert finale)."""
from PIL import Image
import math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets_whimsy')
os.makedirs(OUT, exist_ok=True)

def C(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
def hsh(x,y,s=0): v=math.sin(x*127.1+y*311.7+s*74.7)*43758.5453; return v-math.floor(v)
def mix(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

class T2:
    def __init__(self,w,h):
        self.w,self.h=w,h
        self.img=Image.new('RGBA',(w,h),(0,0,0,0)); self.px=self.img.load()
    def B(self,x,y,c,a=1.0):
        x,y=int(x),int(y)
        if not(0<=x<self.w and 0<=y<self.h) or a<=0: return
        r,g,b,pa=self.px[x,y]
        if pa==0: self.px[x,y]=(c[0],c[1],c[2],int(255*min(1,a))); return
        na=min(1,a); self.px[x,y]=(int(r+(c[0]-r)*na),int(g+(c[1]-g)*na),int(b+(c[2]-b)*na),255)
    def R(self,x0,y0,x1,y1,c,a=1.0):
        for y in range(int(y0),int(y1)+1):
            for x in range(int(x0),int(x1)+1): self.B(x,y,c,a)
    def VG(self,x0,y0,x1,y1,ct,cb,a=1.0):
        h=max(1,y1-y0)
        for y in range(int(y0),int(y1)+1):
            cc=mix(ct,cb,(y-y0)/h)
            for x in range(int(x0),int(x1)+1): self.B(x,y,cc,a)
    def GLOW(self,cx,cy,r,c,amax):
        for y in range(int(cy-r),int(cy+r)+1):
            for x in range(int(cx-r),int(cx+r)+1):
                d=math.hypot(x-cx,y-cy)/r
                if d<1: self.B(x,y,c,amax*(1-d)*(1-d))
    def DISC(self,cx,cy,r,c,a=1.0):
        for y in range(int(cy-r),int(cy+r)+1):
            for x in range(int(cx-r),int(cx+r)+1):
                if math.hypot(x-cx,y-cy)<=r: self.B(x,y,c,a)
    def SPARK(self,x,y,c,big=False):
        self.B(x,y,c,0.95); self.B(x-1,y,c,0.6); self.B(x+1,y,c,0.6)
        self.B(x,y-1,c,0.6); self.B(x,y+1,c,0.6)
        if big: self.B(x-2,y,c,0.3); self.B(x+2,y,c,0.3); self.B(x,y-2,c,0.3); self.B(x,y+2,c,0.3)

SKY_T=C('#8fd4ff'); SKY_B=C('#eaf7ff'); SUN=C('#fff3b0'); GOLD=C('#e8c86a')
PINK=C('#ffb7d5'); ROSE=C('#ff7fae'); MARBLE=C('#f6f1ea'); MARBLE_D=C('#d8cfc2')
LEAF=C('#7ecb7e'); LEAF_D=C('#4e9a54'); WATER=C('#9adcf0'); WATER_D=C('#5cb8dc')

def sky(t,horizon=0.62,sunx=20,suny=14,sunr=9):
    t.VG(0,0,t.w-1,int(t.h*horizon),SKY_T,SKY_B)
    t.GLOW(sunx,suny,sunr*2.6,SUN,0.55); t.DISC(sunx,suny,sunr,C('#fffbe0'),0.95)
    for k in range(3):  # puffy clouds
        cx,cy=int(hsh(k,1)*t.w),int(6+hsh(k,5)*t.h*0.3)
        for d in range(4):
            t.DISC(cx+d*5-8,cy+(d%2)*2,4+int(hsh(k,d)*3),C('#ffffff'),0.85)
def birds(t,n,y0,y1,dark=0.35):
    for k in range(n):
        bx,by=int(hsh(k,21)*t.w),int(y0+hsh(k,23)*(y1-y0))
        c=mix(C('#3a4a5a'),C('#ffffff'),0)
        t.B(bx-2,by-1,c,dark); t.B(bx-1,by,c,dark); t.B(bx,by,c,dark)
        t.B(bx+1,by,c,dark); t.B(bx+2,by-1,c,dark)
def sparkles(t,n,seed=0):
    for k in range(n):
        t.SPARK(int(hsh(k,seed+31)*t.w),int(hsh(k,seed+37)*t.h),
                C('#ffffff') if hsh(k,seed)<0.5 else C('#ffe9a8'),hsh(k,seed+41)>0.7)
def balustrade(t,y,h=14):
    t.R(0,y,t.w-1,y+2,MARBLE); t.R(0,y+h,t.w-1,y+h+2,MARBLE)
    t.R(0,y+2,t.w-1,y+2,MARBLE_D,0.7); t.R(0,y+h+2,t.w-1,y+h+2,MARBLE_D,0.7)
    for x in range(3,t.w,10):
        t.VG(x,y+3,x+4,y+h-1,MARBLE,MARBLE_D)
        t.B(x,y+3,C('#ffffff'),0.6); t.R(x+1,y+h//2+y//200,x+3,y+h//2,MARBLE_D,0.5)

WW,WH=72,96
def w_library(): # SUNLIT LIBRARY — honey wood, arched window, floating book, butterflies
    t=T2(WW,WH)
    t.VG(0,0,WW-1,WH-1,C('#e8cfa0'),C('#c9a066'))
    for ry in (26,52,78): t.R(0,ry,WW-1,ry+3,C('#a87a44')); t.R(0,ry+3,WW-1,ry+3,C('#7a5428'),0.6)
    pal=[C('#e07898'),C('#78a8e0'),C('#8ec98e'),C('#e0b060'),C('#b490dc'),C('#70c8c0')]
    for r,ry in enumerate((26,52,78)):
        x=3
        while x<WW-4:
            wd=3+int(hsh(x,r)*4); hh=12+int(hsh(x,r,7)*7)
            c=pal[(x+r*2)%len(pal)]
            t.VG(x,ry-hh,x+wd,ry-1,mix(c,(255,255,255),0.35),c)
            t.B(x,ry-hh,C('#ffffff'),0.5); x+=wd+1
    wx0,wx1,wy0,wy1=22,50,8,44   # arched sun window
    for y in range(wy0,wy1):
        arch=1 if y>wy0+9 else math.sqrt(max(0,1-((wy0+9-y)/10)**2))
        half=int(14*arch)
        if half>0:
            for x in range(36-half,36+half+1):
                yy=(y-wy0)/(wy1-wy0)
                t.B(x,y,mix(SKY_T,C('#fffbe0'),max(0,1-yy*1.4)),1)
            t.B(36-half,y,C('#a87a44'),0.9); t.B(36+half,y,C('#a87a44'),0.9)
    t.GLOW(36,wy0+12,20,SUN,0.5)
    for a in range(5):  # sun rays into the room
        t.R(30+a*3,wy1,31+a*3,wy1+18+a*3,SUN,0.18)
    t.R(24,60,32,66,C('#c04a6a'))  # floating open book
    t.R(24,60,32,60,C('#ffffff'),0.8); t.B(28,59,C('#ffffff'),0.9)
    for k in range(3):  # butterflies
        bx,by=int(12+hsh(k,3)*48),int(50+hsh(k,9)*30)
        t.B(bx-1,by-1,ROSE,0.9); t.B(bx+1,by-1,ROSE,0.9); t.B(bx,by,C('#7a3050'),0.9)
    sparkles(t,8,1)
    return t
def w_rose(): # ROSE GARDEN COURTYARD — outdoor: sky, hedge, roses, doves
    t=T2(WW,WH)
    sky(t,0.5,16,12,8)
    t.VG(0,44,WW-1,WH-1,LEAF,LEAF_D)  # hedge
    for y in range(44,WH,3):
        for x in range(0,WW,3):
            if hsh(x,y,2)<0.4: t.B(x,y,mix(LEAF,(0,0,0),0.25),0.6)
            if hsh(x,y,3)<0.18: t.B(x,y,mix(LEAF,(255,255,255),0.3),0.6)
    for k in range(9):  # roses
        rx,ry=int(3+hsh(k,11)*(WW-6)),int(48+hsh(k,13)*(WH-56))
        t.DISC(rx,ry,2,ROSE); t.B(rx,ry,mix(ROSE,(255,255,255),0.5)); t.DISC(rx,ry+3,1,LEAF_D,0.7)
    balustrade(t,36,12)
    birds(t,3,4,26)
    sparkles(t,6,2)
    return t
def w_blossom(): # CHERRY BLOSSOM PROMENADE — canopy, red bridge rail, petals
    t=T2(WW,WH)
    sky(t,0.55,54,10,7)
    for k in range(26):  # blossom canopy
        bx,by=int(hsh(k,5)*WW),int(hsh(k,7)*30)
        t.DISC(bx,by,3+int(hsh(k,9)*3),PINK,0.9)
        t.B(bx,by,mix(PINK,(255,255,255),0.5),0.9)
    t.R(30,6,33,34,C('#6a4a34'))  # branch
    t.R(20,16,23,30,C('#6a4a34'),0.8)
    t.R(0,58,WW-1,61,C('#d8384a'))  # red bridge rails
    t.R(0,74,WW-1,76,C('#d8384a'))
    for x in range(4,WW,12): t.VG(x,61,x+3,74,C('#e04a5c'),C('#a82434'))
    for k in range(12):  # falling petals
        px,py=int(hsh(k,15)*WW),int(30+hsh(k,17)*60)
        t.B(px,py,PINK,0.9); t.B(px+1,py,mix(PINK,(255,255,255),0.4),0.7)
    return t
def w_ballroom(): # PRINCESS BALLROOM — pastel panels, gold mirrors, chandelier
    t=T2(WW,WH)
    t.VG(0,0,WW-1,WH-1,C('#fbe8f2'),C('#eccade'))
    for px0 in (4,40):  # gold-framed mirrors
        t.VG(px0-2,14,px0+26,64,GOLD,C('#b08c28'))
        t.VG(px0,16,px0+24,62,C('#dff2fa'),C('#a8cede'))
        for d in range(10): t.B(px0+4+d,20+d*2,C('#ffffff'),0.5)
        t.B(px0-2,14,C('#fff6d0'),0.9); t.B(px0+26,14,C('#fff6d0'),0.9)
    t.R(0,70,WW-1,73,GOLD); t.R(0,73,WW-1,73,C('#8a6a18'),0.6)  # gold chair rail
    cx=36  # crystal chandelier
    t.R(cx-1,0,cx,6,C('#c8b060'))
    t.GLOW(cx,12,12,C('#fff6d0'),0.7)
    for a in range(-2,3):
        t.VG(cx+a*6-1,8,cx+a*6,14+abs(a),C('#f4ecd0'),C('#d0e8f0'))
        t.SPARK(cx+a*6,16+abs(a),C('#ffffff'))
    sparkles(t,10,4)
    return t
def w_fountain(): # FOUNTAIN PLAZA — tiered marble fountain, rainbow spray, statue
    t=T2(WW,WH)
    sky(t,0.5,58,10,7)
    cx=26
    t.VG(cx-20,78,cx+20,88,MARBLE,MARBLE_D)      # basin
    t.R(cx-20,78,cx+20,79,C('#ffffff'),0.7)
    t.VG(cx-12,62,cx+12,70,MARBLE,MARBLE_D)      # mid tier
    t.VG(cx-5,48,cx+5,54,MARBLE,MARBLE_D)        # top tier
    t.VG(cx-1,40,cx+1,48,WATER,WATER_D)          # jet
    t.GLOW(cx,40,5,C('#ffffff'),0.7)
    for k in range(10):  # falling water arcs
        a=k/9*math.pi
        ax,ay=cx+math.cos(a)*10,54+abs(math.sin(a))*8
        t.B(ax,ay,WATER,0.85); t.B(ax,ay+6,WATER_D,0.6); t.B(ax,ay+14,WATER,0.5)
    for k in range(6):  # rainbow in the mist
        rc=[C('#ff9a9a'),C('#ffd29a'),C('#fff69a'),C('#b8f0a8'),C('#a8d8f8'),C('#d0b8f8')][k]
        for x in range(-14,15):
            y=int(70-math.sqrt(max(0,196-x*x))*0.5)-k
            t.B(cx+x+24,y+8,rc,0.35)
    t.VG(58,54,66,86,MARBLE,MARBLE_D)  # statue on plinth
    t.DISC(62,50,4,MARBLE); t.R(60,54,64,66,MARBLE)
    t.R(58,84,66,88,MARBLE_D)
    t.B(60,49,C('#ffffff'),0.6)
    birds(t,3,6,30)
    return t
def w_conservatory(): # STARLIGHT CONSERVATORY — glass panes, glow flowers, fireflies
    t=T2(WW,WH)
    t.VG(0,0,WW-1,WH-1,C('#2a3a6a'),C('#4a5a9a'))  # evening glass
    for x in range(0,WW,18): t.R(x,0,x+1,WH-1,C('#e8e2d0'),0.9)
    for y in range(0,WH,24): t.R(0,y,WW-1,y+1,C('#e8e2d0'),0.9)
    for k in range(20):  # stars through glass
        t.B(int(hsh(k,1)*WW),int(hsh(k,3)*WH*0.5),C('#ffffff'),0.4+hsh(k,5)*0.5)
    for k in range(4):  # hanging glow flowers
        fx=10+k*17; fl=28+int(hsh(k,7)*20)
        t.R(fx,0,fx,fl,C('#8a9a6a'),0.8)
        t.GLOW(fx,fl+4,7,C('#ffd6f0'),0.8)
        t.DISC(fx,fl+4,3,ROSE,0.95); t.B(fx,fl+4,C('#fff0f8'))
    for k in range(8):  # fireflies
        t.SPARK(int(hsh(k,11)*WW),int(40+hsh(k,13)*50),C('#d8ffa0'),hsh(k,15)>0.6)
    return t
def w_swan(): # SWAN LAKE TERRACE — water, swans, willow
    t=T2(WW,WH)
    sky(t,0.42,14,10,7)
    t.VG(0,40,WW-1,WH-1,WATER,WATER_D)  # lake
    for y in range(42,WH,4):
        for x in range(0,WW,5):
            if hsh(x,y,9)<0.3: t.R(x,y,x+2,y,C('#ffffff'),0.25)
    t.GLOW(16,46,12,C('#fffbe0'),0.35)  # sun glitter path
    for k in range(2):  # swans
        sx,sy=16+k*34,56+k*14
        t.DISC(sx,sy,4,C('#ffffff')); t.DISC(sx+3,sy-1,3,C('#ffffff'))
        t.R(sx+5,sy-6,sx+5,sy-2,C('#ffffff'))  # neck
        t.B(sx+6,sy-7,C('#f0a030')); t.B(sx+5,sy-7,C('#202020'),0.8)
        t.R(sx-4,sy+4,sx+7,sy+4,WATER_D,0.5)   # ripple
    for x in range(0,WW,2):  # willow strands
        if hsh(x,1)<0.6:
            ln=10+int(hsh(x,3)*22)
            t.R(x,0,x,ln,LEAF_D,0.75); t.B(x,ln,LEAF,0.9)
    balustrade(t,84,8)
    return t
def w_gallery(): # GALLERY OF DREAMS — pastel walls, cloud paintings, sun medallion
    t=T2(WW,WH)
    t.VG(0,0,WW-1,WH-1,C('#f2ecfa'),C('#d8cfeE'.lower()))
    for (fx,fy,fw,fh,scene) in ((6,16,24,30,0),(40,20,26,34,1)):
        t.VG(fx-3,fy-3,fx+fw+3,fy+fh+3,GOLD,C('#b08c28'))
        if scene==0:  # dream sky painting
            t.VG(fx,fy,fx+fw,fy+fh,SKY_T,PINK)
            t.DISC(fx+8,fy+8,4,C('#ffffff'),0.9); t.DISC(fx+13,fy+9,3,C('#ffffff'),0.85)
            t.GLOW(fx+fw-6,fy+6,6,SUN,0.8)
        else:  # castle painting
            t.VG(fx,fy,fx+fw,fy+fh,C('#cfe8ff'),C('#f8e8f8'))
            t.R(fx+8,fy+14,fx+18,fy+fh-2,C('#e8e0f0'))
            t.R(fx+10,fy+8,fx+12,fy+14,C('#e8e0f0')); t.R(fx+14,fy+10,fx+16,fy+14,C('#e8e0f0'))
            t.B(fx+11,fy+6,ROSE); t.B(fx+15,fy+8,ROSE)
        t.SPARK(fx+2,fy+2,C('#ffffff'))
    cx=36  # gold sun medallion
    t.GLOW(cx,72,10,SUN,0.6); t.DISC(cx,72,5,GOLD)
    for a in range(8):
        an=a/8*6.283
        t.B(cx+math.cos(an)*8,72+math.sin(an)*8,GOLD,0.9)
    sparkles(t,8,6)
    return t
def w_stage(): # SUNSET STAGE — outdoor concert finale: sunset, truss, spots, confetti, crowd
    t=T2(WW,WH)
    t.VG(0,0,WW-1,54,C('#ffca7a'),C('#ff8fa8'))  # sunset sky
    t.GLOW(36,30,16,C('#fff0c0'),0.8); t.DISC(36,30,8,C('#fff6d8'),0.95)
    t.R(0,6,WW-1,8,C('#5a4a6a'),0.9)  # lighting truss
    for x in range(6,WW,16):
        t.R(x,8,x+4,12,C('#3a3048'))
        gc=[ROSE,C('#9ad8ff'),C('#ffe9a8'),C('#c8a8ff')][(x//16)%4]
        t.GLOW(x+2,14,5,gc,0.9)
        for d in range(18):  # light beams
            t.B(x+2-d//3,14+d,gc,0.25*(1-d/20)); t.B(x+2+d//3,14+d,gc,0.25*(1-d/20))
    for k in range(16):  # confetti
        t.B(int(hsh(k,3)*WW),int(hsh(k,5)*50),
            [ROSE,C('#9ad8ff'),C('#ffe9a8'),C('#b8f0a8')][k%4],0.9)
    t.VG(0,54,WW-1,70,C('#6a3a5a'),C('#3a2038'))  # crowd band
    for x in range(1,WW,4):  # crowd silhouettes + phone lights
        hh=int(hsh(x,7)*6)
        t.DISC(x,60+hh,2,C('#241426'),0.95)
        if hsh(x,9)<0.35: t.B(x,56+hh,C('#cfe8ff'),0.9)
    t.VG(0,70,WW-1,WH-1,C('#8a5a30'),C('#5a3a1c'))  # stage boards
    for y in range(70,WH,6): t.R(0,y,WW-1,y,C('#3a240f'),0.6)
    return t

WALLS=[w_library,w_rose,w_blossom,w_ballroom,w_fountain,w_conservatory,w_swan,w_gallery,w_stage]

def floor(i):
    F=48; t=T2(F,F)
    def grid(a,b,step,gc,ga):
        t.VG(0,0,F-1,F-1,a,b)
        for y in range(0,F,step): t.R(0,y,F-1,y,gc,ga)
        for x in range(0,F,step): t.R(x,0,x,F-1,gc,ga)
    if i==0: grid(C('#e0b878'),C('#c09050'),12,C('#8a6030'),0.55)          # honey parquet
    elif i==1:                                                              # garden path
        t.VG(0,0,F-1,F-1,C('#d8cbb0'),C('#b8a888'))
        for ry in range(0,F,16):
            off=8 if (ry//16)%2 else 0
            for rx in range(-off,F,16):
                t.R(rx+1,ry+1,rx+14,ry+14,C('#e2d6bc'),0.8)
                t.R(rx+1,ry+14,rx+14,ry+15,LEAF_D,0.35)
    elif i==2:                                                              # petal boards
        grid(C('#d8a8b8'),C('#b8809a'),12,C('#8a5068'),0.5)
        for k in range(10): t.B(int(hsh(k,1)*F),int(hsh(k,3)*F),PINK,0.9)
    elif i==3:                                                              # ballroom marble
        t.VG(0,0,F-1,F-1,C('#faf4ec'),C('#e2d6c8'))
        for ry in range(0,F,24):
            for rx in range(0,F,24):
                if (rx//24+ry//24)%2: t.R(rx,ry,rx+23,ry+23,C('#f0d8e4'),0.5)
        for d in range(0,F,7):
            for s2 in range(10):
                x,y=d+s2,s2*4
                if 0<=x<F and 0<=y<F: t.B(x,y,C('#ffffff'),0.25)
        t.R(0,23,F-1,24,GOLD,0.45); t.R(23,0,24,F-1,GOLD,0.45)
    elif i==4: grid(C('#e8e0d0'),C('#c8bca8'),16,(152,136,120),0.5)         # plaza cobble
    elif i==5:                                                              # conservatory glass tile
        grid(C('#dce8f2'),C('#b8cade'),12,C('#8aa0be'),0.5)
        for k in range(6): t.SPARK(int(hsh(k,5)*F),int(hsh(k,7)*F),C('#ffffff'))
    elif i==6:                                                              # terrace stone + water sheen
        grid(C('#e0dcd0'),C('#bcb8a8'),16,(148,144,130),0.5)
        for y in range(0,F,5):
            t.R(0,y,F-1,y,WATER,0.06)
    elif i==7:                                                              # dream carpet
        t.VG(0,0,F-1,F-1,C('#e0d2f0'),C('#c4b2dc'))
        for y in range(0,F,2):
            for x in range(0,F,2):
                if hsh(x,y,8)<0.3: t.B(x,y,C('#cebce6'),0.6)
        for k in range(4): t.SPARK(int(hsh(k,9)*F),int(hsh(k,11)*F),C('#ffffff'))
    else: grid(C('#b8804a'),C('#8a5a30'),8,C('#5a3a1c'),0.6)                # stage boards
    for y in range(F):  # sunny sheen
        t.R(0,y,F-1,y,C('#fff6d8'),0.10*max(0,1-y/F*1.3))
    return t

# ambient overlay strip: fairy x2, bird x2, sparkle x3, petal x1 (16x16)
def ambient():
    sheet=Image.new('RGBA',(16*8,16),(0,0,0,0))
    for f in range(2):  # fairy
        t=T2(16,16); wf=3+f*2
        t.GLOW(8,8,6,C('#fff0b0'),0.7)
        t.DISC(8,8,2,C('#ffdf80'),0.95); t.B(8,7,C('#ffffff'))
        t.B(8-wf,6,C('#e0f4ff'),0.9); t.B(8-wf+1,7,C('#e0f4ff'),0.7)
        t.B(8+wf,6,C('#e0f4ff'),0.9); t.B(8+wf-1,7,C('#e0f4ff'),0.7)
        sheet.paste(t.img,(16*f,0))
    for f in range(2):  # bird
        t=T2(16,16)
        c=C('#4a5a6a'); up=f==0
        t.B(6,8,c); t.B(7,8,c); t.B(8,8,c); t.B(9,7,c,0.9)
        t.B(5,7 if up else 9,c,0.9); t.B(4,6 if up else 10,c,0.8)
        t.B(9,7 if up else 9,c,0.9); t.B(10,6 if up else 10,c,0.8)
        sheet.paste(t.img,(32+16*f,0))
    for f in range(3):  # sparkle pulse
        t=T2(16,16)
        t.SPARK(8,8,C('#ffffff'),f>0)
        if f==2:
            t.B(6,6,C('#fff0b0'),0.5); t.B(10,10,C('#fff0b0'),0.5)
            t.B(10,6,C('#fff0b0'),0.5); t.B(6,10,C('#fff0b0'),0.5)
        sheet.paste(t.img,(64+16*f,0))
    t=T2(16,16)  # petal
    t.DISC(8,8,2,PINK,0.95); t.B(9,7,mix(PINK,(255,255,255),0.5)); t.B(7,9,ROSE,0.8)
    sheet.paste(t.img,(112,0))
    return sheet

def save(img,name,scale):
    img=img.resize((img.width*scale,img.height*scale),Image.NEAREST)
    img.save(os.path.join(OUT,name)); print(name,img.size)

walls=Image.new('RGBA',(WW*9,WH),(0,0,0,0))
for i,f in enumerate(WALLS): walls.paste(f().img,(WW*i,0))
save(walls,'walls_whimsy.png',2)
floors=Image.new('RGBA',(48*9,48),(0,0,0,0))
for i in range(9): floors.paste(floor(i).img,(48*i,0))
save(floors,'floors_whimsy.png',2)
save(ambient(),'ambient_whimsy.png',4)

pv=Image.new('RGBA',(WW*9*2,WH*2+48*2+8),(240,236,248,255))
wl=Image.open(os.path.join(OUT,'walls_whimsy.png'));fl=Image.open(os.path.join(OUT,'floors_whimsy.png'))
pv.paste(wl,(0,0),wl); pv.paste(fl,(0,WH*2+8),fl)
pv.save(os.path.join(OUT,'whimsy_preview.png')); print('preview done')
