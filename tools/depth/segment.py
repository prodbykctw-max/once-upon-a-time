#!/usr/bin/env python3
"""
Cut a flat painted backdrop into depth cards.

Follows the method in prodbyKCTW's "Techniques" doc, section 2, rather than
improvising:
  * two passes, coarse then fine, merged at IoU < 0.75
  * text is found by lowering the AREA FLOOR and CONFIDENCE, never by raising
    the sampling grid (measured there: 28 -> 48 moved coverage 85.0 -> 86.0
    while the lettering stayed missing)
  * coverage is judged against the NEGATIVE space, scored by local contrast, so
    flat sky is not counted as a miss

int32 casting is not optional. This box runs NumPy 2.4, where an int16 array
times a Python int stays int16, so r*299 + g*587 + b*114 wraps negative for any
red above 109. That bug is why this file weights luminance in int32 only.
"""
import sys, os, json, numpy as np, cv2, torch
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

def gen(sam, coarse):
    if coarse:
        return SamAutomaticMaskGenerator(
            sam, points_per_side=28, pred_iou_thresh=0.88,
            stability_score_thresh=0.95, min_mask_region_area=1800,
            crop_n_layers=0)
    # FINE: same grid on purpose. The doc is explicit that the grid is not what
    # finds lettering — the area floor and the confidence bar are.
    return SamAutomaticMaskGenerator(
        sam, points_per_side=28, pred_iou_thresh=0.68,
        stability_score_thresh=0.80, min_mask_region_area=60,
        crop_n_layers=0)

def main(src, tag):
    os.makedirs(OUT, exist_ok=True)
    bgr = cv2.imread(src, cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    # SAM sees more on a larger plate; these are only 768x384.
    rgb = cv2.resize(rgb, (rgb.shape[1] * 2, rgb.shape[0] * 2), interpolation=cv2.INTER_CUBIC)
    H, W = rgb.shape[:2]
    print(f'{tag}: plate {W}x{H}', flush=True)

    sam = sam_model_registry['vit_b'](checkpoint=CKPT)
    sam.to('cpu')

    res = {}
    for name in ('coarse', 'fine'):
        m = gen(sam, name == 'coarse').generate(rgb)
        m.sort(key=lambda d: -d['area'])
        res[name] = m
        cov = np.zeros((H, W), bool)
        for d in m:
            cov |= d['segmentation']
        print(f'{tag}: {name:6s} {len(m):4d} masks, coverage {100*cov.mean():.1f}%', flush=True)

    # merge — keep every coarse mask, add a fine one only if it is not already
    # saying the same thing as some coarse mask
    merged = list(res['coarse'])
    added = 0
    for d in res['fine']:
        s = d['segmentation']
        if all(iou(s, c['segmentation']) < 0.75 for c in res['coarse']):
            merged.append(d); added += 1
    cov = np.zeros((H, W), bool)
    for d in merged:
        cov |= d['segmentation']
    print(f'{tag}: merged {len(merged):4d} masks (+{added} fine), coverage {100*cov.mean():.1f}%', flush=True)

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
    main(sys.argv[1], sys.argv[2])
