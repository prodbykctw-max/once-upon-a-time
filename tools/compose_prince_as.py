import os
from PIL import Image, ImageDraw, ImageFilter

# Turn the three AutoSprite poses into the game's prince frames.
#
# The generator returns a solid-white backdrop, so the background has to be
# keyed out. A plain "white -> transparent" threshold would also erase his
# white dress shirt and pocket square, so instead we FLOOD FILL inward from the
# four corners: only white that is connected to the border is background, and
# anything enclosed by the figure survives.
#
# Frame order is the distance ramp the finale drives: arms down while she is
# far, half open as she closes, wide open when she arrives.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'renders', 'prince_as')
DST = os.path.join(ROOT, 'assets', 'renders', 'prince')
os.makedirs(DST, exist_ok=True)

FRAMES = ['waiting.png', 'base.png', 'reaching.png']
CW, CH = 384, 480      # cell size expected by embed_hall_prince.py
THRESH = 36            # flood tolerance against the white backdrop


def key_white(im):
    rgb = im.convert('RGB')
    w, h = rgb.size
    SENT = (255, 0, 255)
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
             (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
    for s in seeds:
        if rgb.getpixel(s) != SENT:
            ImageDraw.floodfill(rgb, s, SENT, thresh=THRESH)
    px = rgb.load()
    alpha = Image.new('L', (w, h), 255)
    ap = alpha.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == SENT:
                ap[x, y] = 0
    # pull the edge in a pixel so the white backdrop doesn't fringe, then
    # feather so the silhouette isn't stair-stepped when scaled down
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert('RGBA')
    out.putalpha(alpha)
    return out


for i, fn in enumerate(FRAMES):
    p = os.path.join(SRC, fn)
    if not os.path.exists(p):
        print('MISSING', fn)
        continue
    im = key_white(Image.open(p))
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    # contain within the cell, then bottom-anchor (he stands on the ground)
    sc = min(CW / im.width, CH / im.height)
    im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    cell = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    cell.paste(im, ((CW - im.width) // 2, CH - im.height), im)
    cell.save(os.path.join(DST, f'prince_{i}.png'))
    print(f'prince_{i}.png  <- {fn}  content {im.width}x{im.height}')

print('PRINCE_FRAMES_DONE')
