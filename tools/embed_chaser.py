import base64, io, os, re, sys
from PIL import Image, ImageDraw, ImageFilter

# The Groom's Shadow chase cycle, from the AutoSprite character.
# Replaces the Blender primitive chaser. Source is an AutoSprite spritesheet
# (one row of square frames); we key the backdrop, crop each frame to content,
# and re-lay them into the game's 176x224 cells.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'renders', 'villain_as', 'shadow_sheet.png')
CW, CH = 176, 224
THRESH = 40


def key_white(im):
    """Knock out the backdrop by flooding inward from the border only, so any
    light detail enclosed by the figure survives."""
    rgb = im.convert('RGB')
    w, h = rgb.size
    SENT = (255, 0, 255)
    for s in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
              (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if rgb.getpixel(s) != SENT:
            ImageDraw.floodfill(rgb, s, SENT, thresh=THRESH)
    px = rgb.load()
    src = im.convert('RGBA').load()
    alpha = Image.new('L', (w, h), 255)
    ap = alpha.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == SENT:
                ap[x, y] = 0
                continue
            # Chroma residue: AutoSprite mattes against green, and green left
            # in ENCLOSED gaps (the tattered coat) is not border-connected, so
            # the flood fill never reaches it. Kill green-dominant pixels too.
            r, g, b, a = src[x, y]
            if a == 0:
                ap[x, y] = 0
            elif g > r * 1.25 and g > b * 1.25 and g > 60:
                ap[x, y] = 0
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
    out = im.convert('RGBA')
    out.putalpha(alpha)
    return out


assert os.path.exists(SRC), 'missing ' + SRC
sheet = Image.open(SRC).convert('RGBA')
sw, sh = sheet.size
# AutoSprite lays frames out as a GRID (columns from the spritesheet record),
# not a single row — read the real geometry rather than inferring from aspect.
FW = int(os.environ.get('FRAME_W', 256))
FH = int(os.environ.get('FRAME_H', 256))
COLS = int(os.environ.get('FRAME_COLS', 3))
N = int(os.environ.get('FRAME_N', 8))
print(f'source {sw}x{sh} -> {N} frames of {FW}x{FH} in {COLS} cols')

def cell(i):
    cx, cy = (i % COLS) * FW, (i // COLS) * FH
    return sheet.crop((cx, cy, cx + FW, cy + FH))

n = N
# Frames must share a common baseline and scale, or he jitters as he runs.
# Key every frame first, measure the union bbox, then apply it to all.
keyed = [key_white(cell(i)) for i in range(n)]
boxes = [k.getbbox() for k in keyed]
boxes = [b for b in boxes if b]
ux0 = min(b[0] for b in boxes); uy0 = min(b[1] for b in boxes)
ux1 = max(b[2] for b in boxes); uy1 = max(b[3] for b in boxes)
uw, uh = ux1 - ux0, uy1 - uy0
sc = min(CW / uw, CH / uh)

out = Image.new('RGBA', (CW * n, CH), (0, 0, 0, 0))
for i, k in enumerate(keyed):
    crop = k.crop((ux0, uy0, ux1, uy1))
    crop = crop.resize((max(1, int(uw * sc)), max(1, int(uh * sc))), Image.LANCZOS)
    out.paste(crop, (i * CW + (CW - crop.width) // 2, CH - crop.height), crop)

png = os.path.join(ROOT, 'assets', 'renders', 'villain_as', 'chaser_sheet.png')
out.save(png)
b = io.BytesIO()
out.save(b, 'WEBP', quality=88, method=6)
payload = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
print(f'chaser {CW*n}x{CH} ({n} frames) -> {len(b.getvalue())//1024} KB')

idx = os.path.join(ROOT, 'index.html')
s = io.open(idx, encoding='utf-8').read()
m = re.search(r"chaser:['\"](data:image/[^'\"]*)['\"]", s)
assert m, 'TEXDATA chaser not found'
s = s[:m.start(1)] + payload + s[m.end(1):]
# keep the frame count in the draw call in step with what we just built
s = s.replace("var chf=Math.floor(GS.tick/7)%4;", f"var chf=Math.floor(GS.tick/5)%{n};")
s = s.replace("FX.drawImage(TEX.chaser,chf*176,0,176,224,",
              "FX.drawImage(TEX.chaser,chf*176,0,176,224,")
io.open(idx, 'w', encoding='utf-8', newline='\n').write(s)
print('frames wired:', n, '| index.html now', len(s) // 1024, 'KB')
