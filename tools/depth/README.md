# Depth-card cutter — flat plate → parallax cards

Cuts a flat painted backdrop into real depth layers, so the multiplane parallax
has actual cards to move instead of one image being warped.

**Method is prodbyKCTW's**, from his "Techniques" doc (section 2), written for
*Will Hill: Player One*. Implemented here as specified rather than improvised.

## Run

```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip3 install git+https://github.com/facebookresearch/segment-anything.git opencv-python-headless
curl -L -o /tmp/sam/sam_vit_b.pth \
  https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth   # 375MB

python3 segment.py ../../web/<plate>.webp <tag>          # ~6 min/plate on CPU
python3 cards.py   ../../web/<plate>.webp <tag> <tag>_regions.json
```

`segment.py` writes masks + the **negative-space** view.
`cards.py` writes the cards, the inpainted base, the **assignment map** and the
**recompose check**.

## The rules that matter (all learned the hard way, most of them his)

- **Two passes, coarse + fine, merged at IoU < 0.75.** Measured here: coarse
  86.1%, fine 96.0%, merged 91.2%.
- **Text/detail is found by lowering the AREA FLOOR and CONFIDENCE, never by
  raising the sampling grid.** His measurement: 28 → 48 moved coverage 85.0 →
  86.0 while the lettering stayed missing.
- **Look at the NEGATIVE space, scored by local contrast.** A proposal sheet only
  shows what was found. On our lake plate this immediately showed the misses were
  boundary pixels plus one genuinely unclaimed thing — the shoreline strip.
- **Group by 70% CONTAINMENT, never centroid.**
- **Scoped colour rule where geometry can't separate.** Box containment cannot
  tell a green willow crown from the blue ridge directly behind it — same screen
  position, both pass, first region wins. The assignment map showed the willows
  swallowing the entire mountain range. `keep: green|blue` fixed it.
- **The sky is subtracted from every card EXCEPT its own.** Not doing this
  emptied the sky card and let the mountains eat the top band — caught by the
  first assignment map.
- **Flood-fill the sky seeded a few px IN**, because plates vignette at the edge.
- **RECOMPOSE CHECK** — base + cards at zero offset must reproduce the original.
  Ours: **0.000%**.
- **LOOK AT THE ASSIGNMENT MAP before wiring anything.** It caught both bugs
  above, in one glance each.
- **`int32` before weighting luminance.** This box is NumPy 2.4, where an int16
  array times a Python int stays int16 and `r*299+g*587+b*114` wraps negative for
  any red above 109.

## Measured cost

Mirror Lake, 8 cards + inpainted base, WebP q82 at game resolution:
**68 KB**. Nine stages ≈ **0.6 MB** against a 5.69 MB game.
