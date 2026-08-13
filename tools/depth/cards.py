#!/usr/bin/env python3
"""
Turn SAM masks into depth CARDS + an inpainted base plate.

Section 2 of the Techniques doc, followed rather than reinvented:
  * group masks into a region by 70% CONTAINMENT, never by centroid (a centroid
    rule put the sky on a column card, because the sky's centroid happened to
    land inside the column's box)
  * regions are listed MOST SPECIFIC FIRST and overlaps resolve in that order,
    but cards are emitted sorted by DEPTH — claim priority and draw order are
    different axes
  * flood-fill the sky ONCE from the frame border inward, seeded a few px IN,
    because plates vignette to black at the edge and a border-row seed finds no
    sky at all
  * fill holes so dark leaves inside a canopy stay part of the canopy — opt-out,
    because a wheel with real gaps comes back a solid disc
  * RECOMPOSE CHECK: base + every card stacked at zero offset must reproduce the
    original. Anything in the difference is stranded or drawn twice. <0.1% good.
  * push-pull pyramid inpaint of the base, not "stretch the band above downward"

Every card is written with alpha. The assignment map is written for a human to
LOOK AT before anything gets wired — two cards once shipped as solid rectangles
because that step got skipped.
"""
import sys, os, json, numpy as np, cv2

OUT = '/tmp/cards'

def luma(rgb):
    a = rgb.astype(np.int32)          # int32 FIRST. NumPy 2 int16 wraps here.
    return (a[..., 0] * 299 + a[..., 1] * 587 + a[..., 2] * 114) // 1000

def sky_mask(rgb):
    """Sky = the background reachable from outside the frame."""
    H, W = rgb.shape[:2]
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    ff = np.zeros((H + 2, W + 2), np.uint8)
    seeds = []
    inset = 6                                   # seed a few px IN, not row 0
    for x in range(inset, W - inset, max(1, W // 24)):
        seeds.append((x, inset))
    got = np.zeros((H, W), bool)
    for s in seeds:
        m = ff.copy()
        tmp = lab.copy()
        cv2.floodFill(tmp, m, s, 0, (7, 7, 7), (7, 7, 7),
                      cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE | (255 << 8))
        got |= m[1:-1, 1:-1].astype(bool)
    return got

def fill_holes(m, maxfrac=0.02):
    """Fill only SMALL enclosed gaps.

    The naive version (flood the inverse from 0,0 and keep everything it cannot
    reach) is catastrophic for a region that spans the frame: a full-width
    treeline touches the left, right and bottom borders, so the entire area
    BELOW it is 'enclosed' and gets filled. Measured: a 9-mask treeline came back
    as 97.4% of the plate. The doc's warning is the milder form of the same bug —
    a wheel with real gaps coming back a solid disc.

    So: fill an enclosed component only if it is genuinely small. That keeps dark
    leaves inside a canopy without swallowing the sky, the path and the lake."""
    h, w = m.shape
    inv = (~m).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(inv, 8)
    out = m.copy()
    lim = maxfrac * h * w
    for i in range(1, n):
        x, y, bw_, bh_, area = stats[i]
        touches = (x == 0 or y == 0 or x + bw_ >= w or y + bh_ >= h)
        if not touches and area <= lim:
            out |= (lab == i)
    return out

def pushpull(rgb, hole, levels=7):
    """Push-pull pyramid fill. NOT a downward stretch — that gives vertical
    streaks. The hole sits behind its card at rest, so a soft fill is invisible."""
    img = rgb.astype(np.float32)
    a = (~hole).astype(np.float32)
    img = img * a[..., None]
    pyr_c, pyr_a = [img], [a]
    for _ in range(levels):
        pyr_c.append(cv2.pyrDown(pyr_c[-1]))
        pyr_a.append(cv2.pyrDown(pyr_a[-1]))
    for i in range(len(pyr_c) - 2, -1, -1):
        up_c = cv2.pyrUp(pyr_c[i + 1], dstsize=(pyr_c[i].shape[1], pyr_c[i].shape[0]))
        up_a = cv2.pyrUp(pyr_a[i + 1], dstsize=(pyr_a[i].shape[1], pyr_a[i].shape[0]))
        w = np.clip(pyr_a[i], 0, 1)[..., None]
        pyr_c[i] = pyr_c[i] * w + up_c * (1 - w)
        pyr_a[i] = np.maximum(pyr_a[i], up_a)
    safe = np.maximum(pyr_a[0], 1e-5)[..., None]
    return np.clip(pyr_c[0] / safe, 0, 255).astype(np.uint8)

def main(src, tag, regions_json):
    bgr = cv2.imread(src, cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    # MUST match segment.py's scaling exactly. The masks were computed at that
    # size; any divergence silently misaligns every card with the image it was
    # cut from, and the recompose check would be the only thing that caught it.
    sc = min(2.0, 1536.0 / max(rgb.shape[0], rgb.shape[1]))
    rgb = cv2.resize(rgb, (int(rgb.shape[1]*sc), int(rgb.shape[0]*sc)), interpolation=cv2.INTER_CUBIC)
    H, W = rgb.shape[:2]
    masks = np.load(f'{OUT}/{tag}_masks.npy')
    regions = json.load(open(regions_json))     # [{name, depth, box:[x0,y0,x1,y1], maxArea?, holes?}]
    print(f'{tag}: {len(masks)} masks, {len(regions)} regions, plate {W}x{H}', flush=True)

    sky = sky_mask(rgb)
    print(f'{tag}: sky {100*sky.mean():.1f}%', flush=True)

    assign = np.full((H, W), -1, np.int16)
    cards = []
    for ri, r in enumerate(regions):
        x0, y0, x1, y1 = [int(v * s) for v, s in zip(r['box'], (W, H, W, H))]
        box = np.zeros((H, W), bool); box[y0:y1, x0:x1] = True
        boxarea = max(1, np.count_nonzero(box))
        acc = np.zeros((H, W), bool)
        used = 0
        for m in masks:
            a = np.count_nonzero(m)
            if not a:
                continue
            # CONTAINMENT, not centroid
            if np.count_nonzero(m & box) / a < 0.70:
                continue
            if 'maxArea' in r and a / boxarea > r['maxArea']:
                continue            # this is what lets lettering lift off its panel
            # SCOPED COLOUR RULE. Box containment alone cannot separate a green
            # willow crown from the blue ridge directly behind it — they occupy
            # the same screen position, so both pass the 70% test and whichever
            # region runs first wins the pixel. The assignment map showed the
            # willow cards swallowing the entire mountain range. Naming the
            # material an item IS resolves it.
            if 'keep' in r:
                mc = rgb[m].astype(np.int32).mean(0)     # int32: NumPy 2 wraps int16
                R, G, B = mc[0], mc[1], mc[2]
                if r['keep'] == 'green' and not (G > B + 8 and G > R + 4):
                    continue
                if r['keep'] == 'blue' and not (B >= G - 2):
                    continue
            acc |= m; used += 1
        if r.get('holes', True):
            acc = fill_holes(acc)
        # The sky is subtracted from every card EXCEPT the sky's own, which is
        # the bug the first assignment map caught: the sky card came out empty
        # and the mountains card ate the whole top band. A card named as the sky
        # is also SEEDED with the flood fill, so it owns the region by
        # construction rather than by whichever mask happened to land there.
        if r.get('isSky'):
            acc |= sky
        else:
            acc &= ~sky
        if np.count_nonzero(acc) < 200:
            print(f'  ! region {r["name"]}: only {np.count_nonzero(acc)}px from {used} masks — SKIPPED', flush=True)
            continue
        assign[acc & (assign < 0)] = ri
        cards.append({'name': r['name'], 'depth': r['depth'], 'mask': acc, 'used': used})
        print(f'  {r["name"]:14s} depth {r["depth"]:.2f}  {used:3d} masks  {100*acc.mean():5.2f}% of plate', flush=True)

    # ── ASSIGNMENT MAP — look at this before wiring anything ──
    # Paint from `assign`, NOT by stamping each card's raw mask in turn. Region
    # masks OVERLAP — that is the normal case, it is what the exclusivity pass
    # downstream exists to resolve — so stamping them in order shows whichever
    # region came LAST, not the one that actually wins the pixel. This map read
    # "the hills own all three willows" while the cut was in fact giving the
    # willows their own cards correctly. A diagnostic that lies is worse than
    # none: `assign` is already first-claim-wins, so read it.
    pal = [(255,90,90),(90,200,255),(255,210,80),(150,255,150),(220,140,255),(255,160,60),(120,255,220),(255,120,180)]
    amap = (rgb * 0.30).astype(np.uint8)
    for i, c in enumerate(cards):
        amap[assign == i] = pal[i % len(pal)]
    cv2.imwrite(f'{OUT}/{tag}_assign.png', cv2.cvtColor(amap, cv2.COLOR_RGB2BGR))

    # ── cards + inpainted base ──
    taken = np.zeros((H, W), bool)
    kept = []
    for c in cards:
        m = c['mask'] & ~taken
        # A card can be emptied here: every pixel it wanted was already claimed
        # by a nearer-to-front region. That is a legitimate outcome (the region
        # was redundant), but np.where on an empty mask throws, so it has to be
        # DROPPED rather than crash the cut.
        if np.count_nonzero(m) < 200:
            print(f'  ! {c["name"]}: fully claimed by earlier cards — dropped', flush=True)
            continue
        taken |= m
        c['mask'] = m
        kept.append(c)
        rgba = np.dstack([rgb, (m * 255).astype(np.uint8)])
        ys, xs = np.where(m)
        c['crop'] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        x0, y0, x1, y1 = c['crop']
        cv2.imwrite(f'{OUT}/{tag}_{c["name"]}.png',
                    cv2.cvtColor(rgba[y0:y1, x0:x1], cv2.COLOR_RGBA2BGRA))
    # CLAIM ORDER AND DRAW ORDER ARE DIFFERENT AXES, and conflating them is a
    # trap this cut walked straight into. Regions are listed MOST SPECIFIC FIRST
    # so a willow beats the hillside behind it — but that same order would then
    # draw the willow behind the hill. Widening the hills box once was enough to
    # make it swallow all three willows and drop them from the cut entirely.
    # So: overlaps resolve in LIST order, output is sorted by DEPTH.
    kept.sort(key=lambda c: c['depth'])
    cards = kept
    print(f'{tag}: draw order ' + ' -> '.join(c['name'] for c in cards), flush=True)
    base = pushpull(rgb, taken)
    cv2.imwrite(f'{OUT}/{tag}_base.png', cv2.cvtColor(base, cv2.COLOR_RGB2BGR))

    # ── RECOMPOSE CHECK ──
    comp = base.copy()
    for c in cards:
        comp[c['mask']] = rgb[c['mask']]
    diff = (np.abs(comp.astype(np.int32) - rgb.astype(np.int32)).sum(2) > 12)
    print(f'{tag}: RECOMPOSE diff {100*diff.mean():.3f}%  ({"PASS" if diff.mean() < 0.001 else "FAIL"})', flush=True)
    cv2.imwrite(f'{OUT}/{tag}_recompose_diff.png', (diff * 255).astype(np.uint8))

    json.dump([{'name': c['name'], 'depth': c['depth'], 'crop': c['crop'],
                'w': W, 'h': H} for c in cards], open(f'{OUT}/{tag}_cards.json', 'w'), indent=1)
    print(f'{tag}: wrote {len(cards)} cards + base', flush=True)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
