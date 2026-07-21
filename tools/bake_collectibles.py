#!/usr/bin/env python3
"""
bake_collectibles.py — 2.5D animated pixel collectibles + HUD life heart.

Client spec (validated):
  BLUE MUSIC NOTE = the collectible grabbed all game long (Grace Note).
  HEART           = lives. Shown as the top-left life counter, AND appears
                    on the stage only as an earned extra-life pickup.
  Everything pixel-art with a BLACK border; when they spin they must stay
  THICK (2.5D) — an extruded side face so an edge-on frame is a chunky slab,
  never a paper-thin sliver.

Outputs (assets_whimsy/):
  note_blue.png   8-frame spin sheet, 48px cells
  heart_spin.png  8-frame spin sheet, 48px cells
  heart_icon.png  single front heart (HUD life counter)
  collectibles_preview.png
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter

CELL, FRAMES, SS = 48, 8, 3
S = CELL * SS
DEPTH = 0.30
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets_whimsy')

def h(c): return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
BLACK = (0, 0, 0)

BLUE  = dict(dark=h('16367e'), mid=h('357bff'), bright=h('6fb0ff'), hi=h('cfe6ff'), side=h('0d1f52'))
HEART = dict(dark=h('9c1030'), mid=h('e11d44'), bright=h('ff5470'), hi=h('ffa8bd'), side=h('5a0a1e'))

def note_mask(dr):
    cx, cy, rw, rh = S*0.40, S*0.66, S*0.205, S*0.155
    dr.ellipse([cx-rw, cy-rh, cx+rw, cy+rh], fill=255)
    sx = cx + rw*0.74
    dr.rectangle([sx-S*0.04, S*0.22, sx+S*0.04, cy], fill=255)
    dr.polygon([(sx, S*0.22), (sx+S*0.19, S*0.33), (sx+S*0.17, S*0.50), (sx+S*0.02, S*0.40)], fill=255)

def heart_mask(dr):
    pts = []
    for d in range(0, 360, 3):
        t = math.radians(d)
        x = 16*math.sin(t)**3
        y = 13*math.cos(t) - 5*math.cos(2*t) - 2*math.cos(3*t) - math.cos(4*t)
        pts.append((S/2 + x*(S*0.027), S*0.44 - y*(S*0.027)))
    dr.polygon(pts, fill=255)

def shaded(mask, pal):
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0)); px = img.load(); mm = mask.load()
    ys = [y for y in range(S) for x in range(S) if mm[x, y]]
    if not ys: return img
    y0, y1 = min(ys), max(ys); lx, ly = S*0.36, S*0.32; maxd = S*0.8
    for y in range(S):
        for x in range(S):
            if not mm[x, y]: continue
            v = (y-y0)/max(1, y1-y0); d = math.hypot(x-lx, y-ly)/maxd
            lit = max(0.0, 1.0-d*1.05)*(1.0-v*0.5)
            c = pal['hi'] if lit > 0.72 else pal['bright'] if lit > 0.46 else pal['mid'] if lit > 0.22 else pal['dark']
            px[x, y] = c + (255,)
    return img

def black_outline(shape, w=None):
    a = shape.split()[3]
    dil = a.filter(ImageFilter.MaxFilter((w or 2*SS+1)))
    out = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    out.paste(Image.new('RGBA', (S, S), BLACK + (255,)), (0, 0), dil)
    out.paste(shape, (0, 0), shape)
    return out

def glare(img, phase):
    a = img.split()[3]
    g = Image.new('RGBA', (S, S), (0, 0, 0, 0)); dr = ImageDraw.Draw(g)
    dr.ellipse([S*0.30, S*0.30, S*0.44, S*0.44], fill=(255, 255, 255, 210))
    sx = int(S*0.14 + phase*S*0.62)
    dr.line([(sx, S*0.16), (sx-S*0.16, S*0.9)], fill=(255, 255, 255, 110), width=int(S*0.045))
    g = g.filter(ImageFilter.GaussianBlur(SS))
    g.putalpha(Image.composite(g.split()[3], Image.new('L', (S, S), 0), a))
    return Image.alpha_composite(img, g)

def build(mask_fn, pal, frames=FRAMES):
    m = Image.new('L', (S, S), 0); mask_fn(ImageDraw.Draw(m))
    front = black_outline(shaded(m, pal))
    sil = Image.new('RGBA', (S, S), (0, 0, 0, 0)); sil.paste(pal['side'] + (255,), (0, 0), m)
    side = black_outline(sil)
    sheet = Image.new('RGBA', (CELL*frames, CELL), (0, 0, 0, 0))
    for i in range(frames):
        ang = i/FRAMES*2*math.pi; c, s = math.cos(ang), math.sin(ang)
        # thick turntable: face never narrower than half-width, chunky extruded
        # side shows on the turn -> reads 3D, never a thin sliver
        fw = int(S*(0.55 + 0.45*abs(c))); dw = int(S*DEPTH*abs(s))
        fr = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        if dw > 2:
            sc = side.resize((dw, S), Image.LANCZOS)
            fr.paste(sc, ((S-dw)//2 + (int(S*0.06) if s > 0 else -int(S*0.06)), 0), sc)
        fc = front.resize((fw, S), Image.LANCZOS)
        fr.paste(fc, ((S-fw)//2, 0), fc)
        fr = glare(fr, i/FRAMES)
        sheet.paste(fr.resize((CELL, CELL), Image.LANCZOS), (i*CELL, 0), fr.resize((CELL, CELL), Image.LANCZOS))
    return sheet.quantize(colors=48, method=Image.FASTOCTREE).convert('RGBA')

def main():
    os.makedirs(OUT, exist_ok=True)
    note  = build(note_mask,  BLUE)
    heart = build(heart_mask, HEART)
    icon  = build(heart_mask, HEART, frames=1)          # front-only HUD heart
    note.save(os.path.join(OUT, 'note_blue.png'))
    heart.save(os.path.join(OUT, 'heart_spin.png'))
    icon.save(os.path.join(OUT, 'heart_icon.png'))
    prev = Image.new('RGBA', (CELL*FRAMES*4, CELL*2*4), (26, 14, 36, 255))
    prev.alpha_composite(note.resize((CELL*FRAMES*4, CELL*4), Image.NEAREST), (0, 0))
    prev.alpha_composite(heart.resize((CELL*FRAMES*4, CELL*4), Image.NEAREST), (0, CELL*4))
    prev.save(os.path.join(OUT, 'collectibles_preview.png'))
    print('baked note_blue.png, heart_spin.png, heart_icon.png (+ preview)')

if __name__ == '__main__':
    main()
