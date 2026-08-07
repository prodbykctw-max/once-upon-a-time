#!/usr/bin/env python3
"""2.5D asset baker — walls & floors with real lighting:
alpha-blended shadows, gradients, ambient occlusion, bevels, glows.
Walls: logical 72x96 -> x2 = 144x192 (same cell dims the game expects)
Floors: logical 48x48 -> x2 = 96x96
Every themed wall is COMPOSED from reusable components (shelf bays, books,
blocks, panes, drapes...) so they can be tweaked independently."""
from PIL import Image
import math, os
OUT = os.path.dirname(os.path.abspath(__file__))

def C(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
def hsh(x,y,s=0): v=math.sin(x*127.1+y*311.7+s*74.7)*43758.5453; return v-math.floor(v)
def mix(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

class T2:
    def __init__(self,w,h,bg=None):
        self.w,self.h=w,h
        self.img=Image.new('RGBA',(w,h),(bg[0],bg[1],bg[2],255) if bg else (0,0,0,0))
        self.px=self.img.load()
    def B(self,x,y,c,a=1.0):
        """alpha-blend color c over existing pixel"""
        x,y=int(x),int(y)
        if not(0<=x<self.w and 0<=y<self.h) or a<=0: return
        r,g,b,pa=self.px[x,y]
        if pa==0: self.px[x,y]=(c[0],c[1],c[2],int(255*min(1,a))); return
        na=min(1,a)
        self.px[x,y]=(int(r+(c[0]-r)*na),int(g+(c[1]-g)*na),int(b+(c[2]-b)*na),255)
    def R(self,x0,y0,x1,y1,c,a=1.0):
        for y in range(int(y0),int(y1)+1):
            for x in range(int(x0),int(x1)+1): self.B(x,y,c,a)
    def VG(self,x0,y0,x1,y1,ct,cb,a=1.0):
        """vertical gradient top->bottom"""
        h=max(1,y1-y0)
        for y in range(int(y0),int(y1)+1):
            cc=mix(ct,cb,(y-y0)/h)
            for x in range(int(x0),int(x1)+1): self.B(x,y,cc,a)
    def HG(self,x0,y0,x1,y1,cl,cr,a=1.0):
        w=max(1,x1-x0)
        for x in range(int(x0),int(x1)+1):
            cc=mix(cl,cr,(x-x0)/w)
            for y in range(int(y0),int(y1)+1): self.B(x,y,cc,a)
    def SH(self,x0,y0,x1,rows,amax,down=True):
        """soft cast shadow fading over rows"""
        for i in range(rows):
            a=amax*(1-i/rows)
            y=y0+i if down else y0-i
            for x in range(int(x0),int(x1)+1): self.B(x,y,(0,0,0),a)
    def GLOW(self,cx,cy,r,c,amax):
        for y in range(int(cy-r),int(cy+r)+1):
            for x in range(int(cx-r),int(cx+r)+1):
                d=math.hypot(x-cx,y-cy)/r
                if d<1: self.B(x,y,c,amax*(1-d)*(1-d))
    def BEV(self,x0,y0,x1,y1,lt,dk,al=0.55):
        """bevel: light top/left, dark bottom/right"""
        for x in range(int(x0),int(x1)+1): self.B(x,y0,lt,al); self.B(x,y1,dk,al)
        for y in range(int(y0),int(y1)+1): self.B(x0,y,lt,al*0.8); self.B(x1,y,dk,al*0.8)
    def NOISE(self,x0,y0,x1,y1,c,amt,a,s=0):
        for y in range(int(y0),int(y1)+1):
            for x in range(int(x0),int(x1)+1):
                if hsh(x,y,s)<amt: self.B(x,y,c,a)

WW,WH=72,96
# ── COMPONENT: a single book with spine shading + page top ──
def book(t,x,ybase,w,h,col,seed):
    dk=mix(col,(0,0,0),0.42); lt=mix(col,(255,255,255),0.35)
    t.HG(x,ybase-h,x+w-1,ybase-1,lt,dk)                    # rounded spine shading
    t.R(x,ybase-h,x,ybase-1,lt,0.7)                        # left rim light
    t.R(x+w-1,ybase-h,x+w-1,ybase-1,(0,0,0),0.35)          # right shade
    t.R(x,ybase-h,x+w-1,ybase-h,mix(col,(255,250,235),0.55),0.9)  # page top
    if hsh(x,seed)>0.55:                                   # spine band
        by=ybase-h+2+int(hsh(x,seed,3)*(h-6))
        t.R(x,by,x+w-1,by+1,(212,175,55),0.75)
    if hsh(x,seed,7)>0.8: t.R(x+w//2,ybase-h+1,x+w//2,ybase-2,dk,0.4) # crease

# ── COMPONENT: one shelf bay — recessed back, books, board w/ front face ──
def shelf_bay(t,x0,x1,ytop,ybot,seed,pal):
    t.VG(x0,ytop,x1,ybot,(26,15,6),(15,8,3))               # recessed back panel
    t.R(x0,ytop,x1,ytop+2,(0,0,0),0.5)                     # AO under shelf above
    t.R(x0,ytop,x0+1,ybot,(0,0,0),0.42)                    # AO left corner
    t.R(x1-1,ytop,x1,ybot,(0,0,0),0.30)                    # AO right corner
    bx=x0+2; k=0
    while bx<x1-3:
        w=2+int(hsh(bx,seed)*4); h=(ybot-ytop)-3-int(hsh(bx,seed,5)*5)
        if bx+w>x1-1: w=x1-1-bx
        if w>=2: book(t,bx,ybot,w,h,pal[(bx+seed)%len(pal)],seed)
        bx+=w+1; k+=1
        if hsh(bx,seed,9)>0.86: bx+=3                      # gap of missing books
    # shelf board: lit top face + dark front face + cast shadow downward
    t.R(x0-1,ybot,x1+1,ybot,(96,64,30))                    # top face catches light
    t.R(x0-1,ybot+1,x1+1,ybot+2,(52,32,13))                # front face
    t.R(x0-1,ybot+3,x1+1,ybot+3,(24,13,5))                 # under-edge
    t.SH(x0,ybot+4,x1,4,0.45)                              # soft shadow below

# ── WALL 0: fully built 2.5D BOOKSHELF cabinet ──
def wall_library():
    t=T2(WW,WH)
    t.VG(0,0,WW-1,WH-1,(64,42,20),(38,23,10))              # cabinet body gradient
    # left side-return column (fake depth: darker, gradient into the room)
    t.HG(0,0,6,WH-1,(20,11,4),(58,38,18))
    t.R(6,0,7,WH-1,(120,84,44),0.5)                        # lit inner edge
    # crown molding + base plinth
    t.VG(0,0,WW-1,5,(120,84,44),(70,46,22)); t.R(0,5,WW-1,6,(30,17,7))
    t.SH(0,7,WW-1,3,0.4)
    t.VG(0,WH-8,WW-1,WH-1,(52,32,15),(24,13,5)); t.R(0,WH-8,WW-1,WH-8,(110,76,40),0.6)
    pal=[C('#8a3324'),C('#3f5f7f'),C('#7f9f4f'),C('#6f3f8f'),C('#bf8f3f'),C('#4f7f6f'),C('#9f4f4f'),C('#2f4f2f'),C('#7a6a9a')]
    bays=[(10,28),(31,49),(52,69),(72,87)]
    yb=9
    for (a,b) in [(9,29),(31,51),(53,73),(75,87)]:
        pass
    for r in range(4):
        ytop=8+r*20; ybot=ytop+17
        if ybot>WH-10: break
        shelf_bay(t,9,WW-3,ytop,ybot,r*13+3,pal)
    # global lighting: warm falloff from upper center (chandelier light)
    for y in range(WH):
        for x in range(WW):
            d=math.hypot((x-WW*0.5)/(WW*0.9),(y-8)/(WH*1.15))
            t.B(x,y,(255,200,120),0.13*max(0,1-d))
            t.B(x,y,(0,0,0),0.22*max(0,(y/WH)-0.55))
    return t

def wall_egypt():
    t=T2(WW,WH); sand=C('#c9a35a')
    t.VG(0,0,WW-1,WH-1,mix(sand,(255,255,255),0.12),mix(sand,(0,0,0),0.25))
    for ry in range(0,WH,24):                              # raised block courses
        off=12 if (ry//24)%2 else 0
        for rx in range(-off,WW,24):
            t.BEV(rx+1,ry+1,min(WW-1,rx+22),min(WH-1,ry+22),(240,214,150),(90,66,26),0.5)
            t.NOISE(rx+2,ry+2,min(WW-2,rx+21),min(WH-2,ry+21),(160,124,66),0.16,0.5,rx+ry)
    # chiseled hieroglyphs: dark inset + light bottom edge (carved look)
    def carve(px,py,pts):
        for (dx,dy) in pts:
            t.B(px+dx,py+dy,(60,40,12),0.85); t.B(px+dx,py+dy+1,(255,232,170),0.35)
    for (gx,gy) in ((14,10),(38,10),(60,12),(10,36),(30,34),(54,38),(18,60),(44,60),(62,62),(26,82),(50,84)):
        g=int(hsh(gx,gy)*3)
        if g==0: carve(gx,gy,[(0,0),(0,1),(0,2),(-1,3),(1,3),(0,4),(-2,2),(2,2)])          # ankh
        elif g==1: carve(gx,gy,[(-2,1),(-1,0),(0,0),(1,0),(2,1),(-1,2),(0,2),(1,2)])       # eye
        else: carve(gx,gy,[(0,0),(1,-1),(-1,1),(-2,2),(0,2),(0,3),(1,3)])                  # bird
    # gold inlay strip w/ specular
    t.VG(0,46,WW-1,49,(212,175,55),(140,108,26)); t.R(8,46,14,46,(255,240,180),0.8)
    t.SH(0,50,WW-1,3,0.35)
    for y in range(WH):
        t.B(0,y,(0,0,0),0.3); t.B(1,y,(0,0,0),0.15)
        t.B(WW-1,y,(255,240,190),0.12)
    return t

def wall_samurai():
    t=T2(WW,WH)
    t.VG(0,0,WW-1,WH-1,(52,32,22),(24,13,8))
    for x in range(0,WW,12):                               # planks w/ grain
        t.R(x,0,x,WH-1,(12,6,3),0.8)
        t.R(x+1,0,x+1,WH-1,(90,58,38),0.35)
        for y in range(0,WH,3):
            if hsh(x,y)>0.6: t.B(x+2+int(hsh(y,x)*8),y,(70,44,28),0.5)
    # dark lacquer rail with specular streak
    t.VG(0,20,WW-1,25,(16,8,4),(5,2,1)); t.R(4,21,26,21,(150,110,70),0.4)
    # RED LANTERN component: glow + ribs + emitted light on wall
    cx,cy=50,44
    t.GLOW(cx,cy,26,(255,120,50),0.4)                      # light spills on wood
    for dy in range(-11,12):
        w=9.2*math.cos(dy/11*1.25)
        for dx in range(int(-w),int(w)+1):
            base=(226,58,40) if abs(dy)>4 else (255,120,70)
            sh=mix(base,(90,10,8),max(0,dx/w if w else 0)*0.7)   # cylindrical shading
            t.B(cx+dx,cy+dy,sh,1)
    for ry in (36,44,52): t.R(cx-8,ry,cx+8,ry,(140,20,14),0.7)
    t.R(cx-2,30,cx+2,32,(60,40,16)); t.R(cx-2,56,cx+2,58,(60,40,16))
    t.R(cx-1,59,cx+1,64,(200,40,30),0.8)
    t.GLOW(cx,cy,7,(255,230,180),0.55)                     # hot core
    # katana on stand w/ cast shadow
    t.R(10,72,11,90,(200,196,186)); t.B(10,72,(255,255,255),0.6)
    t.R(12,70,13,73,(140,108,40)); t.SH(9,91,14,3,0.5)
    t.R(6,88,17,89,(10,5,3)); t.R(6,76,17,77,(10,5,3))
    return t

def wall_royal():
    t=T2(WW,WH)
    # velvet drapes: smooth sinusoidal folds (multi-stop gradient)
    for x in range(WW):
        ph=(math.sin(x*0.42)+1)/2
        col=mix(C('#240c3e'),C('#5a1e86'),ph)
        for y in range(WH):
            fade=1-0.35*(y/WH)
            t.B(x,y,mix(col,(0,0,0),1-fade),1)
        if ph>0.86:
            for y in range(0,WH,1): t.B(x,y,(200,150,255),0.10)  # fold highlight
    t.VG(0,0,WW-1,4,(212,175,55),(140,108,26))             # gold pelmet
    t.SH(0,5,WW-1,4,0.5)
    # STAINED-GLASS WINDOW component: stone surround, glowing panes, sill
    cx=36; wx0,wx1,wy0,wy1=cx-16,cx+16,14,70
    t.R(wx0-3,wy0-3,wx1+3,wy1+2,(70,58,78))                # stone surround
    t.BEV(wx0-3,wy0-3,wx1+3,wy1+2,(140,124,150),(30,24,36),0.6)
    panes=[C('#c04060'),C('#4060c0'),C('#40a060'),C('#c0a040')]
    for y in range(wy0,wy1):
        arch=1 if y>wy0+10 else math.sqrt(max(0,1-((wy0+10-y)/12)**2))
        half=int(15*arch)
        for x in range(cx-half,cx+half+1):
            seg=((x-cx+16)//8+(y-wy0)//14)%4
            gl=panes[seg]
            lum=0.75+0.5*max(0,1-math.hypot((x-cx)/18,(y-40)/30))   # inner glow
            t.B(x,y,mix(gl,(255,255,255),min(0.45,lum-0.75)),1)
        if half>0: t.B(cx-half,y,(20,14,26),0.9); t.B(cx+half,y,(20,14,26),0.9)
    for y in range(wy0,wy1,14): t.R(cx-15,y,cx+15,y,(20,14,26),0.85)   # lead lines
    t.R(cx,wy0,cx,wy1-1,(20,14,26),0.85)
    t.GLOW(cx,42,26,(180,140,255),0.20)                    # light cast into room
    t.VG(wx0-4,wy1+3,wx1+4,wy1+6,(150,132,160),(50,42,60)) # sill
    t.SH(wx0-2,wy1+7,wx1+2,5,0.5)
    return t

def wall_museum():
    t=T2(WW,WH); mar=C('#c8c8c2')
    t.VG(0,0,WW-1,WH-1,mix(mar,(255,255,255),0.2),mix(mar,(0,0,0),0.22))
    for ry in range(0,WH,24):                              # beveled marble blocks
        off=12 if (ry//24)%2 else 0
        for rx in range(-off,WW,24):
            t.BEV(rx+1,ry+1,min(WW-1,rx+22),min(WH-1,ry+22),(255,255,252),(120,120,116),0.4)
    for k in range(14):                                    # marble veins
        vx,vy=int(hsh(k,1)*WW),int(hsh(k,2)*WH)
        for s in range(10):
            t.B(vx+s,vy+int(math.sin(s*0.8+k)*2),(255,255,255),0.25)
    # DISPLAY CASE component: glass w/ diagonal specular, artifact, shadow
    cx0,cy0,cx1,cy1=22,26,50,72
    t.R(cx0-2,cy1+1,cx1+2,cy1+6,(90,90,86))                # pedestal
    t.BEV(cx0-2,cy1+1,cx1+2,cy1+6,(180,180,176),(40,40,38),0.5)
    t.SH(cx0-2,cy1+7,cx1+2,4,0.4)
    t.VG(cx0,cy0,cx1,cy1,(150,190,200),(90,120,132),0.55)  # glass
    t.VG(cx0+9,cy0+16,cx1-9,cy1-4,(212,175,55),(120,92,20))# gold artifact
    t.BEV(cx0+9,cy0+16,cx1-9,cy1-4,(255,240,180),(80,60,10),0.6)
    for d in range(-30,60,14):                             # diagonal glass specular
        for s in range(22):
            x=cx0+d+s; y=cy0+s*2
            if cx0<x<cx1 and cy0<y<cy1: t.B(x,y,(255,255,255),0.18)
    t.BEV(cx0,cy0,cx1,cy1,(240,250,252),(60,80,88),0.7)
    return t

def wall_tech():
    t=T2(WW,WH)
    t.VG(0,0,WW-1,WH-1,(22,26,40),(8,10,18))
    for ry in range(0,WH,24):                              # beveled panels
        for rx in range(0,WW,18):
            t.BEV(rx+1,ry+1,min(WW-1,rx+16),min(WH-1,ry+22),(48,56,84),(2,3,6),0.5)
    pts=[(6,10),(30,10),(30,34),(58,34),(58,66),(18,66),(18,84),(46,84)]
    for k in range(len(pts)-1):                            # glowing traces w/ bloom
        (x0,y0),(x1,y1)=pts[k],pts[k+1]
        if x0==x1:
            for y in range(min(y0,y1),max(y0,y1)+1):
                t.B(x0,y,(30,220,240),0.95); t.B(x0-1,y,(30,220,240),0.3); t.B(x0+1,y,(30,220,240),0.3)
        else:
            for x in range(min(x0,x1),max(x0,x1)+1):
                t.B(x,y0,(30,220,240),0.95); t.B(x,y0-1,(30,220,240),0.3); t.B(x,y0+1,(30,220,240),0.3)
    for (px,py) in pts:
        t.GLOW(px,py,5,(140,255,255),0.8); t.B(px,py,(255,255,255),1)
    for y in range(0,WH,2):                                # scanlines
        t.R(0,y,WW-1,y,(0,0,0),0.10)
    t.GLOW(58,14,8,(51,255,136),0.5); t.B(58,14,(200,255,220),1)   # status LED
    return t

def wall_armory():
    t=T2(WW,WH)
    t.VG(0,0,WW-1,WH-1,(102,102,100),(48,48,46))
    for ry in range(0,WH,18):                              # rough beveled stone
        off=9 if (ry//18)%2 else 0
        for rx in range(-off,WW,19):
            t.BEV(rx+1,ry+1,min(WW-1,rx+17),min(WH-1,ry+16),(160,160,156),(24,24,22),0.5)
            t.NOISE(rx+2,ry+2,min(WW-2,rx+16),min(WH-2,ry+15),(70,70,68),0.2,0.5,rx*3+ry)
    # TORCH component: bracket, flame w/ layered glow lighting the stone
    tx,ty=56,30
    t.GLOW(tx,ty,30,(255,150,50),0.42)
    t.GLOW(tx,ty,14,(255,200,90),0.5)
    t.R(tx-1,ty+6,tx+1,ty+20,(60,38,14)); t.B(tx-1,ty+6,(140,100,50),0.6)
    t.VG(tx-3,ty-6,tx+3,ty+4,(255,220,120),(255,110,20))
    t.VG(tx-1,ty-9,tx+1,ty-4,(255,250,200),(255,190,80))
    # CREST SHIELD component: curved shading + gold cross
    sx,sy=22,52
    for dy in range(-11,13):
        w=9 if dy<4 else 9-int((dy-3)*1.2)
        if w<=0: continue
        for dx in range(-w,w+1):
            base=(150,42,32) if dy<4 else (110,26,20)
            t.B(sx+dx,sy+dy,mix(base,(255,160,120),max(0,0.45-abs(dx+3)/w*0.45)),1)
    t.R(sx-1,sy-11,sx+1,sy+12,(212,175,55)); t.R(sx-9,sy-2,sx+9,sy,(212,175,55))
    t.B(sx-8,sy-2,(255,240,180),0.7)
    t.SH(sx-9,sy+14,sx+9,4,0.45)
    return t

def wall_gallery():
    t=T2(WW,WH)
    t.VG(0,0,WW-1,WH-1,(232,224,204),(190,180,158))
    t.VG(0,12,WW-1,14,(168,152,104),(120,108,70)); t.SH(0,15,WW-1,3,0.3)  # picture rail
    t.VG(0,WH-14,WW-1,WH-1,(150,138,110),(96,88,66))       # wainscot
    t.R(0,WH-14,WW-1,WH-14,(230,220,190),0.7)
    # FRAMED PAINTING component ×2: gilt bevel frame, canvas, spotlight
    def painting(fx,fy,fw,fh,base,hi,seed):
        t.GLOW(fx+fw//2,fy-4,fw,(255,250,220),0.22)        # spotlight pool
        t.SH(fx-2,fy+fh+3,fx+fw+2,4,0.4)                   # wall shadow under frame
        t.VG(fx-3,fy-3,fx+fw+3,fy+fh+3,(230,190,90),(120,90,26))  # gilt
        t.BEV(fx-3,fy-3,fx+fw+3,fy+fh+3,(255,240,180),(80,60,14),0.8)
        t.VG(fx,fy,fx+fw,fy+fh,base,mix(base,(0,0,0),0.5))
        t.R(fx,fy,fx+fw,fy+1,(0,0,0),0.35)                 # canvas inner shadow
        for yy in range(fy,fy+fh):
            for xx in range(fx,fx+fw):
                if hsh(xx,yy,seed)<0.15: t.B(xx,yy,hi,0.5)
        t.GLOW(fx+fw//2,fy+fh//2,fw//2,hi,0.2)
    painting(8,24,22,30,C('#3a5a8a'),C('#9ac2f4'),3)
    painting(40,20,24,38,C('#7a3a52'),C('#e89ab8'),8)
    return t

def wall_vault():
    t=T2(WW,WH)
    t.VG(0,0,WW-1,WH-1,(34,24,50),(12,8,20))
    t.NOISE(0,0,WW-1,WH-1,(52,38,74),0.2,0.6,10); t.NOISE(0,0,WW-1,WH-1,(6,4,12),0.2,0.6,11)
    # GEM CLUSTER components: faceted shading + radial bloom lighting the stone
    for (gx,gy,c,cl) in ((16,20,C('#e04060'),(255,150,175)),(52,16,C('#40c0e0'),(160,235,255)),
                          (34,44,C('#a050e0'),(215,170,255)),(58,58,C('#40e080'),(165,255,200)),
                          (14,64,C('#e0c040'),(255,240,160))):
        t.GLOW(gx,gy,15,c,0.4)
        for dy in range(-4,5):
            w=4-abs(dy)//1
            for dx in range(-w,w+1):
                t.B(gx+dx,gy+dy,mix(c,(255,255,255),max(0,0.5-(dx+2)/8)),1)
        t.B(gx-1,gy-2,cl,0.9); t.B(gx,gy-3,cl,0.8)
    # gold hoard with specular sparkle
    for x in range(2,WW-2,3):
        h=5+int(hsh(x,1)*10)
        t.VG(x,WH-1-h,x+2,WH-1,(230,180,70),(120,86,20))
        t.B(x+1,WH-1-h,(255,245,190),0.9)
        if hsh(x,9)>0.75: t.B(x+1,WH-3-int(hsh(x,4)*6),(255,255,220),0.9)
    t.SH(0,WH-18,WW-1,5,0.3,False)
    return t

WALLS=[wall_library,wall_egypt,wall_samurai,wall_royal,wall_museum,wall_tech,wall_armory,wall_gallery,wall_vault]

# ── FLOORS 48x48 logical: beveled tiles + AO grout + sheen ──
def floor(i):
    F=48; t=T2(F,F)
    base=[((90,58,28),(58,36,16)),(C('#c9a35a'),C('#8a6a30')),((58,36,26),(34,20,14)),
          ((122,26,44),(70,14,26)),((196,196,190),(150,150,144)),((22,26,40),(10,12,20)),
          ((88,88,86),(56,56,54)),((110,74,42),(74,48,26)),((40,28,56),(18,12,30))][i]
    t.VG(0,0,F-1,F-1,base[0],base[1])
    def cell(x0,y0,x1,y1,s):
        t.BEV(x0,y0,x1,y1,mix(base[0],(255,255,255),0.3),mix(base[1],(0,0,0),0.4),0.45)
        t.NOISE(x0+1,y0+1,x1-1,y1-1,mix(base[1],(0,0,0),0.25),0.14,0.5,s)
        t.NOISE(x0+1,y0+1,x1-1,y1-1,mix(base[0],(255,255,255),0.18),0.10,0.5,s+5)
    if i in (0,2,7):
        for y in range(0,F,12):
            cell(0,y,F-1,y+11,y)
            t.R(0,y,F-1,y,(0,0,0),0.4)
        for y in range(0,F,12):
            sx=12 if (y//12)%2 else 30
            t.R(sx,y,sx,y+11,(0,0,0),0.35)
    elif i in (1,4,6):
        for ry in range(0,F,24):
            off=12 if (ry//24)%2 else 0
            for rx in range(-off,F,24): cell(rx+1,ry+1,rx+22,ry+22,rx+ry)
        if i==4:
            for d in range(0,F,9):                          # marble sheen diagonal
                for s2 in range(14):
                    x,y=d+s2,s2*3
                    if 0<=x<F and 0<=y<F: t.B(x,y,(255,255,255),0.10)
    elif i==3:
        t.R(0,3,F-1,4,C('#d4af37'),0.9); t.R(0,43,F-1,44,C('#d4af37'),0.9)
        t.NOISE(0,6,F-1,42,(160,40,60),0.3,0.4,3)           # carpet pile
        for y in range(10,42,10):
            for x in range(4,44,10): t.B(x,y,C('#d4af37'),0.7)
        t.SH(0,0,F-1,4,0.25)
    elif i==5:
        for y in range(0,F,12): t.R(0,y,F-1,y,(30,220,240),0.5)
        for x in range(0,F,12): t.R(x,0,x,F-1,(30,220,240),0.5)
        for y in range(0,F,12):
            for x in range(0,F,12): t.GLOW(x,y,3,(140,255,255),0.4)
    else:
        for k in range(16):
            x,y=int(hsh(k,3)*F),int(hsh(k,9)*F)
            t.B(x,y,(230,180,70),0.9); t.B(x+1,y,(255,245,190),0.5)
    # global directional sheen (light from vanishing point)
    for y in range(F):
        t.R(0,y,F-1,y,(255,240,210),0.06*max(0,1-y/F*1.4))
    return t

def sheet(tiles,cellw,cellh,scale,name):
    out=Image.new('RGBA',(cellw*len(tiles)*scale,cellh*scale),(0,0,0,0))
    for k,tl in enumerate(tiles):
        out.paste(tl.img.resize((cellw*scale,cellh*scale),Image.NEAREST),(k*cellw*scale,0))
    out.save(os.path.join(OUT,name)); print(name,out.size)

walls=[w() for w in WALLS]
sheet(walls,WW,WH,2,'walls2.png')
floors=[floor(i) for i in range(9)]
sheet(floors,48,48,2,'floors2.png')

pv=Image.new('RGBA',(WW*9*2,WH*2+48*2+8),(16,8,26,255))
for k,wl in enumerate(walls): pv.paste(wl.img.resize((WW*2,WH*2),Image.NEAREST),(k*WW*2,0))
for k,fl in enumerate(floors): pv.paste(fl.img.resize((48*2,48*2),Image.NEAREST),(k*WW*2,WH*2+8))
pv.save(os.path.join(OUT,'preview25.png')); print('done')
