#!/usr/bin/env python3
"""Bake per-stage corridor decor statues/props (9 cells 48x80) and
side-mode RPG foes (imp walk x3 + flying skull x3, 34x38 cells)."""
from PIL import Image
import math, os
OUT = os.path.dirname(os.path.abspath(__file__))
def hexc(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))+(255,)
def hsh(x,y,s=0): v=math.sin(x*127.1+y*311.7+s*74.7)*43758.5453; return v-math.floor(v)

class Tile:
    def __init__(self,w,h):
        self.w,self.h=w,h
        self.img=Image.new('RGBA',(w,h),(0,0,0,0)); self.px=self.img.load()
    def P(self,x,y,c):
        x,y=int(x),int(y)
        if 0<=x<self.w and 0<=y<self.h: self.px[x,y]=hexc(c)
    def R(self,x0,y0,x1,y1,c):
        for y in range(int(y0),int(y1)+1):
            for x in range(int(x0),int(x1)+1): self.P(x,y,c)

GOLD='#d4af37'; GOLD_L='#ffe27a'; GOLD_D='#8a6a18'

def decor(i):
    t=Tile(48,80); cx=24
    if i==0:   # LIBRARY — lectern with open book + candle
        t.R(cx-3,40,cx+3,76,'#4a2e14'); t.R(cx-10,74,cx+10,79,'#3a2410')
        t.R(cx-8,44,cx+8,46,'#5a3a1c')
        t.R(cx-11,34,cx-1,40,'#f0e8d8'); t.R(cx+1,34,cx+11,40,'#e6dcc8')  # open book
        t.R(cx-11,34,cx+11,34,'#c8bca4'); t.R(cx,33,cx,41,'#8a7a5c')
        for ly in range(36,40): t.R(cx-9,ly,cx-3,ly,'#b8ac94') if ly%2 else None
        t.R(cx+14,28,cx+16,40,'#e8e0cc')                                   # candle
        fl=Tile(1,1)
        t.R(cx+14,24,cx+16,27,'#ffd23a'); t.P(cx+15,22,'#ff9a2a')
    elif i==1: # EGYPT — seated jackal statue on plinth
        t.R(6,66,42,79,'#a8863c'); t.R(8,62,40,66,'#c9a35a')
        t.R(cx-8,34,cx+8,62,'#1a1a22')                                     # body
        t.R(cx-12,54,cx+12,62,'#1a1a22')                                   # haunches
        t.R(cx+2,20,cx+12,36,'#1a1a22')                                    # head
        t.P(cx+4,16,'#1a1a22');t.P(cx+5,16,'#1a1a22');t.P(cx+10,16,'#1a1a22');t.P(cx+11,16,'#1a1a22')
        t.R(cx+4,17,cx+5,20,'#1a1a22'); t.R(cx+10,17,cx+11,20,'#1a1a22')   # ears
        t.P(cx+6,24,GOLD_L); t.P(cx+10,24,GOLD_L)                          # eyes
        t.R(cx-8,36,cx+8,38,GOLD); t.R(cx-1,40,cx+1,60,GOLD)               # collar+staff
    elif i==2: # SAMURAI — torii post with paper lantern
        t.R(cx-3,14,cx+3,76,'#8a1c14'); t.R(cx-9,8,cx+9,13,'#a82418')
        t.R(cx-11,6,cx+11,8,'#5a100a')
        for dy in range(-9,10):                                            # lantern
            w=int(7.5*math.cos(dy/9*1.15))
            t.R(cx-w,38+dy,cx+w,38+dy,'#f2e6c8' if abs(dy)>3 else '#ffefd6')
        for ry in (32,38,44): t.R(cx-6,ry,cx+6,ry,'#b8241c')
        t.R(cx-2,27,cx+2,29,'#3a2a10'); t.R(cx-2,47,cx+2,49,'#3a2a10')
        t.R(cx-1,50,cx+1,54,'#b8241c')                                     # tassel
    elif i==3: # ROYAL — gold candelabra + red banner
        t.R(cx-14,4,cx+14,40,'#7a1024')                                    # banner
        t.R(cx-14,4,cx+14,6,GOLD)
        for bx in range(-14,15,2):
            t.P(cx+bx,41+(0 if bx%4 else 2),'#7a1024')
        t.R(cx-4,14,cx+4,22,GOLD); t.R(cx-2,16,cx+2,20,GOLD_L)             # crest
        t.R(cx-1,30,cx+1,74,GOLD)                                          # pole
        t.R(cx-12,36,cx+12,38,GOLD)                                        # arms
        for ax in (-12,0,12):
            t.R(cx+ax-1,30,cx+ax+1,36,GOLD_D)
            t.R(cx+ax-1,26,cx+ax+1,30,'#f0e8d8')                           # candles
            t.R(cx+ax-1,22,cx+ax+1,25,'#ffd23a'); t.P(cx+ax,20,'#ff9a2a')  # flames
        t.R(cx-8,74,cx+8,79,GOLD_D)
    elif i==4: # MUSEUM — glass case on pedestal
        t.R(cx-11,48,cx+11,79,'#b8b8b0'); t.R(cx-13,44,cx+13,48,'#d8d8d2')
        t.R(cx-10,14,cx+10,44,'#9fc4cc')                                   # glass
        t.R(cx-10,14,cx+10,16,'#e8f6fa'); t.R(cx-10,14,cx-8,44,'#c8e4ea')
        t.R(cx-3,26,cx+3,42,GOLD); t.R(cx-5,24,cx+5,26,GOLD_L)             # artifact
        t.P(cx-6,18,'#ffffff'); t.P(cx+7,20,'#ffffff')
    elif i==5: # TECH — server obelisk
        t.R(cx-9,10,cx+9,76,'#10121e'); t.R(cx-9,10,cx+9,12,'#2a2e44')
        for ly in range(16,72,8):
            c='#1eb8c8' if hsh(1,ly)>0.3 else '#33ff88'
            t.R(cx-6,ly,cx-4,ly,c); t.R(cx-1,ly,cx+3,ly,'#0a2a30')
            if hsh(2,ly)>0.5: t.P(cx+6,ly,c)
        t.R(cx-1,2,cx+1,10,'#2a2e44'); t.P(cx,0,'#ff4a4a')                 # antenna
    elif i==6: # ARMORY — armor stand
        t.R(cx-2,20,cx+2,70,'#3a2a14'); t.R(cx-10,72,cx+10,79,'#2a1e10')
        for dy in range(-5,6):                                             # helmet
            w=int(6*math.cos(dy/5*0.9))
            t.R(cx-w,14+dy,cx+w,14+dy,'#c8c8d0')
        t.R(cx-4,14,cx+4,16,'#0a0a10')                                     # visor
        t.R(cx-2,10,cx+2,8,'#b8241c')                                      # plume
        t.R(cx-9,24,cx+9,46,'#a8a8b2'); t.R(cx-9,24,cx-6,46,'#888892')     # breastplate
        t.R(cx-1,26,cx+1,44,'#6a6a74')
        t.R(cx-16,30,cx-10,52,'#7a1a12')                                   # shield
        t.R(cx-15,32,cx-11,34,GOLD)
        t.R(cx+12,26,cx+13,62,'#c8c8d0'); t.R(cx+10,28,cx+15,30,GOLD_D)    # sword
    elif i==7: # GALLERY — easel with painting
        t.R(cx-12,20,cx-10,76,'#6a4a2a'); t.R(cx+10,20,cx+12,76,'#6a4a2a')
        t.R(cx-1,20,cx+1,70,'#6a4a2a'); t.R(cx-13,44,cx+13,46,'#5a3c20')
        t.R(cx-11,16,cx+11,42,GOLD)                                        # frame
        t.R(cx-9,18,cx+9,40,'#28486a')
        for yy in range(18,41):
            for xx in range(cx-9,cx+10):
                if hsh(xx,yy,12)<0.16: t.P(xx,yy,'#7aa2d4')
        t.R(cx-4,30,cx+5,36,'#c86a3a')                                     # sunset blob
    else:      # 8 VAULT — crystals on gold mound
        for x in range(4,44,3):                                            # gold mound
            h=4+int(hsh(x,5)*8)
            t.R(x,79-h,x+2,79,'#c89a2a'); t.P(x+1,79-h,GOLD_L)
        for (gx,gh,c,cl) in ((14,34,'#a050e0','#d0a0ff'),(26,46,'#40c0e0','#9ae8ff'),(36,26,'#e04060','#ff8aa0')):
            for dy in range(gh):
                w=max(1,int((1-dy/gh)*6))
                t.R(gx-w,76-dy,gx+w,76-dy,c)
            t.P(gx-1,76-gh+2,cl); t.P(gx,76-gh,cl)
    return t.img

# RPG foes: heartbreak imp (walk x3) + cupid skull (fly x3), 34x38
def foe(kind,f):
    t=Tile(34,38); cx=17
    if kind==0:  # imp — hunched shadow w/ cracked heart
        bob=[0,1,0][f]; step=[-2,0,2][f]
        for y in range(10,30):                                             # body blob
            p=(y-10)/20
            w=5+7*math.sin(min(1,p*1.2)*math.pi*0.6)
            t.R(cx-w,y+bob,cx+w,y+bob,'#241432' if hsh(1,y,f)>0.3 else '#180c22')
        t.R(cx-6,6+bob,cx+6,14+bob,'#241432')                              # head
        t.P(cx-5,4+bob,'#241432'); t.P(cx+5,4+bob,'#241432')               # horns
        t.P(cx-4,3+bob,'#3a2452'); t.P(cx+4,3+bob,'#3a2452')
        t.R(cx-4,9+bob,cx-2,10+bob,'#ff2a3a'); t.R(cx+2,9+bob,cx+4,10+bob,'#ff2a3a')
        # cracked pink heart on chest
        t.R(cx-3,18+bob,cx+3,22+bob,'#ff5a8a'); t.P(cx-2,17+bob,'#ff5a8a'); t.P(cx+2,17+bob,'#ff5a8a')
        t.P(cx,23+bob,'#ff5a8a'); t.R(cx,18+bob,cx,22+bob,'#7a1024')       # crack
        t.R(cx-6+step,30,cx-3+step,35,'#180c22')                           # feet
        t.R(cx+3-step,30,cx+6-step,35,'#180c22')
    else:        # cupid skull — winged skull, tilted halo
        bob=[0,-2,0][f]; wf=[3,7,3][f]
        for dx in range(2,2+wf):                                           # wings
            t.R(cx-8-dx,14+bob+(dx//2),cx-8-dx,20+bob-(dx//2),'#d8d4e8')
            t.R(cx+8+dx,14+bob+(dx//2),cx+8+dx,20+bob-(dx//2),'#d8d4e8')
        t.R(cx-6,10+bob,cx+6,22+bob,'#e8e4da')                             # skull
        t.R(cx-4,22+bob,cx+4,26+bob,'#d8d4c8')                             # jaw
        t.R(cx-4,14+bob,cx-1,17+bob,'#0a0a10'); t.R(cx+1,14+bob,cx+4,17+bob,'#0a0a10')
        t.P(cx-2,15+bob,'#ff2a3a'); t.P(cx+3,15+bob,'#ff2a3a')             # pupils
        for xx in range(-3,4,2): t.P(cx+xx,24+bob,'#8a8478')               # teeth
        t.R(cx-5,5+bob,cx+7,6+bob,GOLD)                                    # tilted halo
        t.P(cx-6,6+bob,GOLD); t.P(cx+8,5+bob,GOLD)
    return t.img

dec=Image.new('RGBA',(48*9,80),(0,0,0,0))
for i in range(9): dec.paste(decor(i),(48*i,0))
dec=dec.resize((48*9*3,240),Image.NEAREST); dec.save(os.path.join(OUT,'decor.png'))
print('decor',dec.size)

foes=Image.new('RGBA',(34*6,38),(0,0,0,0))
for k in range(2):
    for f in range(3): foes.paste(foe(k,f),(34*(k*3+f),0))
foes=foes.resize((34*6*4,38*4),Image.NEAREST); foes.save(os.path.join(OUT,'foes.png'))
print('foes',foes.size)

pv=Image.new('RGBA',(dec.width,240+38*4+8),(24,12,36,255))
pv.paste(dec,(0,0),dec); pv.paste(foes,(0,248),foes)
pv.save(os.path.join(OUT,'decor_preview.png')); print('done')
