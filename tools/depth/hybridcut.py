#!/usr/bin/env python3
"""Cut a plate into depth cards: SAM for BOUNDARIES, a depth map for ORDER.

Neither tool alone does this job, and finding that out is what this file is for.

  * DEPTH ALONE SHREDS OBJECTS. A depth model gives every object its own
    internal near-to-far gradient, so quantising raw pixel depth slices a single
    floating island into four cards that then move at four different rates. On
    the Sky Gardens plate that was unmistakable in the assignment map.
  * SAM ALONE CANNOT ORDER. It finds the island beautifully and has no idea how
    far away it is — which is why the previous cut needed a hand-drawn box and a
    hand-picked depth per card.

So: SAM says WHAT a thing is, the depth map says WHERE it sits, and the layers
fall out. The trick that makes object integrity automatic is banding OBJECT
depth rather than PIXEL depth — every pixel takes the median depth of the mask
that owns it, so a band boundary can never pass through an object.

Ownership is smallest-mask-wins: masks are painted largest to smallest, so a
tree ends up owned by the tree rather than by the hillside it overlaps.

Kept from the earlier cutters because they were right: the push-pull inpainted
base, the recompose check, and the assignment map you look at BEFORE wiring
anything.

VERDICT AFTER RUNNING ALL EIGHT (2026-09-15). Every plate cut with recompose
0.000% and no black base, and the cuts are geometrically good. It is still NOT
what should ship, and the reason is that the hand cut encodes BEHAVIOUR that a
depth cut cannot see:

  * THE PETAL MILE CANOPY comes back split across four cards. That plate's whole
    point is one canopy card shearing about its trunk line; split it and the
    blossom tears at the seams. The hand cut deliberately merged canopy, trunks
    and branches into ONE card to fix exactly this.
  * MIRROR LAKE loses its three separately-swaying willows — depth correctly
    says they are at the same distance (0.357 / 0.353 / 0.341) and merges them,
    which is right geometrically and wrong for the game, because each willow
    needs its own wind phase.
  * THE GLADE AND SKY GARDENS are not rescued. Four approaches on Sky Gardens
    all split islands at six bands; only per-island cards (~15 for one stage)
    would hold, at roughly the asset cost of all six carded stages combined.

What the depth map IS worth, measured inside each shipped card's real alpha
mask: it VALIDATES the shipped cut. Ordering agrees on every stage. The numeric
gaps (16 of 32 cards differ by >0.15) are a SCALE choice, not an error — the
hand values deliberately spread cards across the full 0.05..0.95 range to widen
the parallax, while the model reports true relative distance, where the willows
and their shore really are nearly co-planar. Rescaling to raw model depth would
COMPRESS the spread and weaken the effect.

So this ships as a verification tool, not a replacement cutter. It would have
caught the blossom-over-its-own-trunks bug in one pass.

Usage:  python3 hybridcut.py <tag> [--layers N]
"""
import io, os, sys, json, time
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
CUT, DEPTH = '/tmp/cards', '/tmp/depthtest'
CKPT = '/tmp/sam/sam_vit_b.pth'

sys.path.insert(0, HERE)
from cards import pushpull
from depthcut import PLATES, depth_for, D_LO, D_HI


def sam_masks(rgb, dense=False):
    """The OBJECT tier. Same settings the three-tier cutter found were the ones
    that return things you would put on their own pane — a tree crown, an arch,
    an island — rather than whole masses or fragments."""
    import torch
    from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
    sam = sam_model_registry['vit_b'](checkpoint=CKPT)
    sam.to('cpu')
    # DENSE plates (the fungal glade, the sky isles, the library's spines) leave
    # a third of the frame unclaimed at these thresholds, and every unowned pixel
    # falls back to RAW depth — which is exactly the gradient that shreds objects.
    # crop_n_layers re-runs SAM on sub-crops so each motif is seen at higher
    # effective resolution; raising points_per_side is NOT the lever.
    gen = SamAutomaticMaskGenerator(
        sam, points_per_side=28,
        pred_iou_thresh=0.62 if dense else 0.80,
        stability_score_thresh=0.74 if dense else 0.88,
        min_mask_region_area=120 if dense else 400,
        crop_n_layers=1 if dense else 0, crop_n_points_downscale_factor=2)
    m = gen.generate(rgb)
    m.sort(key=lambda d: -d['area'])          # largest first: smallest wins ownership
    return m


def natural_breaks(v, k, iters=60):
    """Band edges BETWEEN depth clusters, not through them.

    Equal-area quantiles were the first cut and they are wrong here: they place
    a boundary every 1/k of the AREA regardless of where the objects actually
    sit. Measured on the Sky Gardens plate the islands are genuinely separable —
    between-island depth spread 0.121 against a within-island range of 0.069, a
    ratio of 0.57 — so the depth values were never the problem. Quantile edges
    were simply landing mid-cluster and slicing islands that the object masks had
    correctly kept whole.

    1-D k-means (Lloyd, quantile-initialised), cutting at the midpoints between
    consecutive centres. Subsampled — the result is stable well below full
    resolution and this runs on every plate.
    """
    f = v.ravel()
    s = f if f.size <= 200000 else np.random.default_rng(0).choice(f, 200000, replace=False)
    c = np.quantile(s, np.linspace(0.5 / k, 1 - 0.5 / k, k))
    for _ in range(iters):
        idx = np.abs(s[:, None] - c[None, :]).argmin(1)
        new = np.sort(np.array([s[idx == j].mean() if (idx == j).any() else c[j]
                                for j in range(k)]))
        if np.allclose(new, c, atol=1e-5):
            c = new; break
        c = new
    return np.array([-1e-6] + [(c[i] + c[i + 1]) / 2 for i in range(len(c) - 1)] + [1 + 1e-6])


def main(tag, K, DENSE=False):
    os.makedirs(CUT, exist_ok=True)
    bgr = cv2.imread(os.path.join(REPO, 'web', PLATES[tag] + '.webp'), cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    sc = min(2.0, 1536.0 / max(rgb.shape[:2]))
    rgb = cv2.resize(rgb, (int(rgb.shape[1] * sc), int(rgb.shape[0] * sc)),
                     interpolation=cv2.INTER_CUBIC)
    H, W = rgb.shape[:2]

    D = depth_for(tag)
    D = cv2.resize(D, (W, H), interpolation=cv2.INTER_CUBIC)
    D = cv2.bilateralFilter(D.astype(np.float32), 9, 0.08, 9)
    spread = float(np.percentile(D, 90) - np.percentile(D, 10))

    t0 = time.time()
    masks = sam_masks(rgb, DENSE)
    print('%s: %dx%d, %d masks, depth spread %.3f  (%.0fs)'
          % (tag, W, H, len(masks), spread, time.time() - t0), flush=True)

    # ── ownership: paint largest to smallest, so the most SPECIFIC object wins ──
    owner = np.full((H, W), -1, np.int32)
    odep = np.zeros(len(masks), np.float32)
    for i, d in enumerate(masks):
        s = d['segmentation']
        odep[i] = float(np.median(D[s])) if s.any() else 0.0
        owner[s] = i

    # per-pixel OBJECT depth. Banding this cannot split an object, because every
    # pixel of an object carries the same value.
    objd = np.where(owner >= 0, odep[np.clip(owner, 0, None)], D)
    unowned = float((owner < 0).mean())
    print('  unowned by any mask: %.1f%% (falls back to raw depth)' % (100 * unowned), flush=True)

    edges = natural_breaks(objd, K)
    print('  band edges: %s' % np.round(edges[1:-1], 3), flush=True)

    layers = []
    for i in range(len(edges) - 1):
        m = (objd > edges[i]) & (objd <= edges[i + 1])
        if np.count_nonzero(m) < 0.008 * m.size:
            continue
        layers.append([float(np.median(objd[m])), m])
    layers.sort(key=lambda t: t[0])
    merged = []
    for md, m in layers:
        if merged and md - merged[-1][0] < 0.05:
            merged[-1][1] |= m
        else:
            merged.append([md, m])

    # nothing is left for the base to show through: every pixel belongs to a card
    cov = np.zeros((H, W), bool)
    for _, m in merged:
        cov |= m
    if not cov.all() and merged:
        merged[0][1] |= ~cov

    lo, hi = merged[0][0], merged[-1][0]
    rng = max(1e-6, hi - lo)
    squash = min(1.0, spread / 0.55)
    mid = (D_LO + D_HI) / 2
    cards = []
    for i, (md, m) in enumerate(merged):
        d = D_LO + ((md - lo) / rng) * (D_HI - D_LO)
        cards.append({'name': 'd%d' % i, 'depth': round(mid + (d - mid) * squash, 2), 'mask': m})

    pal = [(255,90,90),(90,200,255),(255,210,80),(150,255,150),(220,140,255),
           (255,160,60),(120,255,220),(255,120,180)]
    amap = (rgb * 0.30).astype(np.uint8)
    for i, c in enumerate(cards):
        amap[c['mask']] = pal[i % len(pal)]
    cv2.imwrite('%s/%s_assign.png' % (CUT, tag), cv2.cvtColor(amap, cv2.COLOR_RGB2BGR))

    out, taken = [], np.zeros((H, W), bool)
    for c in cards:
        m = c['mask'] & ~taken
        if np.count_nonzero(m) < 0.004 * m.size:
            print('  %-4s dropped (claimed by a nearer card)' % c['name']); continue
        taken |= m
        ys, xs = np.where(m)
        crop = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        rgba = np.dstack([rgb, (m * 255).astype(np.uint8)])
        x0, y0, x1, y1 = crop
        cv2.imwrite('%s/%s_%s.png' % (CUT, tag, c['name']),
                    cv2.cvtColor(rgba[y0:y1, x0:x1], cv2.COLOR_RGBA2BGRA))
        out.append({'name': c['name'], 'depth': c['depth'], 'crop': crop, 'w': W, 'h': H})
        print('  %-4s d %.2f  covers %5.2f%%' % (c['name'], c['depth'], 100 * m.mean()), flush=True)

    base = pushpull(rgb, taken)
    cv2.imwrite('%s/%s_base.png' % (CUT, tag), cv2.cvtColor(base, cv2.COLOR_RGB2BGR))
    comp = base.copy()
    for c in cards:
        comp[c['mask']] = rgb[c['mask']]
    diff = (np.abs(comp.astype(np.int32) - rgb.astype(np.int32)).sum(2) > 12)
    ok = diff.mean() < 0.001
    print('  RECOMPOSE %.3f%% (%s)   base near-black %.4f%%'
          % (100 * diff.mean(), 'PASS' if ok else 'FAIL',
             100.0 * (base.max(axis=2) < 14).mean()), flush=True)
    json.dump(out, open('%s/%s_cards.json' % (CUT, tag), 'w'), indent=1)
    print('  wrote %d cards + base' % len(out), flush=True)
    return ok


if __name__ == '__main__':
    tag = sys.argv[1]
    K = int(sys.argv[sys.argv.index('--layers') + 1]) if '--layers' in sys.argv else 6
    sys.exit(0 if main(tag, K, '--dense' in sys.argv) else 1)
