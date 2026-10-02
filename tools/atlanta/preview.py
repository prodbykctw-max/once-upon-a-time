#!/usr/bin/env python3
"""Top-down plan of an extracted location — a look at the real geometry
before any of it reaches Blender.

    python3 tools/atlanta/preview.py                 # every world/*.json, as a sheet
    python3 tools/atlanta/preview.py mbs             # one location

Writes tools/atlanta/preview/<key>.png (and _sheet.png for the set).

This exists because `world.json` is 75 KB of numbers and the only honest way to
know the extract is right is to look at it. Surveyed and ESTIMATED building
heights are drawn in different colours, so the amount of guessing in a location
is visible at a glance rather than buried in a log line.
"""
import json, os, sys, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = os.path.join(HERE, 'world')
OUT = os.path.join(HERE, 'preview')
os.makedirs(OUT, exist_ok=True)

PX = 900                      # render size in pixels
BG = (18, 18, 22)
C_SURV = (176, 172, 166)      # BGR — surveyed height
C_EST = (70, 120, 210)        # orange-ish: height was guessed
C_PARK = (70, 110, 55)
C_WATER = (150, 95, 40)
C_FOOT = (95, 95, 110)
C_ROAD = (120, 120, 128)
FOOT_KINDS = {'footway', 'path', 'steps', 'cycleway', 'pedestrian'}
CLASS_W = {'motorway': 14, 'trunk': 12, 'primary': 11, 'secondary': 10, 'tertiary': 9,
           'residential': 7.5, 'unclassified': 7, 'service': 4.5, 'living_street': 6,
           'pedestrian': 5, 'footway': 2, 'path': 1.8, 'cycleway': 2.5, 'steps': 1.6,
           'track': 3}


def render(w):
    R = float(w['location']['radius_m'])
    scale = (PX / 2.0) / (R * 1.08)          # metres -> px, small margin
    img = np.full((PX, PX, 3), BG, np.uint8)

    def to_px(p):
        # +y is north, and screen y grows downward — flip it, or the city is
        # mirrored and nobody notices until it is baked.
        return (int(PX / 2 + p[0] * scale), int(PX / 2 - p[1] * scale))

    # radius ring
    cv2.circle(img, (PX // 2, PX // 2), int(R * scale), (44, 44, 52), 1, cv2.LINE_AA)

    for a in w.get('areas', []):
        pts = np.array([to_px(p) for p in a['pts']], np.int32)
        cv2.fillPoly(img, [pts], C_WATER if a['kind'] == 'water' else C_PARK, cv2.LINE_AA)

    for rd in w['roads']:
        kind = rd['kind']
        lanes = rd.get('lanes')
        wid = (lanes * 3.3) if lanes else CLASS_W.get(kind, 6)
        th = max(1, int(wid * scale))
        pts = np.array([to_px(p) for p in rd['pts']], np.int32)
        cv2.polylines(img, [pts], False, C_FOOT if kind in FOOT_KINDS else C_ROAD,
                      th, cv2.LINE_AA)

    n_surv = n_est = 0
    for b in w['buildings']:
        pts = np.array([to_px(p) for p in b['pts']], np.int32)
        if len(pts) < 3:
            continue
        surveyed = b.get('h') is not None
        n_surv += surveyed
        n_est += (not surveyed)
        cv2.fillPoly(img, [pts], C_SURV if surveyed else C_EST, cv2.LINE_AA)
        cv2.polylines(img, [pts], True, (28, 28, 34), 1, cv2.LINE_AA)

    cv2.drawMarker(img, (PX // 2, PX // 2), (90, 220, 255), cv2.MARKER_CROSS, 18, 2)
    return img, n_surv, n_est


def label(img, w, n_surv, n_est):
    L = w['location']
    bar = np.full((78, img.shape[1], 3), (12, 12, 15), np.uint8)
    cv2.putText(bar, L['label'], (14, 28), cv2.FONT_HERSHEY_DUPLEX, 0.72,
                (240, 240, 245), 1, cv2.LINE_AA)
    km = sum(sum(math.dist(r['pts'][i], r['pts'][i - 1]) for i in range(1, len(r['pts'])))
             for r in w['roads']) / 1000.0
    cv2.putText(bar, '%s  ·  %.0f m radius  ·  %d buildings  ·  %.1f km of ways'
                % (L['osm'], L['radius_m'], len(w['buildings']), km),
                (14, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (155, 155, 165), 1, cv2.LINE_AA)
    cv2.putText(bar, '%d surveyed height' % n_surv, (14, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, C_SURV, 1, cv2.LINE_AA)
    cv2.putText(bar, '%d ESTIMATED' % n_est, (170, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, C_EST, 1, cv2.LINE_AA)
    return np.vstack([bar, img])


def main():
    keys = sys.argv[1:] or sorted(
        f[:-5] for f in os.listdir(WORLD) if f.endswith('.json') and not f.startswith('__'))
    tiles = []
    for k in keys:
        p = os.path.join(WORLD, '%s.json' % k)
        if not os.path.exists(p):
            print('  no world/%s.json — run build_world.mjs %s' % (k, k)); continue
        w = json.load(open(p, encoding='utf-8'))
        img, ns, ne = render(w)
        tile = label(img, w, ns, ne)
        cv2.imwrite(os.path.join(OUT, '%s.png' % k), tile)
        print('  %-10s %d buildings (%d estimated), %d ways -> preview/%s.png'
              % (k, len(w['buildings']), ne, len(w['roads']), k))
        tiles.append(cv2.resize(tile, (tile.shape[1] // 2, tile.shape[0] // 2)))
    if len(tiles) > 1:
        cols = 2
        rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles) - len(tiles) % cols, cols)]
        if len(tiles) % cols:
            last = tiles[-1]
            pad = np.full((last.shape[0], last.shape[1] * (cols - 1), 3), BG, np.uint8)
            rows.append(np.hstack([last, pad]))
        sheet = np.vstack(rows)
        cv2.imwrite(os.path.join(OUT, '_sheet.png'), sheet)
        print('  sheet -> preview/_sheet.png  %dx%d' % (sheet.shape[1], sheet.shape[0]))


if __name__ == '__main__':
    main()
