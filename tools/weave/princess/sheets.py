#!/usr/bin/env python3
"""Princess outfit restyle (Game I): pack hero SPRITES slots onto #00FF00 sheets for a
ChatGPT image edit, then unpack the edited sheet back into per-slot strips.

  python3 sheets.py pack   <group> <out.png>
  python3 sheets.py unpack <group> <edited.png> <outdir>

Cells are uniform (max cw of the group x 154) at 3x with 24px gutters; each frame is
centred in its cell. Unpack keys green (G - max(R,B) > 30..90), clamps spill, scales
back, and aligns each frame to its original by an alpha-IoU offset search (+/-8px).
The originals in web/ are never modified (Jandé's public-game art).
"""
import sys, json, os
import numpy as np
from PIL import Image
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
SL = {  # slot: (frames, cw, src)
 'idle': (6, 89, 'web/865c17b4dacb.png'), 'run': (8, 145, 'web/36be4ed7efc3.png'),
 'jump': (6, 102, 'web/9f32be555c97.png'), 'attack': (8, 154, 'web/6c4f4b151d3d.png'),
 'dash': (5, 159, 'web/e803235545ba.png'), 'block': (3, 93, 'web/1b211642b143.png'),
 'downstrike': (4, 172, 'web/906d4cb96105.png'), 'belt': (5, 150, 'web/5e3c3ac40f3b.png'),
 'refrain': (6, 103, 'web/7308e8a460ab.png')}
# ONE animation per sheet (11-17: mixed sheets sent into a chat that already held the run
# edit came back as copies of the run poses). Cols chosen to keep the sheet near 2:1.
GROUPS = {'idle': (['idle'], 3), 'run': (['run'], 4), 'attack': (['attack'], 4), 'jump': (['jump'], 3),
          'block': (['block'], 3), 'refrain': (['refrain'], 3), 'belt': (['belt'], 3),
          'dash': (['dash'], 3), 'downstrike': (['downstrike'], 2),
          'jumpblock': (['jump', 'block'], 5), 'refrainbelt': (['refrain', 'belt'], 4)}
CH, S, G = 154, 3, 24

def cells(group):
    slots, cols = GROUPS[group]
    cw = max(SL[s][1] for s in slots)
    lst = []
    for s in slots:
        n, w, src = SL[s]
        im = Image.open(os.path.join(REPO, src)).convert('RGBA')
        for i in range(n): lst.append((s, i, w, im.crop((i * w, 0, (i + 1) * w, CH))))
    rows = (len(lst) + cols - 1) // cols
    return lst, cw, cols, rows

def geom(cw, cols, rows):
    return cols * cw * S + (cols + 1) * G, rows * CH * S + (rows + 1) * G

def pack(group, out):
    lst, cw, cols, rows = cells(group)
    W, H = geom(cw, cols, rows)
    sh = Image.new('RGBA', (W, H), (0, 255, 0, 255))
    for k, (s, i, w, f) in enumerate(lst):
        x = G + (k % cols) * (cw * S + G) + (cw - w) * S // 2; y = G + (k // cols) * (CH * S + G)
        sh.alpha_composite(f.resize((w * S, CH * S), Image.LANCZOS), (x, y))
    sh.convert('RGB').save(out); print(out, W, H, len(lst), 'frames')

def unpack(group, edited, outdir):
    lst, cw, cols, rows = cells(group)
    W, H = geom(cw, cols, rows)
    g = Image.open(edited).convert('RGB'); kx, ky = g.size[0] / W, g.size[1] / H
    a = np.asarray(g).astype(float); R, Gc, B = a[..., 0], a[..., 1], a[..., 2]
    gd = Gc - np.maximum(R, B); al = np.clip(1 - (gd - 30) / 60, 0, 1)
    rgb = a.copy(); rgb[..., 1] = np.minimum(Gc, np.maximum(R, B))
    K = Image.fromarray(np.dstack([rgb, al * 255]).astype(np.uint8), 'RGBA')
    strips, rep = {}, {}
    for k, (s, i, w, orig) in enumerate(lst):
        x = G + (k % cols) * (cw * S + G) + (cw - w) * S // 2; y = G + (k // cols) * (CH * S + G)
        f = K.crop((round(x * kx), round(y * ky), round((x + w * S) * kx), round((y + CH * S) * ky))).resize((w, CH), Image.LANCZOS)
        oa = np.asarray(orig)[..., 3] > 40; fa = np.asarray(f)[..., 3] > 40; best = (-1, 0, 0)
        for dx in range(-8, 9):
            for dy in range(-8, 9):
                sh = np.roll(np.roll(fa, dy, 0), dx, 1); sc = (sh & oa).sum() / max(1, (sh | oa).sum())
                if sc > best[0]: best = (sc, dx, dy)
        o = Image.new('RGBA', (w, CH), (0, 0, 0, 0)); o.alpha_composite(f, (best[1], best[2]))
        n = SL[s][0]
        strips.setdefault(s, Image.new('RGBA', (w * n, CH), (0, 0, 0, 0))).alpha_composite(o, (i * w, 0))
        rep.setdefault(s, []).append(round(best[0], 3))
    os.makedirs(outdir, exist_ok=True)
    for s, im in strips.items(): im.save(os.path.join(outdir, s + '_new.png'))
    print(json.dumps(rep))

if __name__ == '__main__':
    if sys.argv[1] == 'pack': pack(sys.argv[2], sys.argv[3])
    else: unpack(sys.argv[2], sys.argv[3], sys.argv[4])
