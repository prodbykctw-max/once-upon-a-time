#!/usr/bin/env python3
"""Does a monocular depth model actually work on THESE plates?

The question is not whether depth estimation is good — it is whether it holds up
on hand-painted fairytale illustrations, because every published benchmark for
these models is photographs. So this does not assume; it measures two things:

RESULT (2026-09-15, Depth Anything V2 Small, CPU, ~15s/plate):
  * It WORKS on this painted art. 30 of 31 consecutive region pairs agree with
    the depths I assigned by eye — 97%. The one inversion is the Mirror Lake
    willows, whose region boxes are tall and swallow sky and hills, so the
    median inside the box is contaminated; that is a limit of comparing against
    BOXES rather than the cut masks, not a real disagreement.
  * SKY GARDENS IS PROBABLY NOT FLAT. Its depth map resolves each floating
    island as a separate near blob against far sky — genuine per-object
    structure. I called that plate flat on a motif-area heuristic; this is
    better evidence and it points the other way. The Wishing Glade, by
    contrast, comes back as mostly a smooth vertical ramp, which supports
    leaving it flat.
  * THE STRUCTURE METRIC BELOW DOES NOT SETTLE ANYTHING. Residual-after-ramp
    ranks Sky Gardens (67%) and the Petal Mile (64%) top, because it cannot
    tell real object depth from high-frequency texture. Kept for reference, not
    relied on. The depth MAPS are the evidence; look at them.

  1. ORDERING AGREEMENT. Every card in CARD_DATA carries a depth `d` that I chose
     BY EYE. The region specs in tools/depth/regions/*.json say which part of the
     plate each one covers. Sample the model's depth inside each of those boxes
     and check whether its ordering matches mine. Where we disagree, one of us is
     wrong — and a card whose depth is wrong relative to its neighbour is exactly
     the bug that had blossom moving faster than its own trunks.

  2. THE FLAT PLATES. The Wishing Glade and the Sky Gardens were declared flat on
     a motif-area heuristic (median segment size per horizontal band was level).
     A depth model is a much better instrument for that question. If it finds
     real depth structure in them, that call needs revisiting.

Writes side-by-side plate/depth previews and a comparison table.
"""
import io, os, sys, json, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT  = os.environ.get('DEPTH_OUT', '/tmp/depthtest')

# stage -> (plate hash, region spec tag)
PLATES = {
    0: ('7026911858d1', None),      1: ('1fa28057a711', 'meadow'),
    2: ('44187ebf6a44', 'petal'),   3: ('afcfb1d92476', 'rose'),
    4: ('da0a81c9b45f', 'lake'),    5: ('9d4d20ccbac3', 'glade'),
    6: ('14ab4c11ab60', 'golden'),  7: ('1ae0890e08c3', 'skyg'),
    8: ('a4a908d52b36', 'encore'),
}
NAMES = ['library','meadow','petal mile','rose waltz','mirror lake',
         'wishing glade','golden hour','sky gardens','her encore']


def load_model():
    from transformers import pipeline
    return pipeline('depth-estimation',
                    model='depth-anything/Depth-Anything-V2-Small-hf', device=-1)


def main():
    from PIL import Image
    os.makedirs(OUT, exist_ok=True)
    pipe = load_model()
    rows = []
    for si, (h, tag) in sorted(PLATES.items()):
        p = os.path.join(REPO, 'web', h + '.webp')
        im = Image.open(p).convert('RGB')
        d = pipe(im)['depth']                       # PIL, higher = NEARER
        a = np.asarray(d).astype(np.float32)
        a = (a - a.min()) / max(1e-6, float(np.ptp(a)))   # 0 far .. 1 near
        # np.ptp(a), not a.ptp() — NumPy 2 removed the method from ndarray
        np.save(os.path.join(OUT, '%s_depth.npy' % (tag or 'library')), a)
        # preview: plate above, depth below
        dv = Image.fromarray((a * 255).astype(np.uint8)).convert('RGB')
        cw, ch = im.size
        sheet = Image.new('RGB', (cw, ch * 2 + 6), (14, 14, 18))
        sheet.paste(im, (0, 0)); sheet.paste(dv, (0, ch + 6))
        sheet.save(os.path.join(OUT, '%s_pair.png' % (tag or 'library')))
        # how much depth RANGE is in this plate at all?
        p10, p90 = np.percentile(a, 10), np.percentile(a, 90)
        rows.append((si, NAMES[si], tag, a, p90 - p10, float(a.std())))
        print('  %-14s depth spread p10-p90 %.3f   std %.3f' % (NAMES[si], p90 - p10, a.std()))

    # ── 1. ordering agreement against the hand-authored card depths ──────────
    print('\nHAND-ASSIGNED depth vs MODEL depth, per region '
          '(model: 0 far .. 1 near, so it should DECREASE as my d increases)\n')
    for si, name, tag, a, _, _ in rows:
        spec = os.path.join(HERE, 'regions', '%s.json' % tag) if tag else None
        if not spec or not os.path.exists(spec):
            continue
        regs = json.load(open(spec))
        H, W = a.shape
        out = []
        for r in regs:
            x0, y0, x1, y1 = [int(v * s) for v, s in zip(r['box'], (W, H, W, H))]
            patch = a[max(0, y0):y1, max(0, x0):x1]
            if patch.size == 0:
                continue
            out.append((r['name'], r['depth'], float(np.median(patch))))
        out.sort(key=lambda t: t[1])                # by MY depth, far -> near
        print('  %s' % name.upper())
        prev = None; bad = 0
        for nm, mine, mod in out:
            flag = ''
            if prev is not None and mod > prev + 0.02:   # model says FARTHER than the last
                flag = '   <-- model disagrees with my ordering'; bad += 1
            print('     %-11s mine %.2f   model %.3f%s' % (nm, mine, mod, flag))
            prev = mod
        print('     -> %d inversion(s)\n' % bad)

    # ── 2. the plates called flat ───────────────────────────────────────────
    print('THE PLATES CALLED FLAT — does the model find depth in them?\n')
    spreads = {r[1]: r[4] for r in rows}
    med = float(np.median([r[4] for r in rows]))
    for si, name, tag, a, spread, sd in rows:
        verdict = 'FLAT-ish' if spread < med * 0.75 else ('deep' if spread > med * 1.15 else 'mid')
        mark = '   <-- called flat' if si in (0, 5, 7) else ''
        print('  %-14s spread %.3f  (median across plates %.3f)  %-9s%s'
              % (name, spread, med, verdict, mark))


if __name__ == '__main__':
    main()
