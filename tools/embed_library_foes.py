import base64, io, os, re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REN = os.path.join(ROOT, 'assets', 'renders')

# ── 1. outprops sheet grows 12 -> 16 cells (library scenery appended) ──
NP, CW, CH = 16, 144, 240
sheet = Image.new('RGBA', (CW * NP, CH), (0, 0, 0, 0))
for i in range(NP):
    p = os.path.join(REN, 'outprops', f'prop_{i}.png')
    if not os.path.exists(p):
        print('MISSING prop', i); continue
    sheet.paste(Image.open(p).convert('RGBA').resize((CW, CH), Image.LANCZOS), (i * CW, 0))
sheet.save(os.path.join(REN, 'sheet_outprops.png'))
b = io.BytesIO(); sheet.save(b, 'WEBP', quality=80, method=6)
props_b64 = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
print(f'outprops {NP} cells -> {len(b.getvalue())//1024} KB')

# ── 2. foes sheet: 3 villains x 3 frames, single row of 136x152 cells ──
FW, FH = 136, 152
foes = Image.new('RGBA', (FW * 9, FH), (0, 0, 0, 0))
for tp in range(3):
    for f in range(3):
        p = os.path.join(REN, 'foes', f'foe_{tp}_{f}.png')
        if not os.path.exists(p):
            print('MISSING foe', tp, f); continue
        foes.paste(Image.open(p).convert('RGBA').resize((FW, FH), Image.LANCZOS), ((tp * 3 + f) * FW, 0))
fb = io.BytesIO(); foes.save(fb, 'WEBP', quality=88, method=6)
foes_b64 = 'data:image/webp;base64,' + base64.b64encode(fb.getvalue()).decode()
print(f'foes 9 cells -> {len(fb.getvalue())//1024} KB')

# ── 3. splice both into index.html ──
idx = os.path.join(ROOT, 'index.html')
src = io.open(idx, encoding='utf-8').read()

# GLWDATA.props: swap just the props value, keep the ground textures
m = re.search(r'(var GLWDATA=\{grounds:\[.*?\],props:")([^"]*)("\};)', src, re.S)
assert m, 'GLWDATA props not found'
src = src[:m.start(2)] + props_b64 + src[m.end(2):]

# TEXDATA.foes: replace the existing value in place (single-quoted in TEXDATA)
m2 = re.search(r"foes:'(data:image/[^']*)'", src)
assert m2, 'TEXDATA foes not found'
src = src[:m2.start(1)] + foes_b64 + src[m2.end(1):]

io.open(idx, 'w', encoding='utf-8', newline='\n').write(src)
print('index.html now', len(src) // 1024, 'KB')
