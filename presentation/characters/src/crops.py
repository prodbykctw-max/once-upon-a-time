import os
from PIL import Image
import os, sys
# repo root = three levels up from presentation/characters/src/
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT=os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT,exist_ok=True)
def cut(im,dst,maxh=560):
    bb=im.split()[3].getbbox(); im=im.crop(bb)
    if im.height>maxh:
        im=im.resize((max(1,round(im.width*maxh/im.height)),maxh),Image.LANCZOS)
    im.save(dst,optimize=True); return im.size
b=Image.open(os.path.join(R,'web','78f95835ae52.webp')).convert('RGBA')
BK=['ink-warden','thistle-ogre','blossom-revenant','thorn-queen','lake-wraith','toadstool-warlock','scarecrow-king','storm-titan','the-groom-who-lied']
for i,k in enumerate(BK):
    print(k, cut(b.crop((0,i*280,200,(i+1)*280)), f'{OUT}/boss-{k}.png'))
f=Image.open(os.path.join(R,'web','e3bc36ab1807.webp')).convert('RGBA')
FK=['thorn-goblin','cursed-raven','nightshade-sprite','bramble-knight','wisp-swarm','rose-wraith']
for i,k in enumerate(FK):
    print(k, cut(f.crop((i*6*136,0,i*6*136+136,152)), f'{OUT}/foe-{k}.png', 300))
for nm,cw,src,fr in [('idle',89,'web/865c17b4dacb.png',0),('attack',154,'web/6c4f4b151d3d.png',3),('belt',150,'web/5e3c3ac40f3b.png',2),('dance',120,'web/89251d16231c.png',4)]:
    a=Image.open(os.path.join(R,src)).convert('RGBA')
    print('jande-'+nm, cut(a.crop((fr*cw,0,(fr+1)*cw,154)), f'{OUT}/jande-{nm}.png', 620))
print('total KB', sum(os.path.getsize(os.path.join(OUT,x)) for x in os.listdir(OUT))//1024)
