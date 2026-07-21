#!/usr/bin/env python3
"""
bake_collectibles.py — high-fidelity ("64-bit") animated pixel collectibles.

Renders a spinning, glaring HEART (DEVOTION life pickup) and MUSIC NOTE
(Grace Note collectible) as 8-frame coin-flip sprite sheets. Each shape is
drawn shaded at 3x, downsampled (LANCZOS) for that smooth HD-pixel look,
given a dark outline + a moving specular glare, and flipped horizontally
per frame so it reads as spinning like a coin. Cell 48x48, sheet 384x48.

Music note stays BLUE (the laptop session set RGB blue for contrast on the
pastel rooms) but gains full shading + glare so it still pops.

Outputs into assets_whimsy/: heart_spin.png, note_spin.png + a preview.
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter

CELL   = 48
FRAMES = 8
SS     = 3                    # supersample factor
S      = CELL * SS
OUT    = os.path.join(os.path.dirname(__file__), '..', 'assets_whimsy')

def h(c): return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

# ── palettes ──────────────────────────────────────────────────────────────
HEART = dict(outline=h('3a0a18'), dark=h('9c1030'), mid=h('e11d44'),
             bright=h('ff5470'), hi=h('ffa8bd'), glare=(255, 255, 255))
NOTE  = dict(outline=h('081633'), dark=h('1c46b8'), mid=h('357bff'),
             bright=h('6fb0ff'), hi=h('cfe6ff'), glare=(255, 255, 255))

def heart_mask(dr):
    pts = []
    for d in range(0, 360, 3):
        t = math.radians(d)
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        pts.append((S/2 + x*(S*0.028), S*0.46 - y*(S*0.028)))
    dr.polygon(pts, fill=255)

def note_mask(dr):
    # eighth note: tilted notehead ellipse + stem + flag
    cx, cy, rw, rh = S*0.40, S*0.66, S*0.20, S*0.15
    dr.ellipse([cx-rw, cy-rh, cx+rw, cy+rh], fill=255)      # notehead
    sx = cx + rw*0.72
    dr.rectangle([sx-S*0.035, S*0.24, sx+S*0.035, cy], fill=255)  # stem
    dr.polygon([(sx, S*0.24), (sx+S*0.18, S*0.34),
                (sx+S*0.16, S*0.50), (sx+S*0.03, S*0.40)], fill=255)  # flag

def shaded(mask, pal):
    """Fill a shape mask with top-left lit vertical-ish gradient + specular."""
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    px = img.load()
    mm = mask.load()
    # bounding rows for gradient normalization
    ys = [y for y in range(S) for x in range(S) if mm[x, y]]
    if not ys:
        return img
    y0, y1 = min(ys), max(ys)
    lx, ly = S*0.36, S*0.34          # light origin (upper-left)
    maxd = S*0.85
    for y in range(S):
        for x in range(S):
            if not mm[x, y]:
                continue
            v = (y - y0) / max(1, (y1 - y0))          # 0 top .. 1 bottom
            d = math.hypot(x-lx, y-ly) / maxd          # dist from light
            lit = max(0.0, 1.0 - d*1.05) * (1.0 - v*0.55)
            if lit > 0.72:   c = pal['hi']
            elif lit > 0.48: c = pal['bright']
            elif lit > 0.24: c = pal['mid']
            else:            c = pal['dark']
            px[x, y] = c + (255,)
    return img

def outlined(shape, pal):
    a = shape.split()[3]
    dil = a.filter(ImageFilter.MaxFilter(2*SS+1))
    out = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ol = Image.new('RGBA', (S, S), pal['outline'] + (255,))
    out.paste(ol, (0, 0), dil)
    out.paste(shape, (0, 0), shape)
    return out

def glare(img, pal, phase):
    """Persistent specular dot + a diagonal shine streak that sweeps."""
    a = img.split()[3]
    g = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(g)
    # fixed specular highlight (upper-left)
    dr.ellipse([S*0.30, S*0.26, S*0.44, S*0.40], fill=pal['glare'] + (150,))
    dr.ellipse([S*0.34, S*0.30, S*0.40, S*0.36], fill=pal['glare'] + (230,))
    # sweeping streak
    sx = int(S*0.12 + phase*S*0.7)
    dr.line([(sx, S*0.15), (sx-S*0.18, S*0.9)], fill=pal['glare'] + (120,), width=int(S*0.05))
    g = g.filter(ImageFilter.GaussianBlur(SS*1.1))
    g.putalpha(Image.composite(g.split()[3], Image.new('L', (S, S), 0), a))
    return Image.alpha_composite(img, g)

def build(mask_fn, pal):
    dr_img = Image.new('L', (S, S), 0)
    mask_fn(ImageDraw.Draw(dr_img))
    front = outlined(shaded(dr_img, pal), pal)
    sheet = Image.new('RGBA', (CELL*FRAMES, CELL), (0, 0, 0, 0))
    for i in range(FRAMES):
        ang = i / FRAMES * 2*math.pi
        wf = max(0.14, abs(math.cos(ang)))
        w = max(2, int(S*wf))
        fr = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        sc = front.resize((w, S), Image.LANCZOS)
        fr.paste(sc, ((S-w)//2, 0), sc)
        if wf < 0.34:   # thin edge sliver reads as the spinning side
            ed = ImageDraw.Draw(fr)
            ed.rectangle([S/2-SS*1.5, S*0.28, S/2+SS*1.5, S*0.74],
                         fill=pal['hi'] + (235,))
        fr = glare(fr, pal, i/FRAMES)
        cell = fr.resize((CELL, CELL), Image.LANCZOS)
        sheet.paste(cell, (i*CELL, 0), cell)
    return sheet.quantize(colors=48, method=Image.FASTOCTREE).convert('RGBA')

def main():
    os.makedirs(OUT, exist_ok=True)
    heart = build(heart_mask, HEART)
    note  = build(note_mask,  NOTE)
    heart.save(os.path.join(OUT, 'heart_spin.png'))
    note.save(os.path.join(OUT, 'note_spin.png'))
    # preview contact sheet (4x, dark bg)
    prev = Image.new('RGBA', (CELL*FRAMES*4, CELL*2*4), (24, 12, 34, 255))
    prev.alpha_composite(heart.resize((CELL*FRAMES*4, CELL*4), Image.NEAREST), (0, 0))
    prev.alpha_composite(note.resize((CELL*FRAMES*4, CELL*4), Image.NEAREST), (0, CELL*4))
    prev.save(os.path.join(OUT, 'collectibles_preview.png'))
    print('baked heart_spin.png, note_spin.png (+ preview)')

if __name__ == '__main__':
    main()
