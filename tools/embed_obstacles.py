import base64, io, os, re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'renders', 'obstacles')
# cell sizes must match FRAME in obstacles3d.py
KINDS = {'low': (256, 96), 'gate': (256, 192), 'wall': (256, 224)}

payload = {}
for kind, (cw, ch) in KINDS.items():
    sheet = Image.new('RGBA', (cw * 9, ch), (0, 0, 0, 0))
    for i in range(9):
        p = os.path.join(SRC, f'{kind}_{i}.png')
        if not os.path.exists(p):
            print(f'MISSING {kind}_{i}'); continue
        im = Image.open(p).convert('RGBA')
        if im.size != (cw, ch):
            im = im.resize((cw, ch), Image.LANCZOS)
        # Fill the cell with actual content. Blender leaves headroom, and it
        # varies per stage (low_0 filled 63% of its height, low_6 filled 100%),
        # so obstacles drew both too small AND inconsistently sized between
        # stages while collision still used the full rect. Crop to the content
        # bbox, scale to fit, and bottom-anchor so it stays on the floor.
        bb = im.getbbox()
        if bb:
            c = im.crop(bb)
            s = min(cw / c.width, ch / c.height)
            c = c.resize((max(1, int(c.width * s)), max(1, int(c.height * s))), Image.LANCZOS)
            im = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
            im.paste(c, ((cw - c.width) // 2, ch - c.height), c)
        sheet.paste(im, (i * cw, 0))
    b = io.BytesIO()
    sheet.save(b, 'WEBP', quality=86, method=6)
    payload['ob' + kind] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
    print(f'{kind}: {cw*9}x{ch}  {len(b.getvalue())//1024} KB')

idx = os.path.join(ROOT, 'index.html')
src = io.open(idx, encoding='utf-8').read()
# drop any previous obstacle keys so re-running is idempotent
src = re.sub(r'\nob(?:low|gate|wall):"data:image/webp;base64,[^"]*",', '', src)
ins = '\n' + ','.join(f'ob{k[2:]}:"{v}"' for k, v in payload.items()) + ','
assert src.count('var TEXDATA={') == 1
src = src.replace('var TEXDATA={', 'var TEXDATA={' + ins, 1)
io.open(idx, 'w', encoding='utf-8', newline='\n').write(src)
print('index.html now', len(src) // 1024, 'KB')
