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
MONO,SMALL=F('GeistMono-Regular.ttf',18),F('GeistMono-Regular.ttf',15)
at=Image.open(os.path.join(R,'web','78f95835ae52.webp')).convert('RGBA')
CW,CH,ROW=200,280,8
SC=0.86; cw,ch=int(CW*SC),int(CH*SC)
W=54+cw*5+54; Hh=250+(ch+92)*2+70
img=Image.new('RGB',(max(W,1364),Hh),INK); W=img.width; d=ImageDraw.Draw(img)
for i in range(Hh): d.line([(0,i),(W,i)],fill=tuple(int(a+(b-a)*(i/Hh)) for a,b in zip(INK2,INK)))
d.text((54,36),'THE GROOM’S DEATH',font=STORY(60),fill=CREAM)
d.text((58,118),'The finale boss played his defeat animation BACKWARDS. Found by measuring, now fixed.',font=F('Lora-Bold.ttf',22),fill=GOLD)
d.text((58,152),'Every other boss drops its alpha-weighted centroid DOWN the cell and sheds mass. Row 8 alone travelled UP (-20.7px) and GAINED 4.9',font=SMALL,fill=DIM)
d.text((58,174),'points of coverage, and ended MOST like its own standing pose (IoU 0.505, the highest of its five). The art is right; the order was not.',font=SMALL,fill=DIM)
d.line([(54,206),(W-54,206)],fill=(70,60,86),width=2)
for k,(lab,order,col) in enumerate([('BEFORE — as it shipped',[4,5,6,7,8],(224,96,110)),('AFTER — cells 8 down to 4',[8,7,6,5,4],(132,224,160))]):
    y=234+k*(ch+92)
    d.rectangle([54,y,58,y+ch+44],fill=col)
    d.text((78,y),lab,font=F('Lora-Bold.ttf',23),fill=col)
    yy=y+34
    for i,c in enumerate(order):
        cc=at.crop((c*CW,ROW*CH,(c+1)*CW,(ROW+1)*CH)).resize((cw,ch),Image.NEAREST)
        img.paste(cc,(78+i*cw,yy),cc)
        d.text((78+i*cw+6,yy+ch+4),f'col {c}',font=SMALL,fill=DIM)
    d.text((78,yy+ch+26),'he collapses into frame, then STANDS BACK UP' if k==0 else 'he is struck, he burns, he falls',font=F('Lora-Italic.ttf',19),fill=(198,190,208))
img.save(os.path.join(OUT,'05-groom-defeat-fix.png')); print('05-groom-defeat-fix.png',img.size)
