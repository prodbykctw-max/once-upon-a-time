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

## Run order

```bash
python3 segment.py ../../web/<plate>.webp <tag> [dense]     # ~8-12 min/plate
python3 cards.py   ../../web/<plate>.webp <tag> regions/<tag>.json
python3 pack.py    <tag> <stage-index> [--write]            # full-frame WebP -> web/
python3 swap.py    [--write]                                # rewrite CARD_DATA, prune orphans
```

Region specs and the rules for writing one: `regions/README.md`.

## The rules that matter (all learned the hard way, most of them his)

- **Three passes now — coarse, MEDIUM, fine — cascaded and merged at IoU < 0.75.**
  Client, 2026-08-13: *"let's do the coarse medium fine recut."* The middle tier
  is the one that matters for depth cards, because coarse returns whole masses,
  fine returns fragments, and a usable card is neither — it is an OBJECT.
  Measured on the meadow plate: **coarse alone 55.7%, medium 85.9%.** Coarse
  cannot resolve gradual rolling hills at all; nothing in the two-tier setup
  could, and it showed in the cut.
  Each tier is compared against everything KEPT SO FAR, not against coarse alone
  — with two tiers that distinction did not exist.
- **CLAIM ORDER AND DRAW ORDER ARE DIFFERENT AXES.** Regions are listed most
  specific first and overlaps resolve in that order; cards are emitted sorted by
  depth. Conflating them meant one widened box swallowed all three lake willows
  and dropped them from the cut. In practice this means **list the NEAR planes
  early**, so a tall object that crosses a band boundary — an edge conifer, a
  willow — is claimed whole by the plane it stands on instead of being torn in
  half between two depths.
- **The number of usable planes is set by the PAINTING, not by how finely you
  cut.** The meadow wanted six and supports five: a box tall enough to claim the
  conifers whole is also tall enough to claim the mid hills, so the mid band
  merges into the near one. Forcing an extra plane is what makes a cut read
  wrong. Same lesson as the library staying flat.
- **`reject: green` where `keep` cannot help.** The Rose Waltz colonnade cannot
  be selected BY a colour — its arches are marble and its garlands are pink and
  green — but the hedge behind it can be excluded by one.
- (superseded) *Two passes, coarse + fine, merged at IoU < 0.75.* Measured then:
  coarse 86.1%, fine 96.0%, merged 91.2%.
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
- **...and the map itself has to be honest.** It used to stamp each region's raw
  mask in turn. Region masks OVERLAP by design — that is what the exclusivity
  pass downstream is for — so it showed whichever region came LAST rather than
  the one that wins the pixel. It read "the hills own all three willows" while
  the cut was in fact giving the willows their own cards correctly. It now paints
  from the first-claim-wins array. A diagnostic that lies is worse than none.
- **pack.py measures each card's PIVOT** (the bottom of its own content) and the
  game reads it. Cards are full-frame, so without it the wind shear pivots on the
  bottom of the PLATE and a tree sways at its own trunk.
- **`int32` before weighting luminance.** This box is NumPy 2.4, where an int16
  array times a Python int stays int16 and `r*299+g*587+b*114` wraps negative for
  any red above 109.

## Measured cost

Mirror Lake, 8 cards + inpainted base, WebP q82 at game resolution:
**68 KB**. Nine stages ≈ **0.6 MB** against a 5.69 MB game.
