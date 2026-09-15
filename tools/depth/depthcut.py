#!/usr/bin/env python3
"""Cut a plate into depth cards using a DEPTH MAP instead of hand-drawn boxes.

This replaces the region specs. The old cutter needed me to draw a box per card
and pick its depth by eye; a depth model measures both. What that buys, in order
of how much it mattered:

  * THE GROUND-PLANE RULE COMES OUT FOR FREE. The hard-won rule from the SAM
    re-cut — a thing and the ground it stands on belong on the same card — is
    just "things at the same distance share a layer", which is what banding a
    depth map does by construction. It cannot put blossom on a different card
    from its own trunks, because they are at the same depth.
  * DEPTH BANDS ARE NOT HORIZONTAL BANDS. This is the whole reason Sky Gardens
    gets cut now. An island bottom-left and an island top-right at the same
    distance land on ONE card; islands at different distances land on different
    cards. Slicing that plate into horizontal strips was wrong; slicing it by
    distance is right.
  * Every card's `d` is MEASURED, not chosen. 30 of 31 of my hand-picked depths
    already agreed with the model (see depthmap_probe.py), so this mostly
    confirms them — but it removes the judgement call.

Kept from the SAM cutter, because they were right: the push-pull inpainted base,
the recompose check, the assignment map you look at before wiring anything, and
the per-card pivot that pack.py measures.

Usage:  python3 depthcut.py <tag> [--bands N]
"""
import io, os, sys, json
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
CUT  = '/tmp/cards'
DEPTH = '/tmp/depthtest'

sys.path.insert(0, HERE)
from cards import pushpull            # same inpaint, same fallback behaviour

PLATES = {
    'library': '7026911858d1', 'meadow': '1fa28057a711', 'petal': '44187ebf6a44',
    'rose': 'afcfb1d92476',    'lake':   'da0a81c9b45f', 'glade': '9d4d20ccbac3',
    'golden': '14ab4c11ab60',  'skyg':   '1ae0890e08c3', 'encore': 'a4a908d52b36',
}
# A plate with genuinely little depth should not have its parallax stretched to
# the full range just because the model normalises per image. Bands are chosen
# on the plate's own histogram, but `d` is compressed toward the middle when the
# plate is shallow, so a flat-ish painting reads as flat-ish rather than as a
# diorama.
D_LO, D_HI = 0.05, 0.95


def depth_for(tag):
    """Depth map at plate resolution, 0 far .. 1 near. Computed once, cached."""
    p = os.path.join(DEPTH, '%s_depth.npy' % tag)
    if os.path.exists(p):
        return np.load(p)
    from transformers import pipeline
    from PIL import Image
    os.makedirs(DEPTH, exist_ok=True)
    pipe = pipeline('depth-estimation',
                    model='depth-anything/Depth-Anything-V2-Small-hf', device=-1)
    im = Image.open(os.path.join(REPO, 'web', PLATES[tag] + '.webp')).convert('RGB')
    a = np.asarray(pipe(im)['depth']).astype(np.float32)
    a = (a - a.min()) / max(1e-6, float(np.ptp(a)))   # np.ptp: NumPy 2 dropped the method
    np.save(p, a)
    return a


def bands(D, k):
    """Split the depth histogram into k layers on its own quantiles.

    Quantiles rather than equal-width, because equal-width puts most of a plate
    into one band whenever the depth histogram is lopsided — which it is on
    every plate with a big sky.
    """
    qs = np.quantile(D, np.linspace(0, 1, k + 1))
    qs[0], qs[-1] = -1e-6, 1 + 1e-6
    # collapse duplicate edges (a plate can be flat enough that quantiles tie)
    out = [qs[0]]
    for q in qs[1:]:
        if q > out[-1] + 1e-4:
            out.append(q)
    return np.array(out)


def clean(mask, minfrac):
    """Despeckle a band without eroding real edges.

    Open then close with a small kernel, then drop components under minfrac of
    the plate — those are depth-estimator noise, and each one would otherwise
    become its own hole in the base plate.
    """
    m = mask.astype(np.uint8)
    k = np.ones((5, 5), np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, k)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros_like(m, bool)
    lim = minfrac * m.size
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= lim:
            keep |= (lab == i)
    return keep


def main(tag, k):
    os.makedirs(CUT, exist_ok=True)
    bgr = cv2.imread(os.path.join(REPO, 'web', PLATES[tag] + '.webp'), cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    # SAM worked at 2x; the depth map is native, and there is no reason to
    # upsample — the cut is only as sharp as the depth map is.
    H, W = rgb.shape[:2]
    D = depth_for(tag)
    if D.shape != (H, W):
        D = cv2.resize(D, (W, H), interpolation=cv2.INTER_CUBIC)
    # Edge-preserving smooth: kills the speckle that would fragment a band
    # without rounding off the silhouettes the cards are cut on.
    D = cv2.bilateralFilter(D, 9, 0.08, 9)
    spread = float(np.percentile(D, 90) - np.percentile(D, 10))
    print('%s: plate %dx%d, depth spread %.3f' % (tag, W, H, spread))

    edges = bands(D, k)
    print('  %d band edges: %s' % (len(edges) - 1, np.round(edges, 3)))

    raw = []
    for i in range(len(edges) - 1):
        m = (D > edges[i]) & (D <= edges[i + 1])
        m = clean(m, 0.004)
        if np.count_nonzero(m) < 0.008 * m.size:
            continue
        raw.append((float(np.median(D[m])), m))
    raw.sort(key=lambda t: t[0])                   # far -> near

    # Merge neighbours that ended up at nearly the same distance: two cards
    # 0.02 apart move together anyway, so they are one card and one request.
    merged = []
    for md, m in raw:
        if merged and md - merged[-1][0] < 0.05:
            merged[-1] = (merged[-1][0], merged[-1][1] | m)
        else:
            merged.append((md, m))

    # Exclusivity, far to near: a pixel belongs to the NEAREST band claiming it.
    taken = np.zeros((H, W), bool)
    cards = []
    for idx, (md, m) in enumerate(reversed(merged)):
        m = m & ~taken
        if np.count_nonzero(m) < 0.004 * m.size:
            continue
        taken |= m
        cards.append({'md': md, 'mask': m})
    cards.sort(key=lambda c: c['md'])              # emit far -> near

    # Anything the bands missed goes to the FARTHEST card, not the base: a hole
    # in the base is a hole you see through when a card moves.
    leftover = ~taken
    if leftover.any() and cards:
        cards[0]['mask'] |= leftover
        taken |= leftover

    # measured depth -> the game's d, compressed when the plate is shallow
    lo, hi = cards[0]['md'], cards[-1]['md']
    rng = max(1e-6, hi - lo)
    squash = min(1.0, spread / 0.55)               # shallow plate, shallow parallax
    mid = (D_LO + D_HI) / 2
    for i, c in enumerate(cards):
        t = (c['md'] - lo) / rng
        d = D_LO + t * (D_HI - D_LO)
        c['depth'] = round(mid + (d - mid) * squash, 2)
        c['name'] = 'd%d' % i

    pal = [(255,90,90),(90,200,255),(255,210,80),(150,255,150),(220,140,255),
           (255,160,60),(120,255,220),(255,120,180)]
    amap = (rgb * 0.30).astype(np.uint8)
    for i, c in enumerate(cards):
        amap[c['mask']] = pal[i % len(pal)]
    cv2.imwrite('%s/%s_assign.png' % (CUT, tag), cv2.cvtColor(amap, cv2.COLOR_RGB2BGR))

    out = []
    for c in cards:
        m = c['mask']
        ys, xs = np.where(m)
        crop = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        rgba = np.dstack([rgb, (m * 255).astype(np.uint8)])
        x0, y0, x1, y1 = crop
        cv2.imwrite('%s/%s_%s.png' % (CUT, tag, c['name']),
                    cv2.cvtColor(rgba[y0:y1, x0:x1], cv2.COLOR_RGBA2BGRA))
        out.append({'name': c['name'], 'depth': c['depth'], 'crop': crop, 'w': W, 'h': H})
        print('  %-4s d %.2f  covers %5.2f%%' % (c['name'], c['depth'], 100 * m.mean()))

    base = pushpull(rgb, taken)
    cv2.imwrite('%s/%s_base.png' % (CUT, tag), cv2.cvtColor(base, cv2.COLOR_RGB2BGR))

    comp = base.copy()
    for c in cards:
        comp[c['mask']] = rgb[c['mask']]
    diff = (np.abs(comp.astype(np.int32) - rgb.astype(np.int32)).sum(2) > 12)
    ok = diff.mean() < 0.001
    print('  RECOMPOSE diff %.3f%%  (%s)' % (100 * diff.mean(), 'PASS' if ok else 'FAIL'))
    black = 100.0 * (base.max(axis=2) < 14).mean()
    print('  base near-black %.4f%%' % black)

    json.dump(out, open('%s/%s_cards.json' % (CUT, tag), 'w'), indent=1)
    print('  wrote %d cards + base' % len(out))
    return ok


if __name__ == '__main__':
    tag = sys.argv[1]
    k = 6
    if '--bands' in sys.argv:
        k = int(sys.argv[sys.argv.index('--bands') + 1])
    sys.exit(0 if main(tag, k) else 1)
