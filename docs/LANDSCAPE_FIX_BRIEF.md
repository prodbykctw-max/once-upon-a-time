# LANDSCAPE IS BROKEN — fix brief for the laptop session

**Reported by the client, 2026-07-26, on device (iPhone, iOS Safari, landscape).**
Screenshots are in `docs/landscape/`. Client's words: *"This is how horrible
everything looks sideways."*

Portrait is fine. **Everything below is landscape-only.** Nine issues, ordered by
how bad they look. #1 and #2 are the ones that make it feel broken; the rest are
clipping/overflow.

---

## 1. RPG: a giant flat slab of ground eats ~40% of the screen 🔴 WORST

![ground slab](landscape/06-rpg-ground-slab-blank-platforms.jpg)
![meadow](landscape/07-rpg-meadow-column-seam.jpg)

The floor line sits ~61% down the screen and everything below it is one
featureless tiled slab. The actual playfield is squeezed into a thin strip at the
top, and the beautiful painted backdrop is mostly hidden behind the slab.

**Root cause — it's a fixed *world-space* margin under the floor, and that's the
bug.** In `resize()` (index.html ~line 812):

```js
if(MODE==='side'){
  var BASE=0.78, VIEW_W=520, VIEW_H=320;
  ZOOM=Math.min(BASE, W/VIEW_W*BASE, H/VIEW_H*BASE);
  ZOOM=Math.max(0.5,ZOOM);
}
VW=W/ZOOM; VH=H/ZOOM;
```

On this device:
| | W×H (CSS px) | ZOOM | **VH (world px visible)** |
|---|---|---|---|
| portrait | ~430×932 | 0.645 | **1445** (~45 tiles) |
| landscape | ~932×430 | 0.78 (BASE cap) | **551** (~17 tiles) |

The camera keeps roughly the same *world-space* distance below the floor in both
orientations — about 6–7 tiles. That's **15% of a portrait screen but 39% of a
landscape screen.** Same world margin, wildly different screen fraction.

**Fix direction:** make the floor line land at a consistent *fraction* of the
viewport instead of a fixed world offset — clamp the camera so the ground surface
sits at ~78–82% of viewport height in both orientations. Equivalently, cap the
below-floor margin to a share of `VH` rather than a constant. Don't just crank
`BASE`; that shrinks the hero without fixing the ratio.

> ⚠ Whatever you change, route it through **`setZoom()`** — never assign `ZOOM`
> directly (your own July 25 rule, `BASEZ` + `setZoom()`).

---

## 2. RPG: blank untextured slabs + a tile column running into the sky 🔴

![blank platforms](landscape/06-rpg-ground-slab-blank-platforms.jpg)

- **Blank white/cream rectangles** float in the library scene (top-left, and
  mid-screen right of the candelabra). They're platforms drawing with no usable
  texture — they read as debug boxes, not level geometry.
- **In the meadow shot (#07), a solid column of ground tiles runs floor→sky** at
  roughly 2/3 across, and the painted backdrop visibly **ends with a hard vertical
  seam** at that same x. Backdrop and geometry disagree about where the world ends.

Both probably surface only in landscape because the wider `VW` (1195 world px vs
667 portrait) streams in columns portrait never reveals on screen.

---

## 3. Runner + RPG: iOS Safari chrome steals ~28% of the height

![safari chrome](landscape/08-runner-safari-chrome.jpg)
![squeezed](landscape/09-runner-squeezed.jpg)

In landscape Safari shows the URL bar **and** the bookmarks/tab strip — about 250
of 1179 device px. The game is letterboxed into what's left and the bottom of the
scene is cut. In #08 Jandé is half out of frame behind the chapter card.

`html,body,#gameWrap` already use `100dvh` (line 43/115), so the *canvas* is
sized right — the problem is the **world layout inside** it assumes a taller box.
Worth also confirming `viewport-fit=cover` + `env(safe-area-inset-*)` are honored
in landscape, where the insets are left/right, not just top/bottom.

---

## 4. Game over: the action buttons are below the fold

![run over](landscape/10-runover-buttons-cut.jpg)

RUN OVER shows the score and the leaderboard name/SAVE, but CONTINUE / RESTART /
MAIN MENU are cut off at the bottom edge — the player has to know to scroll.
`#overlay` (line 199) has `overflow-y:auto`, so it *scrolls*, but nothing signals
that. In a short landscape box the primary actions must be reachable without
scrolling: tighten vertical rhythm under `(orientation:landscape)`, or make the
button row a sticky footer inside the overlay.

---

## 5. Registration card is clipped at the top

![register](landscape/02-register-clipped.jpg)

"Enter the Kingdom" is cut off by the top edge — the card is taller than the
landscape viewport and starts above y=0. Same class of fix as #4 (the how-to
screen at line 211 already got `justify-content:flex-start` + `overflow-y:auto` +
top padding; the register card needs the same treatment).

---

## 6. How-to: the PRODBYKCTW footer sits on top of the content

![howto](landscape/03-howto-footer-overlap.jpg)

`.site-footer` is `position:absolute; bottom:12px` (line 351) — in landscape it
lands **on top of** the second control card, and the card list is cut off below.
The Back-button-vs-title fix worked (title is clear now), but the footer needs to
either flow with the scroll content or be hidden under
`(orientation:landscape) and (max-height:560px)`.

---

## 7. Title screen: a vertical seam splits the background

![title](landscape/01-title-seam.jpg)

A hard vertical edge runs top-to-bottom at ~52% — the left half is lighter purple,
the right half nearly black. Reads as two mismatched panels, not one backdrop.
Likely the same backdrop-tiling seam class as #2.

---

## 8. Control cluster is fine — but verify hit targets

![rpg](landscape/04-rpg-library.jpg)

Good news: **the landscape controls all fit on screen** (left/right pads bottom-left,
DASH above ATK/JUMP bottom-right) — that closes the long-standing "verify landscape
controls on device" item. The existing rule at line 282 is doing its job:

```css
@media (orientation:landscape) and (max-height:560px){
  body.mobile .mdiam{--ak:clamp(52px,15vh,72px)}
  body.mobile .dpad{--dk:clamp(40px,11.5vh,56px)}
}
```
Only thing to check: at `15vh` on a 430px-tall landscape viewport the action keys
compute to ~64px, but the d-pad at `11.5vh` ≈ 49px — **under Apple's 56px minimum
touch target.** Consider raising the d-pad floor.

---

## 9. HUD is clean

No overlap between the RESONANCE/LV panel, the crown progress ribbon, and the
sound/pause buttons in landscape. Nothing to do — noting it so it doesn't get
"fixed" by accident.

---

## Suggested order
1. **#1 camera/ground ratio** — single biggest visual win, makes the painted
   backdrops actually visible.
2. **#2 blank platforms + tile column/backdrop seam** — reads as broken geometry.
3. **#4/#5/#6 overlay & footer clipping** — pure CSS under the existing
   `(orientation:landscape)` query.
4. **#7 title seam**, **#8 d-pad target size**.

## Verifying
Portrait must not regress. Repro at ~932×430 CSS px with `body.mobile` active;
`?stage=0` (library) and `?stage=1` (meadow) reproduce #1 and #2 immediately. Note
the known limit: with the preview pane hidden `requestAnimationFrame` throttles —
use the iframe harness from your July 25 note.
