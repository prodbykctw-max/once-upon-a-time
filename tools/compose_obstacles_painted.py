import base64, io, os, re
from PIL import Image, ImageDraw, ImageFilter

ROOT = r"C:\Users\Owner\Documents\once-upon-a-time"
PROTO = os.path.join(ROOT, 'assets', 'renders', 'proto')

# obstacle sheets: 9 cells (one per stage ai). Replace cell 0 (library) with the
# painted table (gate/slide-under), bookcase (wall/full-block), books (low/jump).
SHEETS = {
    'oblow':  (256, 96,  'ob_books.png',    0.98),
    'obgate': (256, 192, 'ob_table.png',    0.96),
    'obwall': (256, 224, 'ob_bookcase.png', 0.99),
}


def whitekey(im, thresh=36):
    rgb = im.convert('RGB'); w, h = rgb.size; SENT = (255, 0, 255)
    for s in [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, 0), (w//2, h-1), (0, h//2), (w-1, h//2)]:
        if rgb.getpixel(s) != SENT:
            ImageDraw.floodfill(rgb, s, SENT, thresh=thresh)
    px0 = rgb.load()
    for gy in range(12, h, 22):                    # enclosed pure-white pockets
        for gx in range(12, w, 22):
            p = px0[gx, gy]
            if p != SENT and p[0] > 247 and p[1] > 247 and p[2] > 247:
                ImageDraw.floodfill(rgb, (gx, gy), SENT, thresh=14)
    a = Image.new('L', (w, h), 255); ap = a.load()
    for y in range(h):
        for x in range(w):
            if px0[x, y] == SENT:
                ap[x, y] = 0
    a = a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    out = im.copy(); out.putalpha(a); return out


def fit_cell(im, cw, ch, hf):
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    th = int(ch*hf); sc = min(th/im.height, cw/im.width)
    im = im.resize((max(1, int(im.width*sc)), max(1, int(im.height*sc))), Image.LANCZOS)
    cell = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    cell.paste(im, ((cw-im.width)//2, ch-im.height), im)   # bottom-anchor
    return cell


idx = os.path.join(ROOT, 'index.html')
s = io.open(idx, encoding='utf-8').read()

for key, (cw, ch, fname, hf) in SHEETS.items():
    m = re.search(key + r':"data:image/webp;base64,([A-Za-z0-9+/=]+)"', s)
    assert m, key + ' not found'
    sheet = Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGBA')
    painted = fit_cell(whitekey(Image.open(os.path.join(PROTO, fname)).convert('RGBA')), cw, ch, hf)
    sheet.paste(Image.new('RGBA', (cw, ch), (0, 0, 0, 0)), (0, 0))   # clear cell 0
    sheet.paste(painted, (0, 0), painted)
    b = io.BytesIO(); sheet.save(b, 'WEBP', quality=90, method=6)
    payload = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
    s = s[:m.start()] + key + ':"' + payload + '"' + s[m.end():]
    print(f'{key}: cell0 painted, {len(b.getvalue())//1024}KB')

io.open(idx, 'w', encoding='utf-8', newline='\n').write(s)
print('index.html now', len(s)//1024, 'KB')
