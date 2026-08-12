#!/usr/bin/env python3
"""Measure an animation sheet BEFORE changing how it plays.

Answers the three questions that decide the fix, none of which can be judged by
watching it:
  1. How many CYCLES does the sheet hold? (a single out-and-back has its furthest
     frame mid-sequence and its smallest step on the wrap)
  2. What is the real cadence, in breaths/strides per minute?
  3. How far does the head line travel, as a share of her height? — the "hunch"

getbbox() will betray you: it counts any non-zero alpha, and background removal
leaves near-transparent rows below the feet. Threshold at ~40.
int32 before weighting luminance — NumPy 2 keeps int16 and wraps negative.
"""
import sys, numpy as np, cv2

def measure(path, cw, n, ch=154, ticks_per_frame=None, th=40):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    fr = [im[0:ch, i*cw:(i+1)*cw] for i in range(n)]
    g  = [cv2.cvtColor(f[..., :3], cv2.COLOR_BGR2GRAY).astype(np.int32) for f in fr]
    m  = [(f[..., 3] > th) for f in fr]
    D  = np.array([[np.abs(g[i]-g[j])[m[i]|m[j]].mean() for j in range(n)] for i in range(n)])
    far, wrap = int(np.argmax(D[0])), D[n-1, 0]
    step = float(np.mean([D[i, (i+1) % n] for i in range(n)]))
    tops = np.array([np.where(f[..., 3] > th)[0].min() for f in fr], dtype=np.int32)
    bots = np.array([np.where(f[..., 3] > th)[0].max() for f in fr], dtype=np.int32)
    print(f'{path}')
    print(f'  cycles      : furthest-from-f0 = f{far} ({"mid-sequence" if 0 < far < n-1 else "AT AN END"}), '
          f'wrap step {wrap:.1f} vs mean {step:.1f}  -> '
          f'{"ONE cycle" if 0 < far < n-1 and wrap < step else "MAY HOLD SEVERAL — do not sample evenly"}')
    print(f'  head line   : {list(map(int, tops))}  travel {tops.max()-tops.min()}px = '
          f'{100*(tops.max()-tops.min())/ch:.1f}% of height   (quiet breathing is 1-2%)')
    print(f'  feet        : {list(map(int, bots))}  -> '
          f'{"PLANTED (dip is a compression; do NOT offset y, it breaks ground contact)" if bots.max()-bots.min() <= 2 else "MOVING"}')
    if ticks_per_frame:
        t = n * ticks_per_frame
        print(f'  cadence     : {n} frames x {ticks_per_frame} ticks = {t} ticks = {t/60:.2f}s = '
              f'{60/(t/60):.0f} per minute   (human at rest: 12-16)')

if __name__ == '__main__':
    measure('web/865c17b4dacb.png', 89, 6, ticks_per_frame=9)   # idle, as it shipped
