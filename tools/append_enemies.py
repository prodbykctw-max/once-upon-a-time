"""Append one or more new 6-frame enemy walks to the TEX.foes atlas.

Each SHEET is an AutoSprite spritesheet (152x152 frames, 3 cols x 2 rows = 6).
Frames are keyed transparent, fit to the engine's 136x152 cell (feet-anchored,
facing right), and appended as the next tp index(es). Draw picks frame + tp*6.
"""
import io, os, re, hashlib, sys
from PIL import Image, ImageDraw, ImageFilter

ROOT = r"C:\Users\Owner\Documents\once-upon-a-time"
WEB = os.path.join(ROOT, 'web')
IDX = os.path.join(ROOT, 'index.html')
ED = os.path.join(ROOT, 'assets', 'renders', 'proto', 'enemies')
CW, CH = 136, 152

# ordered list of new enemy sheets to append (tp index = 3 + position)
SHEETS = [os.path.join(ED, n) for n in sys.argv[1:]] or [
    os.path.join(ED, 'wisp_idle_sheet.png'),
    os.path.join(ED, 'wraith_idle_sheet.png'),
]


def key_bg(im):
    if im.mode == 'RGBA' and im.split()[3].getextrema()[0] < 250:
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
    cell.paste(im, ((CW-im.width)//2, CH-im.height), im)
    return cell


def strip_of(path):
    sh = Image.open(path).convert('RGBA')
    st = Image.new('RGBA', (CW*6, CH), (0, 0, 0, 0))
    for i in range(6):
        r, c = i // 3, i % 3
        st.alpha_composite(fit_cell(key_bg(sh.crop((c*152, r*152, (c+1)*152, (r+1)*152)))), (i*CW, 0))
    return st


s = io.open(IDX, encoding='utf-8').read()
m = re.search(r"foes:'web/([0-9a-f]{12}\.\w+)'", s) or re.search(r'foes:"web/([0-9a-f]{12}\.\w+)"', s)
assert m, 'foes ref not found'
fn = m.group(1)
atlas = Image.open(os.path.join(WEB, fn)).convert('RGBA')
tp_old = atlas.width // CW // 6
strips = [strip_of(p) for p in SHEETS]
new = Image.new('RGBA', (atlas.width + CW*6*len(strips), CH), (0, 0, 0, 0))
new.alpha_composite(atlas, (0, 0))
for i, st in enumerate(strips):
    new.alpha_composite(st, (atlas.width + i*CW*6, 0))
# preview of the appended types
prev = Image.new('RGBA', (CW*6*len(strips), CH), (58, 60, 72, 255))
for i, st in enumerate(strips):
    prev.alpha_composite(st, (i*CW*6, 0))
prev.convert('RGB').save(os.path.join(ED, '_appended_cells.png'))

b = io.BytesIO(); new.save(b, 'WEBP', quality=92, method=6); raw = b.getvalue()
newfn = hashlib.sha1(raw).hexdigest()[:12] + '.webp'
open(os.path.join(WEB, newfn), 'wb').write(raw)
s = s.replace("foes:'web/" + fn + "'", "foes:'web/" + newfn + "'").replace('foes:"web/' + fn + '"', 'foes:"web/' + newfn + '"')
if newfn != fn and os.path.exists(os.path.join(WEB, fn)):
    os.remove(os.path.join(WEB, fn))
io.open(IDX, 'w', encoding='utf-8', newline='\n').write(s)
print(f'foes atlas: {tp_old} -> {new.width//CW//6} types ({new.width}x{CH}); appended {len(strips)}; {fn} -> {newfn} ({len(raw)//1024}KB)')
