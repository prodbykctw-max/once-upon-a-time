import base64, io, os, re
from PIL import Image

# Compose the 16 premium props (rendered 432x960) into the 3456x480 atlas
# (16 cells of 216x480, 0.45 aspect — unchanged so GLWORLD.drawProps u=kind/16
# still lands) and swap the live GLWDATA.props WebP data-URI in index.html.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'renders', 'outprops_hq')
CW, CH, N = 216, 480, 16

atlas = Image.new('RGBA', (CW * N, CH), (0, 0, 0, 0))
missing = []
for i in range(N):
    p = os.path.join(SRC, f'prop_{i}.png')
    if not os.path.exists(p):
        missing.append(i); continue
    im = Image.open(p).convert('RGBA')
    if im.size != (CW, CH):
        im = im.resize((CW, CH), Image.LANCZOS)
    atlas.paste(im, (i * CW, 0), im)
if missing:
    print('MISSING cells:', missing); raise SystemExit(1)

# client contact sheet (per QA gate) — atlas on a mid grey so alpha reads
os.makedirs(os.path.join(ROOT, 'assets_whimsy'), exist_ok=True)
atlas.save(os.path.join(ROOT, 'assets_whimsy', 'outprops_new.png'))
contact = Image.new('RGBA', (CW * N, CH), (40, 42, 52, 255))
contact.alpha_composite(atlas)
contact.convert('RGB').save(os.path.join(SRC, '_contact16.png'))

# encode WebP (alpha) — keep the single-file payload small
b = io.BytesIO()
atlas.save(b, 'WEBP', quality=90, method=6)
kb = len(b.getvalue()) // 1024
payload = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
print(f'atlas {CW*N}x{CH}  WebP {kb} KB')

idx = os.path.join(ROOT, 'index.html')
s = io.open(idx, encoding='utf-8').read()
# swap the LIVE atlas: props:"data:image/webp;base64,...."  (double-quoted)
m = re.search(r'props:"data:image/webp;base64,[A-Za-z0-9+/=]+"', s)
assert m, 'live props webp atlas not found'
s = s[:m.start()] + 'props:"' + payload + '"' + s[m.end():]
io.open(idx, 'w', encoding='utf-8', newline='\n').write(s)
print(f'swapped; index.html now {len(s)//1024} KB')
