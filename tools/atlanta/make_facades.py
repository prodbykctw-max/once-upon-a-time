#!/usr/bin/env python3
"""Composite facade trim sheets: CC0 wall material + a procedural window grid.

    python3 tools/atlanta/make_facades.py   -> tools/atlanta/art/facades/*.jpg

This is the "floor count -> window grid on trim sheets" half of the detail pass.
OSM gives a footprint and a height and nothing else, so **every generic building
is a box** — what stops it reading as a box is the facade, not the geometry.

Each sheet is one TILE of wall, and the tile's real-world size is baked into the
filename so the UVs cannot drift out of step with it:

    <style>_<tileW>x<tileH>m.jpg

`city.js` divides wall distance by tileW and wall height by tileH, so a 3.2 m
floor is a 3.2 m floor on screen. Change a tile size here and the viewer picks
it up from the name — there is no second place to edit, and no way to forget.

Windows are drawn, not photographed, so there is nothing to clear: no signage,
no brands, no recognisable interiors. (The source project has a live note to
paint real chip brands out of a photographed facade — this avoids that whole
class of problem.)
"""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
PBR = os.path.join(HERE, 'art', 'pbr')
OUT = os.path.join(HERE, 'art', 'facades')
os.makedirs(OUT, exist_ok=True)

PX = 1024
FLOOR_M = 3.2                      # one storey


def base(tex_id, px, tint=1.0, reps=1):
    """CC0 diffuse tiled `reps` times across the sheet, optionally tinted.

    REPS MATTERS AND IS EASY TO GET WRONG. A Poly Haven wall scan covers roughly
    2 m of real wall. Stretched once across a 14 m facade tile, the bricks come
    out about a metre each and the building reads as a toy. Tile it so a brick is
    a brick.
    """
    p = os.path.join(PBR, tex_id, 'diff.jpg')
    if not os.path.exists(p):
        raise SystemExit('missing %s — run `node tools/atlanta/fetch_pbr.mjs` first' % p)
    src = Image.open(p).convert('RGB')
    if reps > 1:
        cell = max(1, px // reps)
        src = src.resize((cell, cell), Image.LANCZOS)
        im = Image.new('RGB', (px, px))
        for yy in range(0, px, cell):
            for xx in range(0, px, cell):
                im.paste(src, (xx, yy))
    else:
        im = src.resize((px, px), Image.LANCZOS)
    if tint != 1.0:
        a = np.asarray(im).astype(np.float32) * tint
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return im


def window_pane(d, x0, y0, x1, y1, rng, glass=(28, 38, 52), lit=0.18):
    """One pane: dark glass, a sky-ish gradient, an occasional lit room."""
    if rng.random() < lit:
        g = (int(188 + rng.random() * 40), int(168 + rng.random() * 40), int(128 + rng.random() * 30))
    else:
        g = glass
    d.rectangle([x0, y0, x1, y1], fill=g)
    # a lighter band at the top of the pane reads as sky reflection
    h = max(1, int((y1 - y0) * 0.34))
    d.rectangle([x0, y0, x1, y0 + h],
                fill=tuple(min(255, int(c * 1.0 + 44)) for c in g))


def grid_facade(name, tex_id, floors, cols, tint=1.0,
                frame=(196, 192, 184), sill=True, seed=7, glass=(26, 36, 50),
                lit=0.16, inset=0.16, band=None, reps=1):
    """A tile `cols` windows wide and `floors` storeys tall."""
    rng = random.Random(seed)
    im = base(tex_id, PX, tint, reps)
    d = ImageDraw.Draw(im)
    cw, ch = PX / cols, PX / floors
    for r in range(floors):
        for c in range(cols):
            x0, y0 = c * cw, r * ch
            mx, my = cw * inset, ch * 0.22
            wx0, wy0 = x0 + mx, y0 + my
            wx1, wy1 = x0 + cw - mx, y0 + ch - my * 1.5
            # frame
            d.rectangle([wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3], fill=frame)
            window_pane(d, wx0, wy0, wx1, wy1, rng, glass, lit)
            # mullion
            xm = (wx0 + wx1) / 2
            d.rectangle([xm - 1.5, wy0, xm + 1.5, wy1], fill=frame)
            if sill:
                d.rectangle([wx0 - 5, wy1 + 2, wx1 + 5, wy1 + 7],
                            fill=tuple(int(c2 * 0.86) for c2 in frame))
        if band is not None and r == 0:
            d.rectangle([0, 0, PX, int(ch * 0.10)], fill=band)
    im = im.filter(ImageFilter.GaussianBlur(0.4))
    tw, th = cols * 3.6, floors * FLOOR_M        # tile size in metres
    f = '%s_%.1fx%.1fm.jpg' % (name, tw, th)
    im.save(os.path.join(OUT, f), quality=88)
    print('  %-34s %d floors x %d windows  tile %.1f x %.1f m' % (f, floors, cols, tw, th))
    return f


def curtain_wall(name, floors, cols, seed=3):
    """A glass tower: mullions over glass, almost no solid wall."""
    rng = random.Random(seed)
    im = Image.new('RGB', (PX, PX), (34, 46, 62))
    d = ImageDraw.Draw(im)
    cw, ch = PX / cols, PX / floors
    for r in range(floors):
        for c in range(cols):
            x0, y0 = c * cw, r * ch
            window_pane(d, x0 + 2, y0 + 3, x0 + cw - 2, y0 + ch - 4, rng,
                        glass=(30, 44, 64), lit=0.13)
        d.rectangle([0, r * ch, PX, r * ch + 4], fill=(150, 152, 156))   # spandrel
    for c in range(cols + 1):
        d.rectangle([c * cw - 2, 0, c * cw + 2, PX], fill=(150, 152, 156))
    im = im.filter(ImageFilter.GaussianBlur(0.35))
    tw, th = cols * 3.0, floors * FLOOR_M
    f = '%s_%.1fx%.1fm.jpg' % (name, tw, th)
    im.save(os.path.join(OUT, f), quality=88)
    print('  %-34s %d floors x %d bays  tile %.1f x %.1f m' % (f, floors, cols, tw, th))
    return f


print('facade trim sheets ->', os.path.relpath(OUT, os.getcwd()))
grid_facade('brick_lowrise', 'red_brick_03', floors=3, cols=4, tint=1.0,
            frame=(224, 220, 210), seed=11, lit=0.20, reps=7)   # 14.4 m / ~2 m scan
grid_facade('concrete_midrise', 'concrete_wall_008', floors=5, cols=5, tint=1.05,
            frame=(186, 184, 180), seed=5, lit=0.15, inset=0.10, reps=5)  # 18 m / ~4 m
curtain_wall('glass_tower', floors=6, cols=6)
print('\n  windows are DRAWN, not photographed — no signage, brands or interiors to clear')
print('  wall bases: CC0 Poly Haven')
