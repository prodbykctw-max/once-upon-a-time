import base64, io, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GDIR = os.path.join(ROOT, 'assets', 'renders', 'ground')
GNAMES = ['library','meadow','blossom','rose','lake','glade','sunflower','clouds','sunset']

# grounds: 256x256 JPEG q82 (no alpha needed)
gout = []
for i, n in enumerate(GNAMES):
    im = Image.open(os.path.join(GDIR, f'g{i}_{n}.png')).convert('RGB').resize((256, 256), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=82)
    gout.append('data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode())
    print(f'g{i} {len(b.getvalue())//1024}KB')

# props sheet: lossy WebP keeping alpha
im = Image.open(os.path.join(ROOT, 'assets', 'renders', 'sheet_outprops.png')).convert('RGBA')
b = io.BytesIO(); im.save(b, 'WEBP', quality=80, method=6)
props = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
print(f'props {len(b.getvalue())//1024}KB')

js = 'var GLWDATA={grounds:[' + ','.join('"%s"' % g for g in gout) + '],props:"%s"};' % props
open(os.path.join(ROOT, 'tools', 'glwdata.js'), 'w').write(js)
print('total JS', len(js)//1024, 'KB')

# Splice into index.html IN PLACE. This step used to be missing -- the script
# only wrote glwdata.js, so re-rendered grounds never reached the game and an
# old stage kept loading. Replace only `grounds` and `props`; wall/ceil are
# appended by embed_hall_prince.py and must survive untouched.
import re
idx = os.path.join(ROOT, 'index.html')
src = io.open(idx, encoding='utf-8').read()
m = re.search(r'var GLWDATA=\{grounds:\[.*?\],props:"[^"]*"', src, re.S)
assert m, 'GLWDATA grounds/props block not found'
new = 'var GLWDATA={grounds:[' + ','.join('"%s"' % g for g in gout) + '],props:"%s"' % props
src = src[:m.start()] + new + src[m.end():]
io.open(idx, 'w', encoding='utf-8', newline='\n').write(src)
print('index.html now', len(src)//1024, 'KB')
