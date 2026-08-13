#!/usr/bin/env python3
"""
Cut a flat painted backdrop into depth cards.

Follows the method in prodbyKCTW's "Techniques" doc, section 2, rather than
improvising:
  * COARSE, MEDIUM and FINE (client, 2026-08-13: "let's do the coarse medium
    fine recut"), cascaded and merged at IoU < 0.75. The middle tier is the one
    that matters for depth cards: coarse returns whole masses and fine returns
    fragments, while a usable card is an OBJECT — one tree, one hedge, one arch.
    Two tiers meant those had to be assembled out of fragments or carved out of
    a mass, which is what made the layering read wrong.
  * text is found by lowering the AREA FLOOR and CONFIDENCE, never by raising
    the sampling grid (measured there: 28 -> 48 moved coverage 85.0 -> 86.0
    while the lettering stayed missing)
  * coverage is judged against the NEGATIVE space, scored by local contrast, so
    flat sky is not counted as a miss

int32 casting is not optional. This box runs NumPy 2.4, where an int16 array
times a Python int stays int16, so r*299 + g*587 + b*114 wraps negative for any
red above 109. That bug is why this file weights luminance in int32 only.
"""
import sys, os, json, time, numpy as np, cv2, torch

TIERS = ('coarse', 'medium', 'fine')
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

CKPT = '/tmp/sam/sam_vit_b.pth'
OUT  = '/tmp/cards'

def luma(rgb):
    """Rec.601 luminance. CAST FIRST — see module docstring."""
    a = rgb.astype(np.int32)
    return (a[..., 0] * 299 + a[..., 1] * 587 + a[..., 2] * 114) // 1000

def iou(a, b):
    inter = np.count_nonzero(a & b)
    if not inter:
        return 0.0
    return inter / float(np.count_nonzero(a | b))

def gen(sam, tier, dense=False):
    """One generator per tier. `dense` adds crop_n_layers on top of the tier's
    own thresholds — it is NOT a tier of its own.

    Getting that wrong cost a plate: the first three-tier version returned the
    same dense generator for both medium and fine, so on the Golden Hour they
    produced byte-identical output (601 masks each, fine contributing 0 new) and
    the fine pass burned 400s duplicating the medium one.

    crop_n_layers re-runs SAM on sub-CROPS, so each region is seen at higher
    EFFECTIVE resolution rather than just sampled more often. That is the lever
    for dense plates (library spines, fungal glade, sunflower field, sky isles),
    which came in at 62-74% where open ones hit 91-94%. Raising points_per_side
    is NOT the lever — the doc measured 28 -> 48 moving coverage 85.0 -> 86.0
    while the lettering stayed missing.
    """
    if tier == 'coarse':
        iou, stab, area = 0.88, 0.95, 1800
    elif tier == 'medium':
        # THE OBJECT TIER. Its area floor is the whole point: 400px at this scale
        # is about one tree crown or one arch, big enough to be a thing you would
        # put on its own pane and small enough not to be the entire treeline.
        iou, stab, area = 0.80, 0.88, 400
    else:
        # FINE: same grid on purpose. The doc is explicit that the grid is not
        # what finds small detail — the area floor and confidence bar are.
        iou, stab, area = (0.62, 0.74, 25) if dense else (0.68, 0.80, 60)
    return SamAutomaticMaskGenerator(
        sam, points_per_side=28, pred_iou_thresh=iou,
        stability_score_thresh=stab, min_mask_region_area=area,
        crop_n_layers=(1 if (dense and tier != 'coarse') else 0),
        crop_n_points_downscale_factor=2)

def main(src, tag, dense=False):
    global DENSE
    DENSE = dense
    os.makedirs(OUT, exist_ok=True)
    bgr = cv2.imread(src, cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    # SAM sees more on a larger plate; these are only 768x384.
    sc = min(2.0, 1536.0 / max(rgb.shape[0], rgb.shape[1]))
    rgb = cv2.resize(rgb, (int(rgb.shape[1]*sc), int(rgb.shape[0]*sc)), interpolation=cv2.INTER_CUBIC)
    H, W = rgb.shape[:2]
    print(f'{tag}: plate {W}x{H}', flush=True)

    sam = sam_model_registry['vit_b'](checkpoint=CKPT)
    sam.to('cpu')

    res = {}
    for name in TIERS:
        t0 = time.time()
        m = gen(sam, name, DENSE).generate(rgb)
        m.sort(key=lambda d: -d['area'])
        res[name] = m
        cov = np.zeros((H, W), bool)
        for d in m:
            cov |= d['segmentation']
        print(f'{tag}: {name:6s} {len(m):4d} masks, coverage {100*cov.mean():.1f}%'
              f'  ({time.time()-t0:.0f}s)', flush=True)

    # CASCADE. Each tier is compared against everything KEPT SO FAR, not just
    # against coarse. With only two tiers that distinction did not exist; with
    # three it does, and skipping it lets medium and fine both contribute their
    # own copy of the same object.
    merged = list(res['coarse'])
    for name in TIERS[1:]:
        added = 0
        for d in res[name]:
            s2 = d['segmentation']
            if all(iou(s2, c['segmentation']) < 0.75 for c in merged):
                merged.append(d); added += 1
        print(f'{tag}: +{added:4d} from {name}', flush=True)
    cov = np.zeros((H, W), bool)
    for d in merged:
        cov |= d['segmentation']
    print(f'{tag}: merged {len(merged):4d} masks, coverage {100*cov.mean():.1f}%', flush=True)

    # NEGATIVE SPACE, scored by local contrast. Reviewing what was FOUND only
    # ever shows what was found; this is the view that shows the misses.
    L = luma(rgb).astype(np.float32)
    contrast = cv2.dilate(L, np.ones((9, 9), np.uint8)) - cv2.erode(L, np.ones((9, 9), np.uint8))
    miss = (~cov)
    interesting = miss & (contrast > 26)
    print(f'{tag}: unclaimed {100*miss.mean():.1f}%  of which HIGH-CONTRAST (real misses) {100*interesting.mean():.2f}%', flush=True)

    vis = (rgb * 0.25).astype(np.uint8)
    vis[interesting] = (255, 40, 40)
    vis[miss & ~interesting] = (60, 60, 90)
    cv2.imwrite(f'{OUT}/{tag}_negative.png', cv2.cvtColor(vis, cv2.COLOR_RGB2BGR))

    np.save(f'{OUT}/{tag}_masks.npy',
            np.stack([d['segmentation'] for d in merged]).astype(bool))
    json.dump([{'area': int(d['area']), 'bbox': [int(v) for v in d['bbox']]} for d in merged],
              open(f'{OUT}/{tag}_meta.json', 'w'))
    print(f'{tag}: saved {len(merged)} masks', flush=True)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], len(sys.argv) > 3)
