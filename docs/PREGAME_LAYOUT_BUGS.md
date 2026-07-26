# Pre-game screens: content top-pinned, oversized in landscape, and UNREACHABLE

**Client, 2026-07-26 (on device, live build):** *"Main screen too high / centered.
Maybe an issue across the game? Horizontal view of main menu too tight."* and
*"No scroll on horizontal on web on mobile."*

Three separate causes. **#3 is a blocker — you cannot start the game in landscape.**

---

## 1. 🔴 Content is pinned to the TOP — regression from the footer fix

`.screen` is correct: `display:flex; flex-direction:column; justify-content:center`.

But the footer fix (`24049d4`) changed `.site-footer` to:

```css
.site-footer{position:static; margin-top:auto; flex:0 0 auto; …}   /* line 413 */
```

**In flexbox, an `auto` margin absorbs *all* free space before `justify-content`
gets to distribute any.** So `margin-top:auto` on the last child pushes the footer
to the bottom **and cancels the centering for everything above it** — the content
collapses to the top and the rest of the screen is dead space. That's exactly what
the client is seeing on the title and register screens.

The footer fix itself was right (it solved the overlap); this is its side effect.

**Fix:** don't use `margin-top:auto` to position the footer. Either
- keep `justify-content:center` and give the screen a bottom padding equal to the
  footer height, letting the footer sit in normal flow; or
- wrap the centred content in its own `flex:1; display:flex; justify-content:center`
  container so the footer is a sibling that doesn't eat the free space.

---

## 2. 🔴 Landscape: the wordmark is sized off WIDTH on a height-constrained screen

```css
.tw-j{font-size:clamp(60px,16vw,140px)}     /* line 63 */
```

| | viewport | 16vw | clamped | **% of viewport HEIGHT** |
|---|---|---|---|---|
| portrait | 430×932 | 69px | 69px | **7.4%** |
| landscape | 932×430 | 149px | 140px | **32.6%** |

The wordmark alone eats **a third of the landscape screen**, which is why the menu
reads "too tight" and BEGIN falls off the bottom.

**This is the same mistake as the runner hazards** (`obW` off `W` while the hero was
off `H`) — a size pinned to the wrong axis. Cap it against height too:

```css
font-size:clamp(46px, min(16vw, 20vh), 140px);
```

Worth grepping the pre-game CSS for other bare `vw` sizes; the same trap will be in
`.tw-line`, `.ms-h`, and the tagline.

---

## 3. 🔴🔴 BLOCKER — overflow is hidden and these screens cannot scroll

```css
html,body{ … overflow:hidden … }            /* line 48 */
.screen{position:absolute; inset:0; …}      /* line 49 — no overflow-y */
```

| screen | scrollable? |
|---|---|
| `#howToScreen` | ✅ `overflow-y:auto` |
| `#overlay` | ✅ `overflow-y:auto` |
| **`#titleScreen`** | ❌ **none** |
| **`#loginScreen`** | ❌ **none** |
| **`#modeScreen`** | ❌ **none** |

So when #1 and #2 push content past the bottom in landscape, **there is no way to
reach it.** The BEGIN button, the ENTER THE KINGDOM button and the mode cards are
simply unreachable — the game cannot be started in landscape on a phone.

The how-to screen and the results overlay were given `overflow-y:auto` during
earlier clipping fixes; **these three never were.**

**Fix:** add the same treatment to `.screen` (or specifically title/login/mode):
`overflow-y:auto; -webkit-overflow-scrolling:touch;` plus a safe-area bottom pad.
Fixing #1 and #2 will hide the symptom, but this should be fixed anyway as the
safety net — any future content growth re-creates an unreachable button.

---

## Verify
Portrait **and** landscape at ~932×430, on the live build:
title → BEGIN reachable · register → ENTER THE KINGDOM reachable · mode select →
both cards reachable · content vertically centred, not hugging the top.

---

## 4. Leaderboard on the STAGE CLEAR screen — NOT collapsed on purpose

Client asked whether the leaderboard collapses deliberately in landscape at the
end of a stage. **It does not.** Checked the CSS: there is **no
`@media (orientation:landscape)` rule anywhere that hides, collapses or shrinks**
`#ovName`, `#ovNameInput`, `#ovNameOk` or `#ovBoard`. The name row is styled once
(`#ovName{margin:4px auto 8px}`, line 426) with no orientation variant.

So whatever the client is seeing is the **overlay clipping bug** (`DO_NOW` item 4 /
`LANDSCAPE_FIX_BRIEF` #4), not intentional design. `#overlay` does have
`overflow-y:auto`, so the content is reachable by scrolling — but on a short
landscape viewport the tally is now taller than the box, so rows below the fold
(objectives, and depending on height the leaderboard row) look "collapsed" when
they are really just cut off with no visual affordance that there's more.

**Fix is the same as item 4:** on short viewports keep the TOTAL row and the
primary button reachable without scrolling — sticky action row inside `#overlay`,
or tighter vertical rhythm under the landscape query. A scroll shadow / fade at
the cut line would also stop it reading as "collapsed".
