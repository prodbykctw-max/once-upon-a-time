import base64, io, os, re, sys
from PIL import Image, ImageDraw, ImageFilter

# Jandé's FRONT-facing ending portrait, from the AutoSprite character the
# client created. This replaces the back-turned runner frame the tableau used
# to borrow — she now faces the player as she reaches him.
#
# Same border flood-fill keying as the prince: a plain white threshold would
# eat her ivory gown and train, so only white connected to the frame edge is
# treated as background.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, 'assets', 'renders', 'jande_as')
CW, CH = 320, 400
THRESH = 36


def key_white(im):
    rgb = im.convert('RGB')
    w, h = rgb.size
    SENT = (255, 0, 255)
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
             (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
    for s in seeds:
        if rgb.getpixel(s) != SENT:
            ImageDraw.floodfill(rgb, s, SENT, thresh=THRESH)
    px = rgb.load()
    alpha = Image.new('L', (w, h), 255)
    ap = alpha.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == SENT:
                ap[x, y] = 0
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert('RGBA')
    out.putalpha(alpha)
    return out


# prefer the generated reunion pose; fall back to her base standing shot
src = None
for cand in ('reunion.png', 'base.png'):
    p = os.path.join(SRC_DIR, cand)
    if os.path.exists(p):
        src = p
        break
assert src, 'no Jande source image found in ' + SRC_DIR
print('source:', os.path.basename(src))

im = key_white(Image.open(src))
bbox = im.getbbox()
if bbox:
    im = im.crop(bbox)
sc = min(CW / im.width, CH / im.height)
im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
cell = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
cell.paste(im, ((CW - im.width) // 2, CH - im.height), im)

b = io.BytesIO()
cell.save(b, 'WEBP', quality=90, method=6)
payload = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
print(f'reunion {CW}x{CH} -> {len(b.getvalue())//1024} KB')

idx = os.path.join(ROOT, 'index.html')
s = io.open(idx, encoding='utf-8').read()
s = re.sub(r'\nreunion:"data:image/webp;base64,[^"]*",', '', s)   # idempotent
assert s.count('var TEXDATA={') == 1
s = s.replace('var TEXDATA={', 'var TEXDATA={\nreunion:"' + payload + '",', 1)
io.open(idx, 'w', encoding='utf-8', newline='\n').write(s)
print('index.html now', len(s) // 1024, 'KB')
