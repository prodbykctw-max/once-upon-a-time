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
H1,H2,H3,BODY,MONO,SMALL=STORY(74),STORY(36),STORY(28),F('Lora-Regular.ttf',20),F('GeistMono-Regular.ttf',17),F('GeistMono-Regular.ttf',15)

STG=['ONCE UPON A PAGE','FIRST LIGHT MEADOW','THE PETAL MILE','THE ROSE WALTZ','THE MIRROR LAKE','THE WISHING GLADE','THE GOLDEN HOUR','THE SKY GARDENS','HER ENCORE']
# name, hp(normal), airborne, aura, gore rgb, gore name, one-line character note
B=[
 ('INK WARDEN',7,False,'Torn pages drift upward while ink motes fall through them.','26,20,34','ink','The library’s keeper. The first thing that tells her the story has a guard.'),
 ('THISTLE OGRE',9,False,'Kicked-up dust and floating thistle seed.','120,170,60','sap','A meadow brute. Heavy, blunt, and the first boss that actually hits back.'),
 ('BLOSSOM REVENANT',11,True,'A wraith’s veil of petals, all held in orbit.','255,150,205','petals','AIRBORNE. Never touches the ground, so it drifts and shoots instead of jumping.'),
 ('THORN QUEEN',13,False,'Rose-and-thorn motes coiling counter-clockwise.','200,20,55','red','Humanoid, and she bleeds RED — the rule across the whole cast: only flesh does.'),
 ('LAKE WRAITH',15,True,'Water beads trailing the serpentine glide, head to tail.','110,200,255','water','AIRBORNE and serpentine: a 58px vertical sway that couples into its horizontal glide.'),
 ('TOADSTOOL WARLOCK',17,False,'A low fog bank with a spore cloud rising out of it.','200,130,255','spores','The glade’s caster. Everything it throws is alive.'),
 ('SCARECROW KING',19,False,'Crows wheel overhead as straw scatters off him.','214,172,92','straw','Stuffed, crowned, and the only boss whose aura is other animals.'),
 ('STORM TITAN',21,False,'Churning cloud haze with lightning strobing inside it.','170,210,255','storm-light','Has its OWN attack table — charge-heavy, because the gusts carry it.'),
 ('THE GROOM WHO LIED',28,False,'Dark embers rising off a broken vow.','195,22,42','red','THE FINALE. 28 HP — a third again the Storm Titan. The story’s real antagonist, and he bleeds red.'),
]
at=Image.open(os.path.join(R,'web','78f95835ae52.webp')).convert('RGBA')
CW,CH=200,280

# This script makes sheet 04 only. Sheet 03 (the nine, full size) is boss3.py --
# an earlier version lived here and overwrote it, so it was removed.

# ── SHEET 4: every frame, idle + defeat ───────────────────────────────────
SC=0.60; cw2,ch2=int(CW*SC),int(CH*SC)
LBL=330; rowh=ch2+76
W=LBL+cw2*9+54+30; Hh=236+rowh*9+40
img=Image.new('RGB',(W,Hh),INK); d=ImageDraw.Draw(img)
for i in range(Hh): d.line([(0,i),(W,i)],fill=tuple(int(a+(b-a)*(i/Hh)) for a,b in zip(INK2,INK)))
d.text((54,40),'EVERY BOSS FRAME',font=H1,fill=CREAM)
d.text((58,132),'4 IDLE  +  5 DEFEAT  ×  9 BOSSES  =  81 cells, all painted',font=F('Lora-Bold.ttf',25),fill=GOLD)
d.text((58,168),'Idle cycles at 6fps through the fight. On the kill the five defeat frames play off GS.bossDeadT under a slow-mo KO spotlight and a push-in.',font=SMALL,fill=DIM)
d.line([(54,206),(W-54,206)],fill=(70,60,86),width=2)
d.text((LBL,214),'IDLE',font=SMALL,fill=GOLD); d.text((LBL+cw2*4+16,214),'DEFEAT',font=SMALL,fill=(220,110,120))
y=236
for i,(nm,hp,fl,aura,gore,gn,note) in enumerate(B):
    gc=tuple(int(v) for v in gore.split(','))
    d.rectangle([54,y,58,y+ch2+40],fill=gc)
    fs=30
    while fs>16 and ImageFont.truetype(os.path.join(R,'web','435323e92ad8.ttf'),fs).getlength(nm)>LBL-100: fs-=1
    d.text((78,y+4),nm,font=STORY(fs),fill=CREAM)
    d.text((78,y+42),f'Stage {i+1} — {STG[i]}',font=SMALL,fill=DIM)
    d.text((78,y+64),f'{hp} HP'+('  ·  AIRBORNE' if fl else ''),font=MONO,fill=GOLD)
    ly=y+92; line=''
    for w in ('Aura: '+aura).split():
        t=(line+' '+w).strip()
        if d.textlength(t,font=F('Lora-Italic.ttf',18))>LBL-100: d.text((78,ly),line,font=F('Lora-Italic.ttf',18),fill=(176,168,188)); ly+=23; line=w
        else: line=t
    d.text((78,ly),line,font=F('Lora-Italic.ttf',18),fill=(176,168,188))
    for c in range(9):
        cc=at.crop((c*CW,i*CH,(c+1)*CW,(i+1)*CH)).resize((cw2,ch2),Image.NEAREST)
        img.paste(cc,(LBL+c*cw2,y),cc)
    d.line([(LBL+cw2*4+6,y-4),(LBL+cw2*4+6,y+ch2+8)],fill=(70,60,86),width=2)
    y+=rowh
img.save(os.path.join(OUT,'04-boss-frames.png')); print('04-boss-frames.png',img.size)
