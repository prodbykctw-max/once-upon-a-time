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
def lift(c,mn=110):
    "A swatch must be visible on an ink ground. Ink (26,20,34) is not."
    l=0.299*c[0]+0.587*c[1]+0.114*c[2]
    if l>=mn: return c
    k=(mn+30)/max(l,1); return tuple(min(255,int(v*k)) for v in c)
STG=['ONCE UPON A PAGE','FIRST LIGHT MEADOW','THE PETAL MILE','THE ROSE WALTZ','THE MIRROR LAKE','THE WISHING GLADE','THE GOLDEN HOUR','THE SKY GARDENS','HER ENCORE']
B=[('INK WARDEN',7,False,'26,20,34','ink','The library’s keeper — the first thing that tells her this story has a guard.'),
 ('THISTLE OGRE',9,False,'120,170,60','sap','A meadow brute. Blunt, heavy, and the first boss that really hits back.'),
 ('BLOSSOM REVENANT',11,True,'255,150,205','petals','Airborne. Never touches the ground, so it drifts and shoots where the others jump and slam.'),
 ('THORN QUEEN',13,False,'200,20,55','red','Humanoid, and she bleeds RED — the rule across the whole cast is that only flesh does.'),
 ('LAKE WRAITH',15,True,'110,200,255','water','Airborne and serpentine: a 58px vertical sway that couples into its horizontal glide.'),
 ('TOADSTOOL WARLOCK',17,False,'200,130,255','spores','The glade’s caster. Everything it throws at her is alive.'),
 ('SCARECROW KING',19,False,'214,172,92','straw','Stuffed and crowned. The only boss whose aura is other animals — crows wheel over him.'),
 ('STORM TITAN',21,False,'170,210,255','storm-light','Has its OWN attack table, charge-heavy, because the gusts carry it across the arena.'),
 ('THE GROOM WHO LIED',28,False,'195,22,42','red','THE FINALE. 28 HP, a third again the Storm Titan. The story’s real antagonist — and he bleeds red.')]
at=Image.open(os.path.join(R,'web','78f95835ae52.webp')).convert('RGBA')
CW,CH=200,280
CARDW,PAD,COLS=430,24,3
NOTE=F('Lora-Regular.ttf',19); NAME=STORY(30); MONO=F('GeistMono-Regular.ttf',17); SMALL=F('GeistMono-Regular.ttf',15)
scratch=ImageDraw.Draw(Image.new('RGB',(10,10)))
def wrap(txt,font,w):
    out=[];line=''
    for word in txt.split():
        t=(line+' '+word).strip()
        if scratch.textlength(t,font=font)>w: out.append(line); line=word
        else: line=t
    out.append(line); return out
notes=[wrap(b[5],NOTE,CARDW-2*PAD) for b in B]
cellh=CH+24+118+max(len(n) for n in notes)*25+PAD
W=54+CARDW*COLS+(COLS-1)*20+54; Hh=250+(cellh+22)*3+40
img=Image.new('RGB',(W,Hh),INK); d=ImageDraw.Draw(img)
for i in range(Hh): d.line([(0,i),(W,i)],fill=tuple(int(a+(b-a)*(i/Hh)) for a,b in zip(INK2,INK)))
d.text((54,40),'THE NINE',font=STORY(76),fill=CREAM)
d.text((58,136),'ONE UNIQUE BOSS PER STAGE — gate, sealed arena, defeat, STAGE CLEAR',font=F('Lora-Bold.ttf',25),fill=GOLD)
d.text((58,174),'Atlas 1800x2520, cells 200x280, row = stage. 4 idle frames + 5 defeat frames each, 81 painted cells with no gaps.',font=SMALL,fill=DIM)
d.text((58,196),'HP shown at NORMAL difficulty (x1.4 on Hard, x0.7 on Easy). Frame 0 of the idle cycle shown.',font=SMALL,fill=DIM)
d.line([(54,228),(W-54,228)],fill=(70,60,86),width=2)
for i,(nm,hp,fl,gore,gn,note) in enumerate(B):
    cx=54+(i%COLS)*(CARDW+20); cy=250+(i//COLS)*(cellh+22)
    gc=tuple(int(v) for v in gore.split(',')); sw=lift(gc)
    d.rounded_rectangle([cx,cy,cx+CARDW,cy+cellh],12,fill=(30,24,40),outline=(62,52,78))
    d.rounded_rectangle([cx,cy,cx+CARDW,cy+5],2,fill=sw)
    c=at.crop((0,i*CH,CW,(i+1)*CH))
    img.paste(c,(cx+(CARDW-CW)//2,cy+18),c)
    ty=cy+CH+30
    d.text((cx+PAD,ty),f'STAGE {i+1}',font=SMALL,fill=sw)
    d.text((cx+PAD+d.textlength(f'STAGE {i+1}',font=SMALL)+14,ty),STG[i],font=SMALL,fill=DIM)
    fs=30
    while fs>17 and STORY(fs).getlength(nm)>CARDW-2*PAD: fs-=1
    d.text((cx+PAD,ty+22),nm,font=STORY(fs),fill=CREAM)
    d.text((cx+PAD,ty+62),f'{hp} HP',font=MONO,fill=GOLD)
    if fl:
        xw=cx+PAD+d.textlength(f'{hp} HP',font=MONO)+14
        d.rounded_rectangle([xw,ty+60,xw+22+d.textlength('AIRBORNE',font=SMALL),ty+82],6,fill=(58,48,74))
        d.text((xw+11,ty+64),'AIRBORNE',font=SMALL,fill=(150,220,255))
    d.rectangle([cx+PAD,ty+92,cx+PAD+13,ty+105],fill=sw)
    d.text((cx+PAD+21,ty+90),f'bleeds {gn}',font=SMALL,fill=DIM)
    ly=ty+118
    for ln in notes[i]: d.text((cx+PAD,ly),ln,font=NOTE,fill=(192,184,202)); ly+=25
img.save(os.path.join(OUT,'03-the-nine-bosses.png')); print('03-the-nine-bosses.png',img.size)
