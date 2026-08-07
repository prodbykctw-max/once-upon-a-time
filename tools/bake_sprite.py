#!/usr/bin/env python3
"""Bake back-view pixel-art sprite sheets of Jande for Temple View.
Look: voluminous auburn curls, flowing white gown w/ gold trim, white boots."""
from PIL import Image
import math, os

SW, SH = 36, 52          # logical pixel grid per frame
SCALE = 4                # upscale factor -> 144x208 cells
OUT = os.path.dirname(os.path.abspath(__file__))

C = {
    'hd': '#421708', 'hm': '#6e2b12', 'hl': '#96421d', 'hs': '#b85c28',
    'sk': '#8a5a3b', 'sd': '#6f4630',
    'dr': '#f1eadd', 'dd': '#d5c9b4', 'dl': '#fffef8', 'au': '#d4af37',
    'bt': '#ece5d6', 'bd': '#c9bda6', 'so': '#7a6a55',
}
def hexc(h):
    return tuple(int(h[i:i+2], 16) for i in (1, 3, 5)) + (255,)

class F:
    def __init__(self):
        self.img = Image.new('RGBA', (SW, SH), (0, 0, 0, 0))
        self.px = self.img.load()
    def P(self, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < SW and 0 <= y < SH:
            self.px[x, y] = hexc(C[c])
    def row(self, x0, x1, y, c):
        for x in range(int(x0), int(x1) + 1):
            self.P(x, y, c)

def hair(f, t, top, lag, low=0):
    """Curly auburn mass: crown at y=top, widest mid, taper to back. low>0 widens/shortens (crouch)."""
    cx = SW // 2
    bot = top + 18 - low * 5
    for y in range(top, bot + 1):
        p = (y - top) / max(1, bot - top)          # 0 crown -> 1 tip
        w = 5 + 9 * math.sin(min(1, p * 1.15) * math.pi * 0.72)   # rounder, widest mid
        w += low * 4
        wob = round(math.sin(y * 1.9 + lag * 2.2) * 1.2)          # curl wobble
        x0, x1 = round(cx - w / 2) + (wob if y % 2 else 0), round(cx + w / 2) + (0 if y % 2 else wob)
        f.row(x0, x1, y, 'hm')
        # curl texture
        for x in range(x0, x1 + 1):
            h = (x * 7 + y * 13 + int(lag * 3)) % 13
            if h < 2: f.P(x, y, 'hl')
            elif h == 3 and y > top + 3: f.P(x, y, 'hd')
            elif h == 5 and p < 0.4: f.P(x, y, 'hs')
        f.P(x0, y, 'hd'); f.P(x1, y, 'hd')        # rim
    # crown highlight
    f.row(SW//2 - 2, SW//2 + 2, top + 1, 'hl')

def dress(f, t, sway, shY, hemY, flare=0, pool=False):
    """Gown from shoulders (shY) to hem (hemY); sway shifts hem laterally."""
    cx = SW // 2
    beltY = None
    for y in range(shY, hemY + 1):
        p = (y - shY) / max(1, hemY - shY)
        if p < 0.26:
            w = 10 - 3 * (p / 0.26)               # fitted bodice 10 -> 7
        else:
            q = (p - 0.26) / 0.74
            w = 7 + (15 + flare * 6) * (q ** 1.25) # flare 7 -> 22
        if pool: w = 10 + 16 * p
        if beltY is None and p >= 0.26: beltY = y
        sh = round(sway * 2.4 * max(0, p - 0.25))
        x0, x1 = round(cx - w / 2 + sh), round(cx + w / 2 + sh)
        f.row(x0, x1, y, 'dr')
        for x in range(x0, x1 + 1):                # soft vertical folds
            if (x - sh + y // 9) % 5 == 0: f.P(x, y, 'dd')
        f.P(x0, y, 'dd'); f.P(x1, y, 'dl')        # shade L, light R
    if beltY and not pool:
        f.row(cx - 4, cx + 4, beltY, 'au')        # gold belt at waist
    f.row(cx - 10 + round(sway * 1.8), cx + 10 + round(sway * 1.8), hemY, 'au')  # gold hem

def arms(f, t, shY, swing):
    """Slim white-gloved arms pumping at the sides; hands skin."""
    cx = SW // 2
    for side in (-1, 1):
        ph = swing * side
        ax = cx + side * 6
        top = shY + 2
        bend = round(ph * 2)
        for y in range(top, top + 7):
            f.P(ax + (side if y > top + 3 else 0), y + max(0, bend), 'dr')
        f.P(ax + side, top + 7 + max(0, bend), 'sk')   # hand

def boots(f, t, hemY, phase, tuck=0):
    """Alternating stride below the hem; lifted heel shows sole. tuck>0: both tucked (jump)."""
    cx = SW // 2
    for side in (-1, 1):
        lx = cx + side * 3
        lift = tuck * 4 if tuck else max(0.0, math.sin(phase + (0 if side < 0 else math.pi))) * 5
        bot = SH - 3 - round(lift)
        for y in range(hemY + 1, bot + 1):
            f.P(lx - 1, y, 'bd'); f.P(lx, y, 'bt'); f.P(lx + 1, y, 'bt')
        if lift > 1.5:                             # kicked-up sole
            f.row(lx - 1, lx + 1, bot + 1, 'so')

def run_frame(i, n=8):
    f = F(); t = i / n * 2 * math.pi
    bob = round(math.sin(2 * t) * 1)
    sway = math.sin(t)
    shY, hemY = 14 + bob, 44
    boots(f, t, hemY, t)
    dress(f, t, sway, shY, hemY)
    arms(f, t, shY, sway)
    hair(f, t, 3 + bob + round(math.sin(2 * t - 1.0) * 1), sway)
    return f.img

def jump_frame(i, n=4):
    f = F()
    ph = [0, 1, 2, 1.4][i]                        # crouch, rise, peak, fall
    rise = round(ph * 2)
    shY, hemY = 14 - rise + (2 if i == 0 else 0), 42 - rise + (3 if i == 0 else 0)
    boots(f, 0, hemY, 0, tuck=(0 if i == 0 else ph))
    dress(f, 0, 0, shY, hemY, flare=(1 if i >= 1 else 0))
    arms(f, 0, shY, -1 if i >= 1 else 0.5)
    hair(f, 0, max(1, 3 - rise), 0.5 * i)
    return f.img

def slide_frame(i, n=2):
    f = F(); j = i * 0.7
    shY, hemY = 26, 45
    dress(f, 0, 0.4 * (1 if i else -1), shY, hemY, pool=True)
    arms(f, 0, shY, 0.8 * (1 if i else -1))
    hair(f, 0, 14, j, low=1)
    f.row(SW//2 - 6, SW//2 + 6, hemY + 1, 'bd')   # boots tucked under pooled dress
    return f.img

def sheet(frames, name):
    cw, ch = SW * SCALE, SH * SCALE
    out = Image.new('RGBA', (cw * len(frames), ch), (0, 0, 0, 0))
    for k, fr in enumerate(frames):
        out.paste(fr.resize((cw, ch), Image.NEAREST), (k * cw, 0))
    out.save(os.path.join(OUT, name))
    return cw, ch

run = [run_frame(i) for i in range(8)]
jmp = [jump_frame(i) for i in range(4)]
sld = [slide_frame(i) for i in range(2)]
print('bkrun', sheet(run, 'bkrun.png'))
print('bkjump', sheet(jmp, 'bkjump.png'))
print('bkslide', sheet(sld, 'bkslide.png'))

# preview contact sheet on dark bg
allf = run + jmp + sld
pw, ph2 = SW * 3, SH * 3
prev = Image.new('RGBA', (pw * len(allf), ph2), (18, 8, 28, 255))
for k, fr in enumerate(allf):
    prev.paste(fr.resize((pw, ph2), Image.NEAREST), (k * pw, 0), fr.resize((pw, ph2), Image.NEAREST))
prev.save(os.path.join(OUT, 'preview.png'))
print('preview done')
