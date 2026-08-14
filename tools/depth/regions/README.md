# Region specs — one per plate

`cards.py` takes one of these and turns SAM masks into depth cards. The boxes are
fractions of the plate, read off a labelled grid (`grid.py`), not estimated.

## THE RULE THAT CHANGED IN THE RE-CUT

**Group by GROUND PLANE, not by object.** A thing and the ground it stands on go
on the same card unless it is genuinely nearer than that ground.

This is what the first cut got wrong, and it is most of what the client meant by
*"some of the cut outs and movements and layering doesn't make sense."* Two
examples from the shipped cut, both visible in the game:

- **The Petal Mile** had `canopy` at depth 0.68 and `trunks` at 0.58 — the
  blossom moved FASTER than the trees holding it up, so a canopy slid off its own
  trunks.
- **First Light Meadow** had `foretrees` on their own card at 0.80 while the hill
  they stand on was `hills` at 0.42. Separation is clamped at ±80px, so on a long
  level a tree drifts most of a hundred pixels off its own hillside.

Neither is a cutting error — both cuts were clean. They are *layering* errors,
and no amount of re-segmenting fixes them. Hence the rule.

The corollary: a card should be a **plane of the scene**, complete — the hill and
everything standing on it — which is exactly what a cel on a multiplane rig is.
Cards get MORE internally complete, not more finely divided.

## The other rules (unchanged, from the Techniques doc)

- Boxes are `[x0,y0,x1,y1]` as fractions. Grouping is by **70% containment**.
- `keep: green|blue` where box containment cannot separate two things at the same
  screen position (a green crown against the blue ridge behind it).
- `maxArea` (fraction of the box) stops a region swallowing a whole band.
- `isSky` seeds the card with the flood fill and exempts it from the sky
  subtraction every other card gets.
- `holes:false` for anything spanning the frame — `fill_holes` is bounded, but a
  full-width band has no business being hole-filled at all.
- Order matters: earlier regions claim pixels first. Put the FAR ones first.

## Wind

`wind:1` is set in `CARD_DATA`, not here, but the cut has to make it possible:
**a card carrying wind must contain only plant life.** The Rose Waltz colonnade
is the case to remember — its rose garlands hang on marble arches, so the
garlands cannot be lifted onto a wind card without either swaying the marble or
sliding the roses off the stone. They stay on the colonnade card, unmoving. The
greenery that does sway is the hedge and treeline behind it.
