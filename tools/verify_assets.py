import base64, io, os, re, sys
from PIL import Image

# Regression guard: every asset baked into index.html is re-encoded here from
# its source on disk using the SAME parameters the embed script used, then
# compared byte-for-byte. A mismatch means a render happened but its embed
# step never ran (or ran before a later re-render) -- the exact failure mode
# that leaves an old stage loading in-game.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REN = os.path.join(ROOT, 'assets', 'renders')
src = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()

GNAMES = ['library', 'meadow', 'blossom', 'rose', 'lake', 'glade', 'sunflower', 'clouds', 'sunset']


def enc(path, mode, size, fmt, **kw):
    if not os.path.exists(path):
        return None
    im = Image.open(path).convert(mode)
    if size:
        im = im.resize(size, Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, fmt, **kw)
    return base64.b64encode(b.getvalue()).decode()


def embedded(key, quoted='"'):
    # The lookbehind matters: 'obwall:"data:..."' CONTAINS 'wall:"data:..."',
    # so without it the hall wall gets compared against the obstacle sheet and
    # reports a phantom regression.
    m = re.search(r'(?<![A-Za-z0-9_])' + re.escape(key) + r':' + quoted +
                  r'data:image/[a-z]+;base64,([^' + quoted + r']*)' + quoted, src)
    return m.group(1) if m else None


def grounds_embedded():
    m = re.search(r'var GLWDATA=\{grounds:\[(.*?)\],props:', src, re.S)
    if not m:
        return []
    return re.findall(r'data:image/[a-z]+;base64,([^"\']*)', m.group(1))


rows = []


def check(label, want, have):
    if want is None:
        rows.append(('NO SOURCE', label)); return
    if have is None:
        rows.append(('NOT EMBEDDED', label)); return
    rows.append(('current' if want == have else 'STALE', label))


ge = grounds_embedded()
for i, n in enumerate(GNAMES):
    want = enc(os.path.join(REN, 'ground', f'g{i}_{n}.png'), 'RGB', (256, 256), 'JPEG', quality=82)
    check(f'ground[{i}] {n}', want, ge[i] if i < len(ge) else None)

check('GLWDATA.props', enc(os.path.join(REN, 'sheet_outprops.png'), 'RGBA', None, 'WEBP', quality=80, method=6),
      embedded('props'))
check('GLWDATA.wall', enc(os.path.join(REN, 'hall', 'wall.png'), 'RGB', (256, 256), 'JPEG', quality=84),
      embedded('wall'))
check('GLWDATA.ceil', enc(os.path.join(REN, 'hall', 'ceil.png'), 'RGB', (256, 256), 'JPEG', quality=84),
      embedded('ceil'))

VA = os.path.join(REN, 'villain_as')
check('TEXDATA.foes', enc(os.path.join(VA, 'foes_sheet.png'), 'RGBA', None, 'WEBP', quality=88, method=6),
      embedded('foes', "'") or embedded('foes'))
check('TEXDATA.boss', enc(os.path.join(VA, 'boss_sheet.png'), 'RGBA', None, 'WEBP', quality=88, method=6),
      embedded('boss'))
# chaser: the ORIGINAL purple Groom's Shadow is the shipping art. The
# AutoSprite black-tailcoat version lives on in villain_as/chaser_sheet.png
# but was reverted at request -- point the check at what actually ships.
check('TEXDATA.chaser',
      enc(os.path.join(REN, 'chaser', 'chaser_sheet_purple.png'), 'RGBA', None, 'WEBP', quality=88, method=6),
      embedded('chaser', "'") or embedded('chaser'))

# prince: three 384x480 frames laid in one row
PW, PH = 384, 480
sheet = Image.new('RGBA', (PW * 3, PH), (0, 0, 0, 0))
ok = True
for f in range(3):
    p = os.path.join(REN, 'prince', f'prince_{f}.png')
    if not os.path.exists(p):
        ok = False; break
    sheet.paste(Image.open(p).convert('RGBA'), (f * PW, 0))
want = None
if ok:
    b = io.BytesIO(); sheet.save(b, 'WEBP', quality=88, method=6)
    want = base64.b64encode(b.getvalue()).decode()
check('TEXDATA.prince', want, embedded('prince'))

# obstacle sheets
for kind, (cw, ch) in {'low': (256, 96), 'gate': (256, 192), 'wall': (256, 224)}.items():
    s = Image.new('RGBA', (cw * 9, ch), (0, 0, 0, 0))
    good = True
    for i in range(9):
        p = os.path.join(REN, 'obstacles', f'{kind}_{i}.png')
        if not os.path.exists(p):
            good = False; break
        im = Image.open(p).convert('RGBA')
        if im.size != (cw, ch):
            im = im.resize((cw, ch), Image.LANCZOS)
        # must mirror embed_obstacles.py's content normalisation exactly, or
        # this reports a phantom regression on every correctly-built sheet
        bb = im.getbbox()
        if bb:
            c = im.crop(bb)
            k = min(cw / c.width, ch / c.height)
            c = c.resize((max(1, int(c.width * k)), max(1, int(c.height * k))), Image.LANCZOS)
            im = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
            im.paste(c, ((cw - c.width) // 2, ch - c.height), c)
        s.paste(im, (i * cw, 0))
    w = None
    if good:
        b = io.BytesIO(); s.save(b, 'WEBP', quality=86, method=6)
        w = base64.b64encode(b.getvalue()).decode()
    check(f'TEXDATA.ob{kind}', w, embedded('ob' + kind))

bad = 0
for status, label in rows:
    if status != 'current':
        bad += 1
    print(f'  {status:14s} {label}')
print(f'\n{len(rows)-bad}/{len(rows)} current' + ('  <-- RE-EMBED NEEDED' if bad else '  (no regressions)'))
sys.exit(1 if bad else 0)
