#!/usr/bin/env python3
"""Rewrite CARD_DATA in index.html from a finished re-cut, and report orphans.

Run pack.py --write for every stage first; this reads the same cut directory,
re-derives the rows, applies the per-card behaviour flags, splices the block into
index.html, and lists any web/ asset the new CARD_DATA no longer references.

The flags live HERE rather than in the region specs because they are game
behaviour, not geometry — and because two of them encode client decisions that
must survive a re-cut:

  * wind:1 goes ONLY on a card that is entirely plant life ("we only want plant
    life swaying bro not grass though"). The Rose Waltz colonnade carries rose
    garlands on marble arches and gets none — the greenery that sways there is
    the hedge behind it.
  * strip:1 is the ground-strip exception: a featureless full-width band gets a
    real rate and a loose clamp, because there is no landmark in it to notice
    having moved.

Usage: python3 swap.py            # dry run, prints the block and the orphans
       python3 swap.py --write
"""
import sys, os, re, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
CUT  = '/tmp/cards'

# stage index -> (cut tag, {card name: extra flags})
STAGES = {
    1: ('meadow', {'verge': 'strip:1'}),
    2: ('petal',  {'trees': 'amp:13,frq:3.0,wind:1', 'path': 'strip:1'}),
    3: ('rose',   {'backhedge': 'wind:1', 'terrace': 'strip:1'}),
    4: ('lake',   {'willowL': 'wind:1', 'willowC': 'wind:1', 'willowR': 'wind:1',
                   'shore': 'strip:1', 'water': 'ripple:1'}),
    # 5 THE WISHING GLADE — deliberately NOT cut. Its cut ran fine (510 masks,
    #   recompose 0.000%) and is discarded, exactly like the library's. The plate
    #   is a tiling wallpaper, not a space: median clump area per horizontal band
    #   measures 3177 / 2233 / 2351 / 2439 px, i.e. FLAT, with the topmost band
    #   holding the LARGEST clumps. A painting with depth shrinks its motif as it
    #   recedes; this one does not, so there is no depth in it to cut. Banding it
    #   anyway would shear the 32% of the plate that is continuous foliage
    #   between the clumps, and put a seam through unbroken growth wherever a
    #   band boundary fell. Stage 5 keeps the flat living-backdrop path.
    6: ('golden', {'farfield': 'wind:1', 'nearfield': 'wind:1', 'verge': 'strip:1'}),
    7: ('skyg',   {}),
    8: ('encore', {'foretrees': 'wind:1', 'river': 'ripple:1'}),
}


def rows():
    out, refs = [], set()
    for si in sorted(STAGES):
        tag, flags = STAGES[si]
        meta = f'{CUT}/{tag}_pack.json'
        if not os.path.exists(meta):
            print(f'  (stage {si} / {tag}: not packed yet — skipping)', file=sys.stderr)
            continue
        d = json.load(open(meta))
        refs.add(d['base'])
        line = [f" {si}:{{w:{d['w']},h:{d['h']},base:'web/{d['base']}.webp',cards:["]
        for c in d['cards']:
            refs.add(c['h'])
            pv = '' if c['pv'] > 0.995 else f"pv:{c['pv']:.3f},"
            ex = flags.get(c['name'], '')
            ex = (ex + ',') if ex else ''
            line.append(f"   {{n:'{c['name']}',".ljust(21) +
                        f"d:{c['depth']:.2f},{pv}{ex}s:'web/{c['h']}.webp'}},")
        line[-1] = line[-1].rstrip(',')
        line.append(' ]},')
        out.append('\n'.join(line))
        unknown = set(flags) - {c['name'] for c in d['cards']}
        if unknown:
            print(f'  ! stage {si}: flags for cards that do not exist: {sorted(unknown)}',
                  file=sys.stderr)
    return out, refs


def main(write):
    block, refs = rows()
    if len(block) != len(STAGES):
        print(f'\nONLY {len(block)}/{len(STAGES)} stages packed — refusing to splice a '
              f'partial CARD_DATA.', file=sys.stderr)
        write = False
    new = 'var CARD_DATA={\n' + '\n'.join(block) + '\n};'
    print(new)

    idx = os.path.join(REPO, 'index.html')
    src = open(idx, encoding='utf-8').read()
    m = re.search(r'var CARD_DATA=\{.*?\n\};', src, re.S)
    old_refs = set(re.findall(r'web/([0-9a-f]{12})\.webp', m.group(0)))
    print(f'\nwas {len(old_refs)} assets, now {len(refs)}; '
          f'{len(old_refs - refs)} superseded, {len(refs - old_refs)} new')

    if write:
        src = src[:m.start()] + new + src[m.end():]
        open(idx, 'w', encoding='utf-8').write(src)
        # only delete what the WHOLE file no longer mentions — an old card hash
        # could in principle still be referenced somewhere else
        rest = set(re.findall(r'web/([0-9a-f]{12})\.\w+', src))
        for h in sorted(old_refs - refs):
            if h in rest:
                print(f'  keeping {h}: still referenced elsewhere')
                continue
            p = os.path.join(REPO, 'web', h + '.webp')
            if os.path.exists(p):
                os.remove(p); print(f'  removed web/{h}.webp')
        print('CARD_DATA spliced.')
    else:
        print('DRY RUN — pass --write')


if __name__ == '__main__':
    main('--write' in sys.argv)
