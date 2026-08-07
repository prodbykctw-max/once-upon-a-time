import base64, io, json, os, re, sys
from PIL import Image, ImageDraw, ImageFilter

# RPG villains from AutoSprite, replacing the Blender primitive foes.
#   tp0 Thorn Goblin (ground stalker) · tp1 Cursed Raven (diver)
#   tp2 Nightshade Sprite (hovering hexer)
# The side-scroller draws them in profile, so these use the facing-right
# sidescroller/custom cycles rather than the toward-camera iso set the Temple
# View chaser needs.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'renders', 'villain_as')
CW, CH = 136, 152
FRAMES = 6                     # per villain; engine cycles %FRAMES
THRESH = 40

# filename -> (frame_w, frame_h, cols, count) written by fetch_foe_sheets
SPEC = os.path.join(SRC, 'foe_sheets.json')


def key(im):
    """Border flood-fill for the backdrop + green-dominance for chroma residue
    caught in enclosed gaps (wing tears, thorn gaps) the fill can't reach."""
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


spec = json.load(io.open(SPEC, encoding='utf-8'))
order = ['goblin', 'raven', 'sprite']
sheet = Image.new('RGBA', (CW * FRAMES * len(order), CH), (0, 0, 0, 0))

for ti, name in enumerate(order):
    s = spec[name]
    img = Image.open(os.path.join(SRC, f'{name}_sheet.png')).convert('RGBA')
    fw, fh, cols, n = s['w'], s['h'], s['cols'], s['n']
    cells = []
    for i in range(min(n, FRAMES)):
        cx, cy = (i % cols) * fw, (i // cols) * fh
        cells.append(key(img.crop((cx, cy, cx + fw, cy + fh))))
    # shared bbox + scale across the cycle, else the foe pulses as it animates
    boxes = [c.getbbox() for c in cells if c.getbbox()]
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
    uw, uh = x1 - x0, y1 - y0
    sc = min(CW / uw, CH / uh)
    for i in range(FRAMES):
        c = cells[i % len(cells)].crop((x0, y0, x1, y1))
        c = c.resize((max(1, int(uw * sc)), max(1, int(uh * sc))), Image.LANCZOS)
        dx = (ti * FRAMES + i) * CW + (CW - c.width) // 2
        sheet.paste(c, (dx, CH - c.height), c)
    print(f'{name}: {n} src frames -> {FRAMES} cells')

sheet.save(os.path.join(SRC, 'foes_sheet.png'))
b = io.BytesIO()
sheet.save(b, 'WEBP', quality=88, method=6)
payload = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
print(f'foes {sheet.width}x{CH} -> {len(b.getvalue())//1024} KB')

idx = os.path.join(ROOT, 'index.html')
s = io.open(idx, encoding='utf-8').read()
m = re.search(r"foes:['\"](data:image/[^'\"]*)['\"]", s)
assert m, 'TEXDATA foes not found'
s = s[:m.start(1)] + payload + s[m.end(1):]
# widen the frame cycle from 3 to FRAMES and match the new cell width
s = s.replace("var ffr=Math.floor(fo2.anim/8)%3+fo2.tp*3;",
              f"var ffr=Math.floor(fo2.anim/7)%{FRAMES}+fo2.tp*{FRAMES};")
s = s.replace("FX.drawImage(TEX.foes,ffr*136,0,136,152,",
              f"FX.drawImage(TEX.foes,ffr*{CW},0,{CW},{CH},")
io.open(idx, 'w', encoding='utf-8', newline='\n').write(s)
print('index.html now', len(s) // 1024, 'KB')
