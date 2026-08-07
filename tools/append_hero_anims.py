"""Recompose AutoSprite hero animations into the engine's hero-sheet format and
wire them into SPRITES.

Engine format: horizontal strip, transparent, ch=154, N evenly-spaced cw-wide
cells, facing right. SPRITES.<name>={frames:N,cw:CW,ch:154,src:'web/<hash>.png'}.

Each ANIMS entry: (name, sheet_png, frameW, frameH, cols, count). Frames are
bbox-cropped, scaled to 154 tall (feet-anchored), padded to a common cw.
"""
import io, os, re, hashlib, json, sys
from PIL import Image

ROOT = r"C:\Users\Owner\Documents\once-upon-a-time"
WEB = os.path.join(ROOT, 'web')
IDX = os.path.join(ROOT, 'index.html')
ED = os.path.join(ROOT, 'assets', 'renders', 'proto', 'hero')
CH = 154

# filled from get_spritesheet metadata; passed as a JSON arg
ANIMS = json.loads(sys.argv[1]) if len(sys.argv) > 1 else []
# [{"name":"refrain","file":"refrain.png","fw":180,"fh":240,"cols":3,"count":6}, ...]

s = io.open(IDX, encoding='utf-8').read()
entries = []
for a in ANIMS:
    sh = Image.open(os.path.join(ED, a['file'])).convert('RGBA')
    fw, fh, cols, count = a['fw'], a['fh'], a['cols'], a['count']
    frames = []
    for i in range(count):
        r, c = i // cols, i % cols
        f = sh.crop((c*fw, r*fh, (c+1)*fw, (r+1)*fh))
        bb = f.getbbox()
        if bb:
            f = f.crop(bb)
        sc = (CH*0.99) / f.height
        f = f.resize((max(1, int(f.width*sc)), max(1, int(f.height*sc))), Image.LANCZOS)
        frames.append(f)
    cw = max(f.width for f in frames) + 4
    strip = Image.new('RGBA', (cw*count, CH), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.paste(f, (i*cw + (cw-f.width)//2, CH-f.height), f)
    # preview
    prev = Image.new('RGBA', strip.size, (58, 60, 72, 255)); prev.alpha_composite(strip)
    prev.convert('RGB').save(os.path.join(ED, '_%s_cells.png' % a['name']))
    b = io.BytesIO(); strip.save(b, 'PNG'); raw = b.getvalue()
    h = hashlib.sha1(raw).hexdigest()[:12] + '.png'
    open(os.path.join(WEB, h), 'wb').write(raw)
    entries.append((a['name'], count, cw, h))
    print(f"{a['name']}: {count} frames, cw{cw}, {len(raw)//1024}KB -> web/{h}")

# splice the new SPRITES entries in, right after the 'dance' entry
for name, count, cw, h in entries:
    ent = "%s:{frames:%d,cw:%d,ch:154,src:'web/%s'}" % (name, count, cw, h)
    if re.search(name + r':\{frames:', s):   # already present -> replace
        s = re.sub(name + r":\{frames:\d+,cw:\d+,ch:154,src:'web/[0-9a-f]{12}\.png'\}", ent, s)
    else:
        s = re.sub(r"(dance:\{frames:\d+,cw:\d+,ch:154,src:'web/[0-9a-f]{12}\.png'\})",
                   r"\1,\n  " + ent, s, count=1)
io.open(IDX, 'w', encoding='utf-8', newline='\n').write(s)
print('SPRITES updated:', [e[0] for e in entries])
