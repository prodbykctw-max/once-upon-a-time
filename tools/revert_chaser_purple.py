import base64, io, os, re
from PIL import Image

# Restore the ORIGINAL purple Groom's Shadow (top hat, pink eyes, cape) as the
# Temple View chaser, replacing the AutoSprite black-tailcoat villain.
# Source frames are already transparent PNGs, so no keying is needed.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'renders', 'chaser')
CW, CH = 176, 224
N = 4

frames = []
for i in range(N):
    p = os.path.join(SRC, f'groom_{i}.png')
    assert os.path.exists(p), 'missing ' + p
    frames.append(Image.open(p).convert('RGBA'))

# shared bbox + scale so he doesn't pulse between frames
boxes = [f.getbbox() for f in frames if f.getbbox()]
x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
uw, uh = x1 - x0, y1 - y0
sc = min(CW / uw, CH / uh)

sheet = Image.new('RGBA', (CW * N, CH), (0, 0, 0, 0))
for i, f in enumerate(frames):
    c = f.crop((x0, y0, x1, y1)).resize((max(1, int(uw * sc)), max(1, int(uh * sc))), Image.LANCZOS)
    sheet.paste(c, (i * CW + (CW - c.width) // 2, CH - c.height), c)

sheet.save(os.path.join(SRC, 'chaser_sheet_purple.png'))
b = io.BytesIO()
sheet.save(b, 'WEBP', quality=88, method=6)
payload = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
print(f'chaser {CW*N}x{CH} ({N} frames) -> {len(b.getvalue())//1024} KB')

idx = os.path.join(ROOT, 'index.html')
s = io.open(idx, encoding='utf-8').read()
m = re.search(r"chaser:['\"](data:image/[^'\"]*)['\"]", s)
assert m, 'TEXDATA chaser not found'
s = s[:m.start(1)] + payload + s[m.end(1):]
# back to the original 4-frame cadence
s = re.sub(r'var chf=Math\.floor\(GS\.tick/\d+\)%\d+;', 'var chf=Math.floor(GS.tick/7)%4;', s)
io.open(idx, 'w', encoding='utf-8', newline='\n').write(s)
print('frames wired: 4 | index.html now', len(s) // 1024, 'KB')
