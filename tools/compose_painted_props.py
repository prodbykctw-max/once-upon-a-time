import base64, io, os, re, urllib.request
from PIL import Image, ImageDraw, ImageFilter

ROOT = r"C:\Users\Owner\Documents\once-upon-a-time"
PROTO = os.path.join(ROOT, 'assets', 'renders', 'proto')
HQ = os.path.join(ROOT, 'assets', 'renders', 'outprops_hq')
os.makedirs(PROTO, exist_ok=True)
CW, CH, N = 216, 480, 16
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36 Chrome/120'}

# cell -> AutoSprite painted URL (0-11 outdoor). 12-15 fall back to the HQ
# Blender renders (indoor, library-only, low priority — paint later).
URLS = {
    0:  'https://im.runware.ai/image/os/a03d21/ws/4/ii/c0855ee7-bfb8-4e29-8fc5-c31c7fa63158.png',  # door oak
    1:  'https://im.runware.ai/image/os/a05d22/ws/4/ii/adf1cca3-f939-4dcd-83bf-802d6179fd62.png',  # birch
    2:  'https://im.runware.ai/image/os/a07dlim3/ws/4/ii/d2e199db-b645-4f19-bf72-2b8231e1c3b8.png', # blossom
    3:  'https://im.runware.ai/image/os/a08dlim3/ws/4/ii/77dc9730-ce11-4f02-85f7-3bb00501a819.png', # willow
    4:  'https://im.runware.ai/image/os/a01d21/ws/4/ii/77763617-3111-4a13-9609-cf6ef3b1d177.png',  # round oak
    5:  'https://im.runware.ai/image/os/a08dlim3/ws/4/ii/3a169578-86ad-4e58-83b6-5e633ca8b6a8.png', # rose bush
    6:  'https://im.runware.ai/image/os/a08dlim3/ws/4/ii/878ffc64-f7b0-4b4b-8e3e-f27b1987d336.png', # fountain
    7:  'https://im.runware.ai/image/os/a03d21/ws/4/ii/a5196af3-3aef-48f7-9e90-8ebf3fe15283.png',  # angel
    8:  'https://im.runware.ai/image/os/a10dlim3/ws/4/ii/765c79e0-4006-4679-b7ab-1995dd40f56c.png', # glow-flower
    9:  'https://im.runware.ai/image/os/a08dlim3/ws/4/ii/8b6d9a98-c790-4f76-a284-c18228736073.png', # daisies
    10: 'https://im.runware.ai/image/os/a08dlim3/ws/4/ii/d0533ee2-d713-43a4-82cc-b4f61d53927e.png', # swan (statue slot)
    11: 'https://im.runware.ai/image/os/a08dlim3/ws/4/ii/d0533ee2-d713-43a4-82cc-b4f61d53927e.png', # swan (live)
    12: 'https://im.runware.ai/image/os/a10dlim3/ws/4/ii/1dfcf4e7-23c4-422d-9970-ea87eee09977.png', # library globe
    13: 'https://im.runware.ai/image/os/a08dlim3/ws/4/ii/74d636ee-5142-4798-8a51-932457af896a.png', # topiary
    14: 'https://im.runware.ai/image/os/a10dlim3/ws/4/ii/18966173-ca5b-4769-ba99-f146740b2c1e.png', # bunny
    15: 'https://im.runware.ai/image/os/a10dlim3/ws/4/ii/18966173-ca5b-4769-ba99-f146740b2c1e.png', # bunny
}
# target height fraction per cell (brief: tree fills, bush lower third, etc.)
HFRAC = {0:0.96,1:0.97,2:0.95,3:0.95,4:0.96,5:0.58,6:0.80,7:0.82,8:0.72,9:0.72,10:0.70,11:0.46,
         12:0.82,13:0.80,14:0.52,15:0.52}


def dl(url, dest):
    if not (os.path.exists(dest) and os.path.getsize(dest) > 5000):
        with open(dest, 'wb') as f:
            f.write(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read())
    return Image.open(dest).convert('RGBA')


def whitekey(im, thresh=36):
    """Remove the WHITE studio background by border flood-fill, so white parts
    of the prop (marble, swan) that aren't connected to the border survive."""
    rgb = im.convert('RGB')
    w, h = rgb.size
    SENT = (255, 0, 255)
    seeds = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, 0), (w//2, h-1), (0, h//2), (w-1, h//2)]
    for s in seeds:
        if rgb.getpixel(s) != SENT:
            ImageDraw.floodfill(rgb, s, SENT, thresh=thresh)
    px = rgb.load()
    a = Image.new('L', (w, h), 255); ap = a.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == SENT:
                ap[x, y] = 0
    a = a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    out = im.copy(); out.putalpha(a)
    return out


def fit_cell(im, hfrac):
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    target_h = int(CH * hfrac)
    scale = min(target_h / im.height, CW / im.width)
    im = im.resize((max(1, int(im.width*scale)), max(1, int(im.height*scale))), Image.LANCZOS)
    cell = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    cell.paste(im, ((CW - im.width)//2, CH - im.height), im)   # bottom-anchor
    return cell


atlas = Image.new('RGBA', (CW*N, CH), (0, 0, 0, 0))
for i in range(N):
    if i in URLS:
        raw = dl(URLS[i], os.path.join(PROTO, f'painted_{i}.png'))
        cell = fit_cell(whitekey(raw), HFRAC[i])
        print(f'cell {i}: painted')
    else:
        p = os.path.join(HQ, f'prop_{i}.png')
        cell = Image.open(p).convert('RGBA').resize((CW, CH), Image.LANCZOS)
        print(f'cell {i}: HQ fallback (indoor)')
    atlas.paste(cell, (i*CW, 0), cell)

atlas.save(os.path.join(ROOT, 'assets_whimsy', 'outprops_painted.png'))
contact = Image.new('RGBA', (CW*N, CH), (40, 42, 52, 255)); contact.alpha_composite(atlas)
contact.convert('RGB').save(os.path.join(PROTO, '_atlas_painted.png'))
b = io.BytesIO(); atlas.save(b, 'WEBP', quality=90, method=6)
print(f'atlas {CW*N}x{CH}  WebP {len(b.getvalue())//1024} KB')
payload = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

idx = os.path.join(ROOT, 'index.html')
s = io.open(idx, encoding='utf-8').read()
m = re.search(r'props:"data:image/webp;base64,[A-Za-z0-9+/=]+"', s)
assert m, 'live props atlas not found'
s = s[:m.start()] + 'props:"' + payload + '"' + s[m.end():]
io.open(idx, 'w', encoding='utf-8', newline='\n').write(s)
print(f'swapped; index.html now {len(s)//1024} KB')
