import os
from PIL import Image, ImageDraw, ImageFont
import os, sys
# repo root = three levels up from presentation/characters/src/
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT=os.path.join(R,'presentation','characters')
CF='/mnt/skills/examples/canvas-design/canvas-fonts'
INK,INK2,CREAM,GOLD,DIM=(24,19,32),(33,26,44),(232,224,207),(255,224,138),(150,140,160)
def F(n,s): return ImageFont.truetype(os.path.join(CF,n),s)
def STORY(s): return ImageFont.truetype(os.path.join(R,'web','435323e92ad8.ttf'),s)
H1,H2,BOLD,BODY,MONO,SMALL=STORY(74),STORY(34),F('Lora-Bold.ttf',25),F('Lora-Regular.ttf',20),F('GeistMono-Regular.ttf',17),F('GeistMono-Regular.ttf',15)

# tp, name, drawn WxH in game, flight, behaviour, blood, first stage
FOES=[
 (0,'THORN GOBLIN',(112,124),'GROUND','A troll on the floor. Patrols at 0.7, then accelerates to 1.9 the moment she is inside 340px. Ledge-guarded — it will stop at the brink of a pit rather than glide across.','118,168,54','green sap',0),
 (1,'CURSED RAVEN',(100,110),'FLYER','Bobs on a slow sine at its hover line, then DIVES to her exact height once she is inside 170px. Closes at 1.6.','58,52,72','smoke',1),
 (2,'NIGHTSHADE SPRITE',(100,110),'FLYER','Hovers wide and out of reach on a 46px swing, then darts. The dash window is 40 of every 150 frames and it crosses at 3.4 — nearly double the raven.','226,150,255','violet ichor',3),
 (3,'BRAMBLE KNIGHT',(138,152),'GROUND','The heaviest thing on the floor and the largest sprite in the set. Tops out at 1.15 with 0.92 inertia, so it accelerates and turns slowly — every approach is telegraphed. Ledge-guarded.','96,150,52','green sap',4),
 (4,'WISP SWARM',(88,96),'FLYER','The smallest and the fastest to change its mind. Weaves on a 0.09 sine while closing, and inside 150px it swarms her head on a 0.3 oscillation.','150,235,255','pale light',5),
 (5,'ROSE WRAITH',(124,138),'FLYER','The elite. Homes from 420px away — further than anything else sees — and never stops, but only at 1.05. It is the one flyer that bleeds RED.','196,26,64','red',7),
]
ROST=[[0],[0,1],[0,1],[0,1,2],[0,1,2,3],[0,1,2,3,4],[0,1,2,3,4],[0,1,2,3,4,5],[0,1,2,3,4,5]]
STG=['ONCE UPON A PAGE','FIRST LIGHT MEADOW','THE PETAL MILE','THE ROSE WALTZ','THE MIRROR LAKE','THE WISHING GLADE','THE GOLDEN HOUR','THE SKY GARDENS','HER ENCORE']

at=Image.open(os.path.join(R,'web','e3bc36ab1807.webp')).convert('RGBA')
SC=1.12; CW,CH=136,152
rowh=int(CH*SC)+118
W=54+int(CW*6*SC)+470; Hh=236+rowh*6+40
img=Image.new('RGB',(W,Hh),INK); d=ImageDraw.Draw(img)
for i in range(Hh): d.line([(0,i),(W,i)],fill=tuple(int(a+(b-a)*(i/Hh)) for a,b in zip(INK2,INK)))
d.text((54,40),'THE FOE ROSTER',font=H1,fill=CREAM)
d.text((58,132),'SIX TYPES — 36 hand-painted cells, 6 frames each',font=BOLD,fill=GOLD)
d.text((58,168),'Atlas 4896x152, cells 136x152. All six share one 52x58 collider anchored at the feet; the drawn size differs per type so the painting reads.',font=SMALL,fill=DIM)
d.line([(54,206),(W-54,206)],fill=(70,60,86),width=2)
y=236
for tp,nm,(dw,dh),fly,beh,gore,gname,first in FOES:
    gc=tuple(int(v) for v in gore.split(','))
    d.rectangle([54,y,58,y+int(CH*SC)+86],fill=gc)
    d.text((80,y),nm,font=H2,fill=CREAM)
    tag='GROUND — ledge-guarded' if fly=='GROUND' else 'FLYER'
    tl=d.textlength(nm,font=H2)
    d.rounded_rectangle([80+tl+18,y+8,80+tl+34+d.textlength(tag,font=SMALL),y+32],6,fill=(60,50,76))
    d.text((80+tl+26,y+13),tag,font=SMALL,fill=GOLD)
    d.text((80,y+44),f'tp{tp}  ·  drawn {dw}x{dh} px  ·  bleeds {gname} ({gore})',font=MONO,fill=DIM)
    yy=y+76
    for f in range(6):
        c=at.crop(((tp*6+f)*CW,0,(tp*6+f+1)*CW,CH)).resize((int(CW*SC),int(CH*SC)),Image.NEAREST)
        img.paste(c,(80+int(f*CW*SC),yy),c)
    tx=80+int(CW*6*SC)+28
    # wrap the behaviour note
    words=beh.split(); line=''; ly=yy+4
    for w in words:
        t=(line+' '+w).strip()
        if d.textlength(t,font=BODY)>380: d.text((tx,ly),line,font=BODY,fill=(198,190,208)); ly+=27; line=w
        else: line=t
    d.text((tx,ly),line,font=BODY,fill=(198,190,208)); ly+=40
    stages=[i for i in range(9) if tp in ROST[i]]
    d.text((tx,ly),'APPEARS IN',font=SMALL,fill=GOLD); ly+=22
    d.text((tx,ly),f'stages {stages[0]+1}-9  ({STG[first]} onward)',font=MONO,fill=DIM)
    y+=rowh
img.save(os.path.join(OUT,'02-foe-roster.png')); print('02-foe-roster.png',img.size)
