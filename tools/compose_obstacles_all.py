"""Swap the painted stage-1..8 obstacles into cells 1-8 of the external obstacle
atlases (obgate/oblow/obwall). Cell 0 (library) is already painted — left alone.
Surgical per-file: load current web/ atlas, replace cells, save new sha1, repoint
index.html, delete old file.

White-key: aggressive grid-seed (clears enclosed white pockets in lattices/fences)
EXCEPT for the marble/cloud stages (4 lake, 7 clouds) whose bodies are near-white
and would be eaten — those use border-only keying.
"""
import io, os, re, base64, hashlib
from PIL import Image, ImageDraw, ImageFilter

ROOT = r"C:\Users\Owner\Documents\once-upon-a-time"
WEB = os.path.join(ROOT, 'web')
OB = os.path.join(ROOT, 'assets', 'renders', 'proto', 'ob24')
IDX = os.path.join(ROOT, 'index.html')
s = io.open(IDX, encoding='utf-8').read()

WHITE_BODY = {4, 7}   # marble / clouds → border-only key (preserve white)


def whitekey(im, thresh=36, aggressive=True):
    rgb = im.convert('RGB'); w, h = rgb.size; SENT = (255, 0, 255)
    for p in [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, 0), (w//2, h-1), (0, h//2), (w-1, h//2)]:
        if rgb.getpixel(p) != SENT:
            ImageDraw.floodfill(rgb, p, SENT, thresh=thresh)
    if aggressive:
        px = rgb.load()
        for gy in range(12, h, 20):
            for gx in range(12, w, 20):
                q = px[gx, gy]
                if q != SENT and q[0] > 248 and q[1] > 248 and q[2] > 248:
                    ImageDraw.floodfill(rgb, (gx, gy), SENT, thresh=12)
    px = rgb.load(); a = Image.new('L', (w, h), 255); ap = a.load()
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
    cell.paste(im, ((cw-im.width)//2, ch-im.height), im)
    return cell


def cur_ref(key):
    m = re.search(key + r':"web/([0-9a-f]{12}\.\w+)"', s)
    assert m, 'ref not found: ' + key
    return m.group(1)


# key -> (cell_w, cell_h, height_frac, source-type)
SHEETS = {'obgate': (256, 192, 0.98, 'gate'), 'oblow': (256, 96, 0.98, 'low'), 'obwall': (256, 224, 0.99, 'wall')}

for key, (cw, ch, hf, ty) in SHEETS.items():
    fn = cur_ref(key)
    atlas = Image.open(os.path.join(WEB, fn)).convert('RGBA')
    assert atlas.height == ch, f'{key} height {atlas.height} != {ch}'
    for st in range(1, 9):
        src = os.path.join(OB, f's{st}_{ty}.png')
        img = Image.open(src).convert('RGBA')
        painted = fit_cell(whitekey(img, aggressive=(st not in WHITE_BODY)), cw, ch, hf)
        atlas.paste(Image.new('RGBA', (cw, ch), (0, 0, 0, 0)), (st*cw, 0))
        atlas.alpha_composite(painted, (st*cw, 0))
    b = io.BytesIO(); atlas.save(b, 'WEBP', quality=90, method=6); raw = b.getvalue()
    newfn = hashlib.sha1(raw).hexdigest()[:12] + '.webp'
    open(os.path.join(WEB, newfn), 'wb').write(raw)
    s = s.replace('web/' + fn, 'web/' + newfn)
    if newfn != fn and os.path.exists(os.path.join(WEB, fn)):
        os.remove(os.path.join(WEB, fn))
    print(f'{key}: cells 1-8 painted, {fn} -> {newfn} ({len(raw)//1024}KB)')

io.open(IDX, 'w', encoding='utf-8', newline='\n').write(s)
print('index.html updated')
