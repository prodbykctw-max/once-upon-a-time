import base64, io, json, os, re
from PIL import Image, ImageDraw, ImageFilter

# RPG bosses from AutoSprite, replacing the canvas rectangles in drawBoss().
#   row 0 = HEARTBREAKER "The Groom Who Lied"  (final)
#   row 1 = REVENANT     "The False Suitor"    (earlier stages)
# One row each, FRAMES cells wide, so the draw call is a flat index.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'renders', 'villain_as')
CW, CH = 160, 224          # boss box is 70x96; cells carry crown/train overhang
FRAMES = 6
THRESH = 40
ORDER = ['groom', 'suitor']


def key(im):
    rgb = im.convert('RGB')
    w, h = rgb.size
    SENT = (255, 0, 255)
    for s in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
              (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if rgb.getpixel(s) != SENT:
            ImageDraw.floodfill(rgb, s, SENT, thresh=THRESH)
    px = rgb.load()
    src = im.convert('RGBA').load()
    a = Image.new('L', (w, h), 255)
    ap = a.load()
    for y in range(h):
        for x in range(w):
            r, g, b, al = src[x, y]
            if px[x, y] == SENT or al == 0 or (g > r * 1.25 and g > b * 1.25 and g > 60):
                ap[x, y] = 0
    a = a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
    out = im.convert('RGBA')
    out.putalpha(a)
    return out


spec = json.load(io.open(os.path.join(SRC, 'boss_sheets.json'), encoding='utf-8'))
sheet = Image.new('RGBA', (CW * FRAMES, CH * len(ORDER)), (0, 0, 0, 0))

for ri, name in enumerate(ORDER):
    s = spec[name]
    img = Image.open(os.path.join(SRC, f'{name}_sheet.png')).convert('RGBA')
    fw, fh, cols, n = s['w'], s['h'], s['cols'], s['n']
    cells = []
    for i in range(min(n, FRAMES)):
        cx, cy = (i % cols) * fw, (i // cols) * fh
        cells.append(key(img.crop((cx, cy, cx + fw, cy + fh))))
    boxes = [c.getbbox() for c in cells if c.getbbox()]
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
    uw, uh = x1 - x0, y1 - y0
    sc = min(CW / uw, CH / uh)
    for i in range(FRAMES):
        c = cells[i % len(cells)].crop((x0, y0, x1, y1))
        c = c.resize((max(1, int(uw * sc)), max(1, int(uh * sc))), Image.LANCZOS)
        sheet.paste(c, (i * CW + (CW - c.width) // 2, ri * CH + (CH - c.height)), c)
    print(f'{name}: {n} src frames -> row {ri}')

sheet.save(os.path.join(SRC, 'boss_sheet.png'))
b = io.BytesIO()
sheet.save(b, 'WEBP', quality=88, method=6)
payload = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
print(f'boss {sheet.width}x{sheet.height} -> {len(b.getvalue())//1024} KB')

idx = os.path.join(ROOT, 'index.html')
s = io.open(idx, encoding='utf-8').read()
s = re.sub(r'\nboss:"data:image/webp;base64,[^"]*",', '', s)
assert s.count('var TEXDATA={') == 1
s = s.replace('var TEXDATA={', 'var TEXDATA={\nboss:"' + payload + '",', 1)
io.open(idx, 'w', encoding='utf-8', newline='\n').write(s)
print('index.html now', len(s) // 1024, 'KB')
