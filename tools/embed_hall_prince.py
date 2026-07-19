import base64, io, os, re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REN = os.path.join(ROOT, 'assets', 'renders')

def b64(im, fmt='WEBP', **kw):
    b = io.BytesIO(); im.save(b, fmt, **kw)
    mime = 'webp' if fmt == 'WEBP' else 'jpeg'
    print(f'  {len(b.getvalue())//1024} KB')
    return f'data:image/{mime};base64,' + base64.b64encode(b.getvalue()).decode()

print('hall wall'); wall = b64(Image.open(os.path.join(REN, 'hall', 'wall.png')).convert('RGB').resize((256, 256), Image.LANCZOS), 'JPEG', quality=84)
print('hall ceil'); ceil = b64(Image.open(os.path.join(REN, 'hall', 'ceil.png')).convert('RGB').resize((256, 256), Image.LANCZOS), 'JPEG', quality=84)

# prince: 3 frames of 384x480 in one row
PW, PH = 384, 480
sheet = Image.new('RGBA', (PW * 3, PH), (0, 0, 0, 0))
for f in range(3):
    p = os.path.join(REN, 'prince', f'prince_{f}.png')
    if not os.path.exists(p): print('MISSING prince', f); continue
    sheet.paste(Image.open(p).convert('RGBA'), (f * PW, 0))
print('prince'); prince = b64(sheet, 'WEBP', quality=88, method=6)

idx = os.path.join(ROOT, 'index.html')
src = io.open(idx, encoding='utf-8').read()

# Re-sync the inlined GL engine from its source file. The inlined copy runs
# from `var GLWORLD=(...)` up to the hero light-wrap helper that follows it.
engine = io.open(os.path.join(ROOT, 'tools', 'glworld_engine.js'), encoding='utf-8').read()
START, END = 'var GLWORLD=(function(){', '// ── world light-wrap for the hero'
a, b = src.index(START), src.index(END)
assert a < b, 'engine anchors out of order'
body = engine[engine.index(START):]
src = src[:a] + body + '\n' + src[b:]
print(f'engine re-synced ({len(body)//1024} KB)')

# GLWDATA gains wall/ceil (idempotent: strip any previous pair first)
src = re.sub(r',wall:"[^"]*",ceil:"[^"]*"', '', src)
m = re.search(r'(var GLWDATA=\{grounds:\[.*?\],props:"[^"]*")(\};)', src, re.S)
assert m, 'GLWDATA not found'
src = src[:m.end(1)] + f',wall:"{wall}",ceil:"{ceil}"' + src[m.start(2):]

# TEXDATA gains prince
src = re.sub(r'\nprince:"data:image/webp;base64,[^"]*",', '', src)
assert src.count('var TEXDATA={') == 1
src = src.replace('var TEXDATA={', 'var TEXDATA={\nprince:"' + prince + '",', 1)

io.open(idx, 'w', encoding='utf-8', newline='\n').write(src)
print('index.html now', len(src) // 1024, 'KB')
