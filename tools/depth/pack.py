#!/usr/bin/env python3
"""Pack a finished cut into the game: full-frame WebP cards + the CARD_DATA row.

cards.py writes each card CROPPED to its own bounding box, at the 2x scale SAM
worked on. The game wants the opposite of that:

  * FULL FRAME, at the plate's native size. A card drawn at the same rect as the
    base plate is always in register with the hole it was lifted from, so there
    is no per-card offset to get wrong — and getting one wrong is exactly what
    produced the displaced cards the client saw as "gaps in space".
  * content-addressed: web/<sha1-12>.webp, so a re-cut that happens to produce an
    identical card reuses the file instead of orphaning one.

Usage:  python3 pack.py <tag> <stage-index> [--write]
Without --write it reports what it WOULD do and touches nothing.
"""
import sys, os, json, hashlib, io as _io
import numpy as np
from PIL import Image

CUT  = '/tmp/cards'
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
WEB  = os.path.join(REPO, 'web')
Q    = 82


def sha_name(buf):
    return hashlib.sha1(buf).hexdigest()[:12]


def encode(im, rgba):
    b = _io.BytesIO()
    im.save(b, 'WEBP', quality=Q, method=6, exact=rgba)
    return b.getvalue()


def main(tag, stage, write):
    cards = json.load(open(f'{CUT}/{tag}_cards.json'))
    if not cards:
        print(f'{tag}: no cards'); return
    CW, CH = cards[0]['w'], cards[0]['h']            # the cut resolution (2x)
    NW, NH = CW // 2, CH // 2                        # the plate's native size
    print(f'{tag}: cut {CW}x{CH} -> plate {NW}x{NH}, {len(cards)} cards')

    out, total = [], 0
    base = Image.open(f'{CUT}/{tag}_base.png').convert('RGB').resize((NW, NH), Image.LANCZOS)
    buf = encode(base, False)
    base_h = sha_name(buf)
    files = [(base_h + '.webp', buf)]
    total += len(buf)

    for c in cards:
        x0, y0, x1, y1 = c['crop']
        full = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
        full.paste(Image.open(f'{CUT}/{tag}_{c["name"]}.png').convert('RGBA'), (x0, y0))
        full = full.resize((NW, NH), Image.LANCZOS)
        # A card that survives the cut but covers almost nothing is not worth a
        # network request or a draw call — say so rather than shipping it.
        al = np.asarray(full)[:, :, 3] > 8
        cov = 100.0 * al.mean()
        # PIVOT: the bottom of this card's own content, as a fraction of the
        # frame. The wind shear is zero here, so for a tree card this is the
        # trunk line and the roots stay put. Full-frame cards all share the
        # plate's rect, so without this the pivot lands on the bottom of the
        # PLATE and the trunk swings with the crown.
        rows = np.where(al.any(axis=1))[0]
        pv = (float(rows.max()) + 1) / NH if len(rows) else 1.0
        buf = encode(full, True)
        h = sha_name(buf)
        files.append((h + '.webp', buf))
        total += len(buf)
        out.append((c['name'], c['depth'], h, cov, len(buf), pv))
        flag = '   <-- under 0.5% of frame, consider dropping' if cov < 0.5 else ''
        print(f'  {c["name"]:12s} d {c["depth"]:.2f}  covers {cov:5.2f}%  {len(buf)/1024:6.1f} KB{flag}')
    print(f'{tag}: base + {len(out)} cards = {total/1024:.1f} KB')

    row = [f' {stage}:{{w:{NW},h:{NH},base:\'web/{base_h}.webp\',cards:[']
    for n, d, h, cov, _, pv in out:
        # pv only matters to a wind card; emit it when it is not the frame edge
        # so a later wind flag has it already measured and correct.
        p = '' if pv > 0.995 else f'pv:{pv:.3f},'
        row.append(f"   {{n:'{n}',".ljust(22) + f"d:{d:.2f},{p}s:'web/{h}.webp'}},")
    row[-1] = row[-1].rstrip(',')
    row.append(' ]},')
    print('\n'.join(row))

    if write:
        for name, buf in files:
            open(os.path.join(WEB, name), 'wb').write(buf)
        print(f'{tag}: wrote {len(files)} files into web/')
    else:
        print(f'{tag}: DRY RUN — pass --write to place the files')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], '--write' in sys.argv)
