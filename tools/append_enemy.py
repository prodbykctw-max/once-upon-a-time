"""Append a new 6-frame enemy walk to the TEX.foes atlas as the next tp index.

Foes atlas: horizontal strip, 136x152 cells, N types x 6 frames. Draw picks
cell frame + tp*6. Current = 18 cells (tp 0/1/2). This appends 6 cells (tp 3).
Source = an AutoSprite walk sheet (152x152, 3 cols x 2 rows). Each frame is
keyed transparent, fit to the 136x152 cell (feet-anchored, facing right).
"""
import io, os, re, hashlib
from PIL import Image, ImageDraw, ImageFilter

ROOT = r"C:\Users\Owner\Documents\once-upon-a-time"
WEB = os.path.join(ROOT, 'web')
IDX = os.path.join(ROOT, 'index.html')
SHEET = os.path.join(ROOT, 'assets', 'renders', 'proto', 'enemies', 'bramble_walk_sheet.png')
CW, CH = 136, 152

sheet = Image.open(SHEET).convert('RGBA')
frames = []
for i in range(6):
    r, c = i // 3, i % 3
    frames.append(sheet.crop((c*152, r*152, (c+1)*152, (r+1)*152)))


def key_bg(im):
    """The AutoSprite sheet already has alpha; but flatten any near-solid backdrop
    the removeBg left. Border flood-fill from the corners on the RGB copy."""
    if im.mode == 'RGBA':
        a = im.split()[3]
        if a.getextrema()[0] < 250:   # already has real transparency
            return im
    rgb = im.convert('RGB'); w, h = rgb.size; SENT = (255, 0, 255)
    for s in [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, 0), (0, h//2), (w-1, h//2)]:
        if rgb.getpixel(s) != SENT:
            ImageDraw.floodfill(rgb, s, SENT, thresh=40)
    px = rgb.load(); al = Image.new('L', (w, h), 255); ap = al.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == SENT:
                ap[x, y] = 0
    al = al.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.5))
    out = im.convert('RGBA'); out.putalpha(al); return out


def fit_cell(im):
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    sc = min(CW / im.width, (CH*0.98) / im.height)
    im = im.resize((max(1, int(im.width*sc)), max(1, int(im.height*sc))), Image.LANCZOS)
    cell = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    cell.paste(im, ((CW-im.width)//2, CH-im.height), im)   # feet at cell bottom
    return cell


strip = Image.new('RGBA', (CW*6, CH), (0, 0, 0, 0))
for i, f in enumerate(frames):
    strip.alpha_composite(fit_cell(key_bg(f)), (i*CW, 0))

# preview
bg = Image.new('RGBA', strip.size, (58, 60, 72, 255)); bg.alpha_composite(strip)
bg.convert('RGB').save(os.path.join(ROOT, 'assets', 'renders', 'proto', 'enemies', '_bramble_cells.png'))

# append to the live foes atlas
s = io.open(IDX, encoding='utf-8').read()
m = re.search(r"foes:'web/([0-9a-f]{12}\.\w+)'", s) or re.search(r'foes:"web/([0-9a-f]{12}\.\w+)"', s)
assert m, 'foes ref not found'
fn = m.group(1)
atlas = Image.open(os.path.join(WEB, fn)).convert('RGBA')
assert atlas.height == CH, f'atlas height {atlas.height}'
tp_old = atlas.width // CW // 6
new = Image.new('RGBA', (atlas.width + CW*6, CH), (0, 0, 0, 0))
new.alpha_composite(atlas, (0, 0))
new.alpha_composite(strip, (atlas.width, 0))
b = io.BytesIO(); new.save(b, 'WEBP', quality=92, method=6); raw = b.getvalue()
newfn = hashlib.sha1(raw).hexdigest()[:12] + '.webp'
open(os.path.join(WEB, newfn), 'wb').write(raw)
s = s.replace("foes:'web/" + fn + "'", "foes:'web/" + newfn + "'").replace('foes:"web/' + fn + '"', 'foes:"web/' + newfn + '"')
if newfn != fn and os.path.exists(os.path.join(WEB, fn)):
    os.remove(os.path.join(WEB, fn))
io.open(IDX, 'w', encoding='utf-8', newline='\n').write(s)
print(f'foes atlas: {tp_old} types -> {new.width//CW//6} types ({new.width}x{CH}); {fn} -> {newfn} ({len(raw)//1024}KB)')
