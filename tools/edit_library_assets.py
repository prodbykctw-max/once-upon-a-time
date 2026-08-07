"""Surgically swap individual atlas cells in the EXTERNAL web/ asset files.

Assets are now external + content-addressed (web/<sha1>.<ext>). To change one
cell we: load the current file the index references, replace just that cell,
re-encode, save under a fresh sha1 name, repoint index.html, and delete the old
file. Other cells (other stages) are untouched.

This round (library polish):
  props  cell 12  -> globe-on-a-table   (globes now sit on tables)
  obgate cell  0  -> table with books   (roll-UNDER = table, books on top)
  oblow  cell  0  -> low book cart       (jump-OVER, replaces the giant stack)
"""
import io, os, re, base64, hashlib
from PIL import Image, ImageDraw, ImageFilter

ROOT = r"C:\Users\Owner\Documents\once-upon-a-time"
WEB = os.path.join(ROOT, 'web')
PROTO = os.path.join(ROOT, 'assets', 'renders', 'proto')
IDX = os.path.join(ROOT, 'index.html')

s = io.open(IDX, encoding='utf-8').read()


def whitekey(im, thresh=36):
    rgb = im.convert('RGB'); w, h = rgb.size; SENT = (255, 0, 255)
    for p in [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, 0), (w//2, h-1), (0, h//2), (w-1, h//2)]:
        if rgb.getpixel(p) != SENT:
            ImageDraw.floodfill(rgb, p, SENT, thresh=thresh)
    px = rgb.load()
    for gy in range(12, h, 22):                    # enclosed pure-white pockets
        for gx in range(12, w, 22):
            q = px[gx, gy]
            if q != SENT and q[0] > 247 and q[1] > 247 and q[2] > 247:
                ImageDraw.floodfill(rgb, (gx, gy), SENT, thresh=14)
    a = Image.new('L', (w, h), 255); ap = a.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == SENT:
                ap[x, y] = 0
    a = a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    out = im.copy(); out.putalpha(a); return out


def fit_cell(im, cw, ch, hf):
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    th = int(ch * hf); sc = min(th/im.height, cw/im.width)
    im = im.resize((max(1, int(im.width*sc)), max(1, int(im.height*sc))), Image.LANCZOS)
    cell = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    cell.paste(im, ((cw-im.width)//2, ch-im.height), im)   # bottom-anchor
    return cell


def cur_ref(key):
    m = re.search(key + r':"web/([0-9a-f]{12}\.\w+)"', s)
    assert m, 'ref not found for ' + key
    return m.group(1)


# key, cell_w, cell_h, cell_index, source_png, height_fraction
EDITS = [
    ('props',  216, 480, 12, 'globe_table.png', 0.84),
    ('obgate', 256, 192, 0,  'lib_table.png',   0.96),
    ('oblow',  256, 96,  0,  'book_cart.png',   0.98),
]

for key, cw, ch, cell, fname, hf in EDITS:
    fn = cur_ref(key)
    atlas = Image.open(os.path.join(WEB, fn)).convert('RGBA')
    assert atlas.height == ch and atlas.width % cw == 0, f'{key} size {atlas.size} vs cell {cw}x{ch}'
    painted = fit_cell(whitekey(Image.open(os.path.join(PROTO, fname)).convert('RGBA')), cw, ch, hf)
    atlas.paste(Image.new('RGBA', (cw, ch), (0, 0, 0, 0)), (cell*cw, 0))   # clear cell
    atlas.alpha_composite(painted, (cell*cw, 0))
    b = io.BytesIO(); atlas.save(b, 'WEBP', quality=90, method=6); raw = b.getvalue()
    newfn = hashlib.sha1(raw).hexdigest()[:12] + '.webp'
    open(os.path.join(WEB, newfn), 'wb').write(raw)
    s = s.replace('web/' + fn, 'web/' + newfn)
    if newfn != fn and os.path.exists(os.path.join(WEB, fn)):
        os.remove(os.path.join(WEB, fn))
    print(f'{key} cell {cell}: {fn} -> {newfn} ({len(raw)//1024}KB)')

io.open(IDX, 'w', encoding='utf-8', newline='\n').write(s)
print('index.html updated')
