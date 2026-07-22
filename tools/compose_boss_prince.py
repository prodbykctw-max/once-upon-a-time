import base64, io, os, re
from PIL import Image, ImageDraw, ImageFilter

ROOT = r"C:\Users\Owner\Documents\once-upon-a-time"
PROTO = os.path.join(ROOT, 'assets', 'renders', 'proto')

# Draw specs (from the existing sample rects — no JS change):
#   TEX.boss   : cells 160x224, cols=frames(4), rows=type(HEARTBREAKER,REVENANT)
#   TEX.prince : cells 384x480, 3 frames in a row
BOSS_CW, BOSS_CH, BOSS_COLS, BOSS_ROWS = 160, 224, 4, 2
PR_CW, PR_CH, PR_FR = 384, 480, 3


def whitekey(im, thresh=36):
    rgb = im.convert('RGB'); w, h = rgb.size; SENT = (255, 0, 255)
    for s in [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, 0), (w//2, h-1), (0, h//2), (w-1, h//2)]:
        if rgb.getpixel(s) != SENT:
            ImageDraw.floodfill(rgb, s, SENT, thresh=thresh)
    px = rgb.load(); a = Image.new('L', (w, h), 255); ap = a.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == SENT:
                ap[x, y] = 0
    a = a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    out = im.copy(); out.putalpha(a); return out


def fit(im, cw, ch, hfrac=0.98):
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    th = int(ch * hfrac); sc = min(th/im.height, cw/im.width)
    im = im.resize((max(1, int(im.width*sc)), max(1, int(im.height*sc))), Image.LANCZOS)
    cell = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    cell.paste(im, ((cw-im.width)//2, ch-im.height), im)   # bottom-anchor
    return cell


def swap(s, key, payload):
    m = re.search(key + r':"data:image/webp;base64,[A-Za-z0-9+/=]+"', s)
    assert m, key + ' not found'
    return s[:m.start()] + key + ':"' + payload + '"' + s[m.end():]


def webp(img):
    b = io.BytesIO(); img.save(b, 'WEBP', quality=90, method=6)
    return len(b.getvalue())//1024, 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()


# ── boss: groom fills both type-rows x 4 frames (static art, canvas fx animate)
groom = fit(whitekey(Image.open(os.path.join(PROTO, 'as_boss.png')).convert('RGBA')), BOSS_CW, BOSS_CH, 0.99)
boss = Image.new('RGBA', (BOSS_CW*BOSS_COLS, BOSS_CH*BOSS_ROWS), (0, 0, 0, 0))
for r in range(BOSS_ROWS):
    for c in range(BOSS_COLS):
        boss.paste(groom, (c*BOSS_CW, r*BOSS_CH), groom)
boss.save(os.path.join(PROTO, '_boss_sheet.png'))
bkb, bpay = webp(boss)

# ── prince: painted prince across all 3 frames (arms already open)
pr = fit(whitekey(Image.open(os.path.join(PROTO, 'as_prince.png')).convert('RGBA')), PR_CW, PR_CH, 0.99)
prince = Image.new('RGBA', (PR_CW*PR_FR, PR_CH), (0, 0, 0, 0))
for f in range(PR_FR):
    prince.paste(pr, (f*PR_CW, 0), pr)
prince.save(os.path.join(PROTO, '_prince_sheet.png'))
pkb, ppay = webp(prince)

print(f'boss sheet {boss.size} {bkb}KB | prince sheet {prince.size} {pkb}KB')

idx = os.path.join(ROOT, 'index.html')
s = io.open(idx, encoding='utf-8').read()
s = swap(s, 'boss', bpay)
s = swap(s, 'prince', ppay)
io.open(idx, 'w', encoding='utf-8', newline='\n').write(s)
print('swapped; index.html now', len(s)//1024, 'KB')
