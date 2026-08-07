"""Compose the 9-villain boss atlas for the RPG.

Each stage has its own boss (atlas row = stage index 0..8). Columns are:
  0..3  idle cycle  (from the boss's `idle` sheet, 4 frames)
  4..8  defeat/collapse (from the boss's `custom` defeat sheet, 5 frames)
Cell = 200x280, feet-anchored, keyed transparent. Atlas = 9 cols x 9 rows.

drawBoss reads: IN=4 idle frames, DN=5 defeat frames, cw=200, ch=280, row=b.bi.

Source sheets are AutoSprite (200x200 frames). Idle: columns=2 (2x2). Defeat:
columns=3 (3x2). Downloaded fresh from signed URLs in tools/boss_urls.json.
"""
import io, os, re, json, hashlib, urllib.request
from PIL import Image, ImageDraw, ImageFilter

ROOT = r"C:\Users\Owner\Documents\once-upon-a-time"
WEB = os.path.join(ROOT, 'web')
IDX = os.path.join(ROOT, 'index.html')
ED = os.path.join(ROOT, 'assets', 'renders', 'proto', 'bosses')
DL = os.path.join(ED, 'sheets'); os.makedirs(DL, exist_ok=True)
CW, CH = 200, 280           # atlas cell
IN, DN = 4, 5               # idle frames, defeat frames
FW = FH = 200               # source frame size

URLS = json.load(io.open(os.path.join(ROOT, 'tools', 'boss_urls.json')))['bosses']


def fetch(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 2000:
        return
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        open(path, 'wb').write(r.read())


def key_bg(im):
    """Flood the flat backdrop to transparent from the border, keep the figure."""
    if im.mode == 'RGBA' and im.split()[3].getextrema()[0] < 250:
        return im
    rgb = im.convert('RGB'); w, h = rgb.size; SENT = (255, 0, 255)
    seeds = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, 0), (0, h//2), (w-1, h//2), (w//2, h-1)]
    for s in seeds:
        if rgb.getpixel(s) != SENT:
            ImageDraw.floodfill(rgb, s, SENT, thresh=42)
    px = rgb.load(); al = Image.new('L', (w, h), 255); ap = al.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == SENT:
                ap[x, y] = 0
    al = al.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    out = im.convert('RGBA'); out.putalpha(al); return out


def cell_of(frame):
    """Key + bbox-crop + scale to fit the 200x280 cell, feet-anchored bottom-centre."""
    f = key_bg(frame)
    bb = f.getbbox()
    if bb:
        f = f.crop(bb)
    sc = min(CW / f.width, (CH * 0.99) / f.height)
    f = f.resize((max(1, int(f.width * sc)), max(1, int(f.height * sc))), Image.LANCZOS)
    cell = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    cell.paste(f, ((CW - f.width) // 2, CH - f.height), f)
    return cell


def frames_from(path, count, cols):
    sh = Image.open(path).convert('RGBA')
    out = []
    for i in range(count):
        r, c = i // cols, i % cols
        out.append(sh.crop((c*FW, r*FH, (c+1)*FW, (r+1)*FH)))
    return out


atlas = Image.new('RGBA', (CW * (IN + DN), CH * 9), (0, 0, 0, 0))
for bo in URLS:
    st, key = bo['st'], bo['key']
    ip = os.path.join(DL, key + '_idle.png'); dp = os.path.join(DL, key + '_death.png')
    fetch(bo['idle'], ip); fetch(bo['death'], dp)
    idle = frames_from(ip, IN, 2)      # idle: 4 frames, 2 cols
    death = frames_from(dp, DN, 3)     # defeat: 5 frames, 3 cols
    for c, fr in enumerate(idle):
        atlas.alpha_composite(cell_of(fr), (c * CW, st * CH))
    for c, fr in enumerate(death):
        atlas.alpha_composite(cell_of(fr), ((IN + c) * CW, st * CH))
    print('row %d %-10s idle=%d death=%d' % (st, key, len(idle), len(death)))

# preview on a slate so transparency reads
prev = Image.new('RGBA', atlas.size, (54, 46, 64, 255)); prev.alpha_composite(atlas)
prev.convert('RGB').save(os.path.join(ED, '_atlas_preview.png'))

b = io.BytesIO(); atlas.save(b, 'WEBP', quality=92, method=6); raw = b.getvalue()
newfn = hashlib.sha1(raw).hexdigest()[:12] + '.webp'
open(os.path.join(WEB, newfn), 'wb').write(raw)

s = io.open(IDX, encoding='utf-8').read()
m = re.search(r'boss:"web/([0-9a-f]{12}\.\w+)"', s) or re.search(r"boss:'web/([0-9a-f]{12}\.\w+)'", s)
assert m, 'boss ref not found'
old = m.group(1)
s = s.replace('boss:"web/' + old + '"', 'boss:"web/' + newfn + '"').replace("boss:'web/" + old + "'", "boss:'web/" + newfn + "'")
io.open(IDX, 'w', encoding='utf-8', newline='\n').write(s)
if newfn != old and os.path.exists(os.path.join(WEB, old)):
    os.remove(os.path.join(WEB, old))
print('atlas %dx%d -> web/%s (%dKB); boss ref %s -> %s' % (atlas.width, atlas.height, newfn, len(raw)//1024, old, newfn))
