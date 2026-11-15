# GLIDE TRANSITIONS — "nothing just appears" — ✅ SHIPPED (branch `feat/glide-transitions`)

Three rules, applied to every menu and card that opens something:

1. **Card → page.** The card or button that was tapped grows into the page it opens.
2. **Back goes back.** Going back shrinks the page into the card it came from.
3. **Menus start at their button.** A menu, overlay or panel opened by a button grows out
   of that button (transform-origin at the button, scale + opacity) and closes back into it.

**Motion only.** No layout, colour, copy, art or size changed. The end state of every
screen is identical to before; only the in-between frames are new. Measured: the end-state
screenshots of every screen below match the base build pixel for pixel (0 differing pixels
above a 12/255 threshold; the in-game frames differ only by gameplay noise).

## What moves

| Opens / closes | From / back into | How |
|---|---|---|
| Pause menu (`#pauseMenu`) — button, `P` or `Esc` | `#btnPause` | `glideIn` / `glideOut` in `syncPauseMenu` |
| Settings (`#settingsScr`) | `#msSettings` (mode select), `#pmSettings` (pause menu) | `glideOpenScr` / `glideCloseScr` |
| The Boutique (`#shopScr`) | `#htShop` (how-to page), `#msShop` | same |
| Stage Select (`#stageSelScr`) | `#htStage`, `#msStageSel` | same |
| How-to page (`#howToScreen .ht-wrap`) | the tapped mode card (`#msSide` / `#msTemple`), or the tapped Stage Select button | `glideNav` (View Transitions API) |
| Back from the how-to page (`#htBack`) | the mode card for the current `MODE` | `glideNav(..., back=true)` |
| Login card (`#loginScreen .lb`) | `#tPress` (BEGIN) | `glideNav` |

Not animated, on purpose: the in-game map (`btnMap` toggles a canvas-drawn map, not a DOM
menu), the level card, the game-over overlay (opens on its own, no button), and the
`startGame` hand-off from the how-to page into play.

## How it is built (all in `index.html`, right after `show()`)

* `glideOff()` — true under `body.rm` (the reduce-motion setting + OS preference, kept by
  `applyMotionClass`) or `prefers-reduced-motion`. **Nothing plays then; the change is instant.**
* Menus: `glideIn` / `glideOut` run `el.animate` on the menu box from the button's centre:
  `scale(.55)` + opacity 0 to identity, 240 ms out / 190 ms back, easings
  `cubic-bezier(.2,.8,.2,1)` / `cubic-bezier(.4,0,.2,1)`. The scrim fades alongside.
* A just-closed menu is kept painted by a `.closing` class (`display:flex; pointer-events:none`)
  until its shrink finishes. **The game state (`GS.paused`, `.on`) has already changed by then**;
  nothing waits on the animation. Re-opening, a second `Esc`, or `pmMenu` calls `glideKill`
  first, so no half-open state can survive.
* The modal boxes' older `jellyIn` pop-in is switched off for them (`.sh-box[data-gl]`),
  otherwise it would replay on top of the grow.
* Cards: `glideNav` names the tapped element `glide-card` in the old state and the destination
  container `glide-card` in the new state inside `document.startViewTransition`, then clears the
  names on `finished`. 320 ms; `:root.glide-back` swaps in the back easing. A running transition
  is skipped first, so rapid taps cannot stack. Without `startViewTransition` the swap is instant.
* `body.glide-nav` suppresses `jellyIn` on the elements being morphed for the duration only.

## Rules for adding another

Any new button-opened menu: use `glideOpenScr`/`glideCloseScr` (modal screens) or
`glideIn`/`glideOut` (anything else), and never gate game state on the animation. Any new
card that opens a detail page: `glideNav`. Never animate under `body.rm`.

## Verified (Playwright / headless Chromium 1243, 1000x640)

Mid-transition frames (animations frozen at 40%) and end states are in
`/home/claude/audit/glide/jande/` (`new/` and `base/`; `reduce/` is the same run with
`reducedMotion: 'reduce'`, where no animation is created at all). Also checked: rapid
`Esc` x3 + 1 settles with `GS.paused` correct and the menu fully hidden; no
`startViewTransition` still navigates; `node --check` on every inline script; glyph gate clean.
