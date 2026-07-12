#!/usr/bin/env python3
"""Bake the Temple View pixel-art world pack:
- walls.png   : 9 themed wall textures, 48x64 cells, x3 upscale
- floors.png  : 9 themed floor tiles,  32x32 cells, x3 upscale
- chaser.png  : 4-frame wraith 'The Groom's Shadow', 44x56, x4
- items.png   : 8 icons 16x16 [magnet,boost,x2,shield,gem,arrowL,arrowR,meganote], x4
"""
from PIL import Image
import math, os

OUT = os.path.dirname(os.path.abspath(__file__))

def hexc(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))+(255,)
def hsh(x,y,s=0): v=math.sin(x*127.1+y*311.7+s*74.7)*43758.5453; return v-math.floor(v)

class Tile:
    def __init__(self,w,h,bg=None):
        self.w,self.h=w,h
        self.img=Image.new('RGBA',(w,h),hexc(bg) if bg else (0,0,0,0))
        self.px=self.img.load()
    def P(self,x,y,c):
        x,y=int(x),int(y)
        if 0<=x<self.w and 0<=y<self.h: self.px[x,y]=hexc(c)
    def R(self,x0,y0,x1,y1,c):
        for y in range(int(y0),int(y1)+1):
            for x in range(int(x0),int(x1)+1): self.P(x,y,c)
    def noise(self,c,amt,s=0):
        for y in range(self.h):
            for x in range(self.w):
                if hsh(x,y,s)<amt: self.P(x,y,c)

# ─────────────────────────── WALLS (48x64) ───────────────────────────
def wall(i):
    t=Tile(48,64)
    if i==0:  # LIBRARY — wooden shelves + colored spines
        t.R(0,0,47,63,'#3a2412')
        pal=['#8a3324','#3f5f7f','#7f9f4f','#6f3f8f','#bf8f3f','#4f7f6f','#9f4f4f','#2f4f2f']
        for row in range(4):
            ry=2+row*16
            t.R(0,ry+13,47,ry+15,'#5a3a1c')      # shelf board
            x=2
            k=0
            while x<46:
                w=2+int(hsh(x,row)*3)
                h=10+int(hsh(x,row,7)*3)
                t.R(x,ry+13-h,x+w,ry+12,pal[(x+row*3)%len(pal)])
                t.R(x,ry+13-h,x,ry+12,'#00000000'.replace('#00000000','#2a1a0a'))
                x+=w+1; k+=1
        t.R(0,0,47,1,'#5a3a1c'); t.R(0,62,47,63,'#241505')
    elif i==1:  # EGYPT — sandstone + hieroglyphs + ankh
        t.R(0,0,47,63,'#c9a35a')
        for y in range(0,64,16):
            t.R(0,y,47,y,'#8a6a30')
            off=8 if (y//16)%2 else 0
            for x in range(off,48,16): t.R(x,y,x,min(63,y+15),'#8a6a30')
        t.noise('#b8924a',0.18,1); t.noise('#dbb76e',0.10,2)
        for gy,gx in ((6,6),(6,26),(22,14),(22,36),(38,6),(38,28),(54,18),(54,40)):
            g=int(hsh(gx,gy)*3)
            if g==0:  # ankh
                t.R(gx,gy+3,gx,gy+8,'#6a4a18'); t.R(gx-2,gy+5,gx+2,gy+5,'#6a4a18')
                t.P(gx-1,gy,'#6a4a18');t.P(gx+1,gy,'#6a4a18');t.P(gx,gy+1,'#6a4a18');t.P(gx-1,gy+2,'#6a4a18');t.P(gx+1,gy+2,'#6a4a18')
            elif g==1:  # eye
                t.R(gx-3,gy+3,gx+3,gy+3,'#6a4a18'); t.P(gx,gy+2,'#6a4a18'); t.R(gx-2,gy+4,gx+2,gy+4,'#6a4a18')
            else:  # bird
                t.R(gx-2,gy+2,gx+1,gy+2,'#6a4a18'); t.P(gx+2,gy+1,'#6a4a18'); t.R(gx-1,gy+3,gx,gy+6,'#6a4a18')
    elif i==2:  # SAMURAI — dark wood + red lantern + katana
        t.R(0,0,47,63,'#2a1a12')
        for x in range(0,48,8): t.R(x,0,x,63,'#1a0e08')
        t.noise('#3a2418',0.2,3)
        t.R(4,8,20,10,'#0e0804')                     # rail
        cx,cy=32,20
        for dy in range(-8,9):                       # red lantern
            w=int(6.5*math.cos(dy/8*1.2))
            t.R(cx-w,cy+dy,cx+w,cy+dy,'#b8241c' if abs(dy)>2 else '#e04a30')
        t.R(cx-2,cy-11,cx+2,cy-9,'#3a2a10'); t.R(cx-2,cy+9,cx+2,cy+11,'#3a2a10')
        t.R(cx,cy-8,cx,cy+8,'#7a100c')
        t.R(6,40,7,58,'#c9c4b8'); t.R(8,38,9,40,'#8a6a30')   # katana on stand
        t.R(4,56,12,57,'#0e0804'); t.R(4,44,12,45,'#0e0804')
    elif i==3:  # ROYAL — purple drapes + stained glass
        t.R(0,0,47,63,'#2a1040')
        for x in range(48):                          # drape folds
            ph=math.sin(x*0.55)*0.5+0.5
            c='#4a1a70' if ph>0.62 else ('#38125a' if ph>0.3 else '#240c3e')
            t.R(x,0,x,63,c)
        t.R(0,0,47,3,'#d4af37')
        cx=24
        for dy in range(10,44):                      # arched window
            w=11 if dy>18 else int(math.sqrt(max(0,121-((18-dy)*1.6)**2)))
            if w>0:
                for dx in range(-w,w+1):
                    seg=(dx+12)//8+(dy//12)
                    c=['#c04060','#4060c0','#40a060','#c0a040'][seg%4]
                    t.P(cx+dx,dy,c)
                t.P(cx-w,dy,'#1a0a2e'); t.P(cx+w,dy,'#1a0a2e')
        t.R(cx,10,cx,43,'#1a0a2e'); t.R(cx-11,28,cx+11,28,'#1a0a2e')
        t.R(cx-12,44,cx+12,45,'#d4af37')
    elif i==4:  # MUSEUM — marble + display case
        t.R(0,0,47,63,'#c8c8c2')
        for y in range(0,64,16):
            t.R(0,y,47,y,'#9a9a94')
            for x in range((8 if (y//16)%2 else 0),48,16): t.R(x,y,x,min(63,y+15),'#9a9a94')
        t.noise('#b8b8b0',0.15,4); t.noise('#d8d8d2',0.1,5)
        t.R(14,18,34,48,'#6a7a80')                   # case
        t.R(16,20,32,42,'#9fc4cc'); t.R(17,21,25,28,'#c8e4ea')
        t.R(21,30,27,40,'#7a5a30')                   # artifact
        t.R(19,40,29,41,'#4a4a44')
    elif i==5:  # TECH — dark panel + cyan circuits
        t.R(0,0,47,63,'#10121e')
        for y in range(0,64,16): t.R(0,y,47,y,'#080a12')
        for x in range(0,48,12): t.R(x,0,x,63,'#080a12')
        pts=[(4,6),(20,6),(20,22),(38,22),(38,44),(12,44),(12,56),(30,56)]
        for k in range(len(pts)-1):
            (x0,y0),(x1,y1)=pts[k],pts[k+1]
            t.R(min(x0,x1),min(y0,y1),max(x0,x1),max(y0,y1),'#1eb8c8')
        for (px,py) in pts: t.R(px-1,py-1,px+1,py+1,'#7ff2ff')
        for y in range(4,64,10):
            if hsh(3,y)>0.5: t.P(44,y,'#33ff88')
    elif i==6:  # ARMORY — flagstone + shield + torch
        t.R(0,0,47,63,'#5a5a58')
        for y in range(0,64,12):
            t.R(0,y,47,y,'#3a3a38')
            for x in range((6 if (y//12)%2 else 0),48,13): t.R(x,y,x,min(63,y+11),'#3a3a38')
        t.noise('#4c4c4a',0.2,6); t.noise('#6a6a68',0.1,7)
        cx,cy=14,26                                   # crest shield
        for dy in range(-8,10):
            w=7 if dy<3 else 7-int((dy-2)*1.1)
            if w>0: t.R(cx-w,cy+dy,cx+w,cy+dy,'#8a2a20' if dy<3 else '#6a1a14')
        t.R(cx,cy-8,cx,cy+8,'#d4af37'); t.R(cx-6,cy-2,cx+6,cy-2,'#d4af37')
        t.R(36,20,37,34,'#4a3010')                    # torch
        t.R(34,14,39,19,'#ff9a2a'); t.R(35,12,38,15,'#ffd23a')
    elif i==7:  # GALLERY — cream wall + gilt frames
        t.R(0,0,47,63,'#d8d0be')
        t.noise('#ccc4b2',0.12,8)
        t.R(0,8,47,9,'#a89868')
        for fx,fy,fw,fh,k in ((6,16,15,20,0),(28,14,14,26,1),(10,44,26,14,2)):
            t.R(fx-2,fy-2,fx+fw+2,fy+fh+2,'#b08c28')
            t.R(fx-1,fy-1,fx+fw+1,fy+fh+1,'#d4af37')
            base=['#3a5a8a','#8a3a5a','#4a7a4a'][k]
            t.R(fx,fy,fx+fw,fy+fh,base)
            for yy in range(fy,fy+fh+1):
                for xx in range(fx,fx+fw+1):
                    if hsh(xx,yy,9+k)<0.2: t.P(xx,yy,['#7a9aca','#ca7a9a','#8aba8a'][k])
    else:  # 8 VAULT — dark stone + gems + gold
        t.R(0,0,47,63,'#181022')
        t.noise('#241832',0.25,10); t.noise('#100a18',0.2,11)
        for gx,gy,c,cl in ((10,14,'#e04060','#ff8aa0'),(34,10,'#40c0e0','#9ae8ff'),(22,30,'#a050e0','#d0a0ff'),(40,38,'#40e080','#a0ffc0'),(8,44,'#e0c040','#fff0a0')):
            t.R(gx-2,gy,gx+2,gy,c); t.R(gx-1,gy-2,gx+1,gy+2,c); t.P(gx,gy-3,cl); t.P(gx-1,gy-1,cl)
        for x in range(2,46,4):                       # gold pile at base
            h=3+int(hsh(x,1)*4)
            t.R(x,63-h,x+2,63,'#c89a2a'); t.P(x+1,63-h,'#ffd76a')
    return t.img

# ─────────────────────────── FLOORS (32x32) ───────────────────────────
def floor(i):
    t=Tile(32,32)
    base=[('#5a3a1c','#4a2e14','#6a4a26'),('#c9a35a','#b8924a','#8a6a30'),
          ('#3a241a','#2a1810','#4a3222'),('#701828','#5a1220','#d4af37'),
          ('#b8b8b2','#a8a8a2','#8a8a84'),('#141824','#0c101a','#1eb8c8'),
          ('#4c4c4a','#3c3c3a','#2a2a28'),('#6a4a2a','#5a3c20','#7a5a36'),
          ('#221830','#181020','#c89a2a')][i]
    t.R(0,0,31,31,base[0])
    for y in range(32):
        for x in range(32):
            if hsh(x,y,20+i)<0.15: t.P(x,y,base[1])
    if i in (0,2,7):   # planks
        for y in range(0,32,8):
            t.R(0,y,31,y,base[1])
            t.R((8 if (y//8)%2 else 20),y,(8 if (y//8)%2 else 20),min(31,y+7),base[1])
    elif i in (1,4,6): # stone grid
        for y in range(0,32,16):
            t.R(0,y,31,y,base[2])
            for x in range((8 if (y//16)%2 else 0),32,16): t.R(x,y,x,min(31,y+15),base[2])
    elif i==3:         # carpet w/ gold border stripes
        t.R(0,2,31,2,base[2]); t.R(0,29,31,29,base[2])
        for y in range(8,28,8):
            for x in range(2,30,8): t.P(x,y,base[2])
    elif i==5:         # tech grid glow
        for y in range(0,32,8): t.R(0,y,31,y,base[2])
        for x in range(0,32,8): t.R(x,0,x,31,base[2])
    else:              # vault flecks
        for k in range(14):
            x,y=int(hsh(k,3)*31),int(hsh(k,9)*31); t.P(x,y,base[2])
    return t.img

# ─────────────────────────── CHASER (44x56 ×4) ───────────────────────────
def chaser(fi):
    t=Tile(44,56); cx=22
    fl=math.sin(fi/4*2*math.pi)
    # tattered dark shroud
    for y in range(8,52):
        p=(y-8)/44
        w=6+14*p+math.sin(y*0.8+fi*1.6)*2
        x0,x1=int(cx-w/2),int(cx+w/2)
        for x in range(x0,x1+1):
            c='#0c0614' if hsh(x,y,fi)<0.75 else '#1a0e28'
            t.P(x,y,c)
        if y>40 and int(hsh(y,fi)*4)==0: t.P(x0,y,'#00000000'.replace('#00000000','#0c0614'))
    # ragged hem
    for x in range(4,40,3):
        h=int(hsh(x,fi)*5)
        t.R(x,51-h,x+1,51,'#0c0614')
    # hood + face void
    for dy in range(-7,7):
        w=int(8*math.cos(dy/7*1.1))
        t.R(cx-w,14+dy,cx+w,14+dy,'#150a24')
    t.R(cx-4,12,cx+4,18,'#050208')
    # burning eyes
    ey=14+int(fl*1)
    t.R(cx-3,ey,cx-2,ey+1,'#ff2a3a'); t.R(cx+2,ey,cx+3,ey+1,'#ff2a3a')
    t.P(cx-3,ey,'#ffb0b0'); t.P(cx+2,ey,'#ffb0b0')
    # broken gold crown
    t.R(cx-5,6,cx+5,8,'#b8922a')
    for x in range(-5,6,3): t.P(cx+x,5,'#d4af37')
    t.P(cx+4,4,'#d4af37')
    # claw hands reaching
    hy=30+int(fl*3)
    t.R(2,hy,6,hy+1,'#150a24'); t.P(1,hy-1,'#2a1a3e');t.P(2,hy+2,'#2a1a3e')
    t.R(38,hy+2,42,hy+3,'#150a24'); t.P(43,hy+1,'#2a1a3e');t.P(42,hy+4,'#2a1a3e')
    return t.img

# ─────────────────────────── ITEMS (16x16 ×8) ───────────────────────────
def items():
    sheet=Image.new('RGBA',(16*8,16),(0,0,0,0))
    def cell(k):
        t=Tile(16,16); return t
    # 0 magnet
    t=cell(0)
    for dy in range(2,10): t.P(4,dy,'#e03030');t.P(5,dy,'#ff6a5a');t.P(10,dy,'#3050e0');t.P(11,dy,'#6a8aff')
    t.R(4,10,11,12,'#c8c8d0'); t.R(5,11,10,11,'#eaeaf2')
    t.R(4,2,5,3,'#f0f0f8'); t.R(10,2,11,3,'#f0f0f8')
    sheet.paste(t.img,(0,0))
    # 1 boost wing
    t=cell(1)
    for k in range(3):
        y=4+k*3
        t.R(2+k,y,12-k,y+1,'#ffd23a'); t.P(13-k,y,'#fff0a0')
    t.R(6,10,9,13,'#ff9a2a')
    sheet.paste(t.img,(16,0))
    # 2 x2 star
    t=cell(2)
    for (x,y) in ((7,1),(8,1),(6,3),(9,3),(2,5),(13,5),(4,7),(11,7),(3,12),(12,12),(7,9),(8,9)):
        t.P(x,y,'#ffd23a')
    t.R(5,4,10,8,'#ffd23a'); t.R(6,5,9,7,'#fff0a0')
    t.R(6,11,7,14,'#ff5a9a'); t.R(9,11,10,14,'#ff5a9a'); t.P(8,12,'#ff5a9a')
    sheet.paste(t.img,(32,0))
    # 3 shield
    t=cell(3)
    for dy in range(2,14):
        w=6 if dy<9 else 6-(dy-8)
        if w>0: t.R(8-w,dy,7+w,dy,'#20c8d8' if dy%2 else '#18a8b8')
    t.R(7,4,8,10,'#b0f4ff')
    sheet.paste(t.img,(48,0))
    # 4 gem
    t=cell(4)
    for dy in range(3,13):
        w=6-abs(dy-7)
        if w>0: t.R(8-w,dy,7+w,dy,'#b050ff' if dy>6 else '#d090ff')
    t.P(6,5,'#f0d8ff'); t.P(7,4,'#f0d8ff')
    sheet.paste(t.img,(64,0))
    # 5/6 arrows
    for k,dr in ((5,-1),(6,1)):
        t=cell(k)
        for s in range(6):
            x=8+dr*(s-3)
            t.R(x,4+s,x+1,4+s,'#ffd23a')
            t.R(x,12-s,x+1,12-s,'#ffd23a')
        t.R(8-(3*dr),7,8-(3*dr)+1,9,'#fff0a0')
        sheet.paste(t.img,(16*k,0))
    # 7 mega note (ENCORE)
    t=cell(7)
    t.R(9,2,10,10,'#ffd23a'); t.R(10,2,13,4,'#ffd23a')
    for dy in range(9,13):
        w=3-abs(dy-11)
        t.R(6-w,dy,6+w,dy,'#ffb02a')
    t.P(5,10,'#fff0a0')
    sheet.paste(t.img,(112,0))
    return sheet

def save(img,name,scale):
    img=img.resize((img.width*scale,img.height*scale),Image.NEAREST)
    img.save(os.path.join(OUT,name)); print(name,img.size)

walls=Image.new('RGBA',(48*9,64),(0,0,0,0))
for i in range(9): walls.paste(wall(i),(48*i,0))
save(walls,'walls.png',3)

floors=Image.new('RGBA',(32*9,32),(0,0,0,0))
for i in range(9): floors.paste(floor(i),(32*i,0))
save(floors,'floors.png',3)

ch=Image.new('RGBA',(44*4,56),(0,0,0,0))
for i in range(4): ch.paste(chaser(i),(44*i,0))
save(ch,'chaser.png',4)

save(items(),'items.png',4)

# preview
pv=Image.new('RGBA',(48*9*3,64*3+32*3+8),(24,12,36,255))
pv.paste(walls.resize((48*9*3,64*3),Image.NEAREST),(0,0))
pv.paste(floors.resize((32*9*3,32*3),Image.NEAREST),(0,64*3+8))
pv.save(os.path.join(OUT,'world_preview.png'))
print('done')
