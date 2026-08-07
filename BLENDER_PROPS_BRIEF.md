# BLENDER BRIEF — Runner décor prop upgrade (for the laptop/Blender session)

**Goal:** raise the *quality* of the Runner (Temple/"Royal Runner") environment
props — trees, bushes, statues, fountains, flowers — to a **premium, paid-app
look** ("$29.99 subscription" bar). **Keep the whimsical princess-fairytale
style and the same silhouettes/kinds** — this is a fidelity/detail upgrade, a
re-skin, **not a redesign**. The cloud session already fixed *placement* (they
sit in composed, symmetric shoulders beside the lanes); what's left is that the
sprites themselves are low-poly. That's the job.

The current atlas is your exact baseline: `assets_whimsy/outprops_current.png`
(raw) and `assets_whimsy/outprops_labeled.png` (numbered contact sheet).

---

## 1. The spec you MUST match (drop-in)

| Property | Value |
|---|---|
| File | one horizontal atlas, transparent PNG |
| Dimensions | **1728 × 240** px |
| Cells | **16 cells, each 108 × 240** (cell N spans x = N·108 … (N+1)·108) |
| Background | fully transparent (alpha) — the engine keys nothing, edges must be clean |
| Anchor | **bottom-aligned**: the prop's base/feet/trunk-bottom sits on the **bottom edge** of its 108×240 cell (props are billboards planted on the ground) |
| Orientation | straight-on **front orthographic** view (no perspective; they're billboards) |
| Content | no text, no watermark, no ground/shadow baked in (engine draws a blob shadow) |

Keep the cell **order and meaning identical** (below) — the stages index into it
by number. If you change what a cell is, you break which prop shows in which room.

### The 16 cells (current → make the premium version of each)
| # | What it is | Upgrade notes |
|---|---|---|
| 0 | round bushy tree (brown trunk) | real bark + layered foliage, soft rim light |
| 1 | tall slim tree (pale) | birch-like trunk texture, airy canopy |
| 2 | white/cream **blossom** tree | cherry-blossom clusters, petals, soft pink-white |
| 3 | green **willow** (hanging strands) | trailing willow fronds, translucent leaves |
| 4 | round green tree | fuller canopy, dappled light |
| 5 | green **rose bush** (pink roses) | real rose blooms + leaves, dense shrub |
| 6 | white **marble fountain** (tiered) | polished marble, real water arc, subtle caustics |
| 7 | white **angel statue** (halo, arms out) | carved marble detail, gold-leaf halo |
| 8 | pink **glow-flower / lamp** | luminous petal, soft emissive bloom |
| 9 | cluster of **golden daisies** | detailed petals/stems, gentle gold |
| 10 | white **swan statue** (gold orb) | marble swan + polished gold sphere |
| 11 | white **swan** (live critter) | feathered swan, clean silhouette |
| 12–15 | small interior props / critters (globe on stand, topiary, bunny) | used indoors — lower priority, but match the set |

### Which rooms use which cells (priority order for you)
`LOOK.props = [nearKindA, nearKindB, critterKind]` per stage:

| Stage | Room | props |
|---|---|---|
| 0 | The Sunlit Library (indoor) | 13, 14, 13 |
| 1 | Rose Garden Waltz | 0, 1, 11 |
| 2 | Blossom Promenade | 2, 2, 11 |
| 3 | The Crystal Ballroom | 4, 6, 5 |
| 4 | Fountain Plaza | 3, 10, 4 |
| 5 | Swan Lake Terrace | 7, 7, 11 |
| 6 | Starlight Conservatory | 8, 8, 11 |
| 7 | Gallery of Dreams | 9, 9, 6 |
| 8 | The Sunset Stage | 6, 5, 4 |

**Highest-impact cells to nail first:** 0,1 (trees — every garden), 5 (rose
bush), 6 (fountain), 7 (angel statue), 11 (swan). Those cover the stages the
client screenshots most.

---

## 2. Engine notes that affect how you author

- **Per-prop colour tint is now added in-engine.** Each placed prop gets a
  subtle warm/cool/fresh RGB multiplier (via a new `aTint` vertex attribute in
  the GL prop shader). So author the textures at a **neutral, mid-key** colour
  and let the engine vary them — don't bake heavy colour variants into the atlas
  or it'll double up. Baked *form/detail* is all yours; *hue variation* is the
  engine's.
- Props render as **billboards** (two crossed quads for a little volume), base
  size ~340×560 world units × per-prop scale. So the **vertical proportions**
  of your art inside the 108×240 cell matter: a tree fills most of the height;
  a bush occupies the lower third. Match the current proportions per cell.
- **Fog** fades props toward the horizon — don't rely on far detail; read the
  silhouette + near detail.
- **Readability rule (binding):** décor must NOT look like an obstacle. Keep
  silhouettes clearly "scenery," distinct from the lane hurdles/gates.

---

## 3. Suggested Blender workflow

1. Model/upgrade each prop (you already have the Rodin/Blender pipeline).
2. **Orthographic front render**, high res (e.g. 432×960 = 4× a cell), on a
   fully transparent film (Filmic/AgX, alpha).
3. Trim to content, **bottom-align** the base, fit into a 108×240 cell
   (LANCZOS downscale — these are painterly now, not nearest).
4. Assemble the 16 cells into the **1728×240** horizontal atlas, same order.
5. Quantize if needed to keep size sane (target the whole atlas well under
   ~300 KB base64 — it embeds into the single-file `index.html`).
6. Save to `assets_whimsy/outprops_new.png` and **show the client a contact
   sheet before embedding** (per the art-direction QA gates).

### Optional: higher-res atlas
If 108×240 is too tight for the detail you want, you can bump the cell size
(e.g. 216×480 → atlas 3456×480) — but then update these references in
`index.html` so the math still lands:
- `outprops:'...'` data-URI in `GLWDATA` (the atlas itself)
- the cell math in `GLWORLD.drawProps`: `u0=p.kind/16, u1=(p.kind+1)/16`
  (stays /16 if you keep 16 cells) and the base `pw=340*ps*s, ph=560*ps*s`
  (aspect must match your new cell aspect 108:240 = 0.45; keep it or adjust pw).
Easiest is to keep **16 cells at the same 0.45 aspect** so nothing in the JS
changes — only the pixels get sharper.

---

## 4. Swap recipe (once the new atlas is ready)

```python
import re, base64
new = base64.b64encode(open('assets_whimsy/outprops_new.png','rb').read()).decode()
s = open('index.html').read()
s = re.sub(r"outprops:'data:image/png;base64,[A-Za-z0-9+/=]+'",
           "outprops:'data:image/png;base64,"+new+"'", s, count=1)
open('index.html','w').write(s)
```

Then Playwright-test a couple of outdoor stages (`?stage=4#dev`) + the library
(`stage 0`), confirm props render + are bottom-anchored + read cleanly, commit
to the dev branch, deploy to gh-pages (see HANDOFF.md deploy recipe).

## 5. QA gates (binding)
- Clean transparent edges (no white/black halo from the key).
- Bottom-anchored (props "plant" on the ground, don't float).
- Reads at small size + through fog; silhouette ≠ obstacle.
- Neutral mid-key colour (engine adds the hue variation).
- No text/watermark/ground/shadow baked in.
- Same 16-cell order/meaning as the baseline.
