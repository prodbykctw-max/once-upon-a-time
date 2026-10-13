# RPG CHARACTER SHEETS — rendered from the SHIPPED atlases in web/, nothing redrawn.
import os
from PIL import Image, ImageDraw, ImageFont
import os, sys
# repo root = three levels up from presentation/characters/src/
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

OUT = os.path.join(R, 'presentation', 'characters')
os.makedirs(OUT, exist_ok=True)
CF = '/mnt/skills/examples/canvas-design/canvas-fonts'

# The palette is the GAME'S OWN: ink 181320 is the Ink Warden's ink, cream e8e0cf
# is the torn page from the same aura code, gold ffe08a is stage 0's accent.
INK, INK2, CREAM, GOLD = (24, 19, 32), (33, 26, 44), (232, 224, 207), (255, 224, 138)
DIM = (150, 140, 160)

def F(name, sz):
    return ImageFont.truetype(os.path.join(CF, name), sz)
def STORY(sz):  # the game's display face — headings only, per the two-tier rule
    return ImageFont.truetype(os.path.join(R, 'web', '435323e92ad8.ttf'), sz)

H1, H2, BOLD, BODY, MONO = STORY(74), STORY(40), F('Lora-Bold.ttf', 23), F('Lora-Regular.ttf', 20), F('GeistMono-Regular.ttf', 17)

def hdr(d, w, title, sub, note):
    d.text((54, 40), title, font=H1, fill=CREAM)
    d.text((58, 132), sub, font=BOLD, fill=GOLD)
    d.text((58, 166), note, font=MONO, fill=DIM)
    d.line([(54, 204), (w - 54, 204)], fill=(70, 60, 86), width=2)

def cell(atlas, x, y, cw, ch, scale):
    c = atlas.crop((x, y, x + cw, y + ch))
    return c.resize((int(cw * scale), int(ch * scale)), Image.NEAREST)

# ════════════════════════════════════════════════════════════════════════
#  1. JANDÉ — every animation slot that ships
# ════════════════════════════════════════════════════════════════════════
SPR = [
    ('idle',       6, 89, 154, 0, 'web/865c17b4dacb.png', 9, 'Standing. Breath and shift.'),
    ('run',        8, 145, 154, 0, 'web/36be4ed7efc3.png', 4, '203 world px per 32-frame cycle = 2.36 body heights.'),
    ('jump',       6, 102, 154, 0, 'web/9f32be555c97.png', 7, '6 frames held 7 each across 44 frames of airtime.'),
    ('attack',     8, 154, 154, 0, 'web/6c4f4b151d3d.png', 2, 'MIC STRIKE — the fastest sheet in the game, 30fps.'),
    ('dash',       5, 159, 154, 0, 'web/e803235545ba.png', 4, 'Ground dash, on a cooldown.'),
    ('block',      3, 93, 154, 0, 'web/1b211642b143.png', 6, 'HOLD NOTE — the guard.'),
    ('dance',      6, 120, 154, 0, 'web/89251d16231c.png', 6, 'Idle flourish and the victory beat.'),
    ('refrain',    6, 103, 154, 0, 'web/7308e8a460ab.png', 6, 'REFRAIN — she heals by singing.'),
    ('belt',       5, 150, 154, 0, 'web/5e3c3ac40f3b.png', 4, 'BELT — the magic strike.'),
    ('downstrike', 4, 172, 154, 0, 'web/906d4cb96105.png', 4, 'DOWNBEAT — the aerial pogo.'),
]
BK = [
    ('bkrun',   'web/73d33193c5ad.webp', 'Royal Runner — the run.'),
    ('bkjump',  'web/c2da2f2d110f.webp', 'Royal Runner — the jump.'),
    ('bkslide', 'web/1ff3fa4d05b5.webp', 'Royal Runner — the slide.'),
]
SC = 1.05
rowh = int(154 * SC) + 62
W = 54 + max(int(cw * n * SC) for _, n, cw, _, _, _, _, _ in SPR) + 54
W = max(W, 1500)
Hh = 230 + rowh * len(SPR) + 90 + (int(256 * 0.62) + 62) * len(BK) + 70
img = Image.new('RGB', (W, Hh), INK)
d = ImageDraw.Draw(img)
for i in range(Hh):  # a faint vertical lift, so the sheet is not a flat slab
    d.line([(0, i), (W, i)], fill=tuple(int(a + (b - a) * (i / Hh)) for a, b in zip(INK2, INK)))
hdr(d, W, 'JANDÉ', 'THE HERO — 13 rendered animation sheets, 75 side frames + 75 back frames',
    'Side view faces RIGHT; left is a mirror.  `spd` is game-frames PER animation frame, so SMALLER IS FASTER.')
y = 230
for nm, n, cw, ch, _c, src, spd, note in SPR:
    at = Image.open(os.path.join(R, src)).convert('RGBA')
    d.text((54, y), nm.upper(), font=BOLD, fill=GOLD)
    d.text((54 + d.textlength(nm.upper(), font=BOLD) + 18, y + 3),
           f'{n} frames · {cw}x{ch} · spd {spd} = {60/spd:.1f}fps', font=MONO, fill=DIM)
    d.text((54, y + 30), note, font=BODY, fill=(190, 182, 200))
    yy = y + 58
    for f in range(n):
        img.paste(cell(at, f * cw, 0, cw, ch, SC), (54 + int(f * cw * SC), yy), cell(at, f * cw, 0, cw, ch, SC))
    y += rowh
d.line([(54, y + 10), (W - 54, y + 10)], fill=(70, 60, 86), width=2)
d.text((54, y + 30), 'BACK VIEW — ROYAL RUNNER', font=H2, fill=CREAM)
d.text((54, y + 80), '25 frames each, 1280x1280 at 5x5 of 256px. Frames 0 / 6 / 12 / 18 / 24 shown.', font=MONO, fill=DIM)
y += 112
for nm, src, note in BK:
    at = Image.open(os.path.join(R, src)).convert('RGBA')
    d.text((54, y), nm.upper(), font=BOLD, fill=GOLD)
    d.text((54 + d.textlength(nm.upper(), font=BOLD) + 18, y + 3), '25 frames · 256x256 cells', font=MONO, fill=DIM)
    d.text((54, y + 30), note, font=BODY, fill=(190, 182, 200))
    yy = y + 58
    for i, f in enumerate([0, 6, 12, 18, 24]):
        c = cell(at, (f % 5) * 256, (f // 5) * 256, 256, 256, 0.62)
        img.paste(c, (54 + i * (c.width + 8)), None) if False else img.paste(c, (54 + i * (c.width + 8), yy), c)
    y += int(256 * 0.62) + 62
img.save(os.path.join(OUT, '01-jande-hero.png'))
print('01-jande-hero.png', img.size)
