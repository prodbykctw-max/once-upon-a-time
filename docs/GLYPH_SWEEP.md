# STOCK-GLYPH SWEEP — regression, 52 user-visible sites

**Client, 2026-07-26:** *"That little AI arrow on the button pill for proceeding
to the next stage… we were supposed to do a sweep for all of those. There was not
supposed to be any of those buttons anywhere for moving forward."*

He's right, and it's worse than the one arrow.

## This is a REGRESSION, not an un-done task

The sweep **was** completed on 2026-07-21:
- `Replace every system arrow glyph with baked pixel arrows + remove throw`
- `Full de-emoji sweep: 13 baked pixel icons replace every emoji in the UI`
- `HANDOFF ground rule: no stock glyphs/emoji as game UI visuals`

**The baked icon system is no longer in the build** (no `ICO*` map, no `.ic-*`
classes survive), and every UI built *since* — stage select, settings, the
Boutique atlas row, the map legend, the STAGE CLEAR tally, the boss toasts —
reintroduced raw Unicode. **52 user-visible sites.** (Box-drawing inside code
comments is fine and excluded; this list is only what a player actually sees.)

## Why it matters (client's own directive, CLAUDE.md)

> **NO STOCK GLYPHS IN GAME UI** — never use Unicode arrows/symbols/emoji as
> visual elements; the OS renders them as generic system/emoji art, off-theme.
> Anything visual is a MADE asset in the game's style, or plain words.

On iOS several of these (`⏸ ⚙ ⚑ ✦`) render as **Apple system glyphs or emoji** — a
grey iOS pause bar sitting inside a storybook fairytale UI. That is exactly the
"AI button" look he's calling out.

---

## Replacement policy — cheapest correct fix first

1. **Decorative flourish → delete it.** `✦ QUEEN'S REGISTRY ✦` → `QUEEN'S
   REGISTRY`. The two-tier type system already carries the display weight; the
   sparkles add nothing but OS-font noise. **This alone covers ~half the list.**
2. **Label icon → plain words.** `⚙ SETTINGS` → `SETTINGS`. `▶` → nothing
   (`PROCEED TO STAGE II` is already a button; the arrow is redundant).
3. **Data icon → the word.** `♪ 38` → `38 NOTES`; `◆ 12` → `12 GEMS`.
4. **Only where a mark is genuinely load-bearing → draw it.** A pip, a beacon and
   a checkmark are 3–6 lines of canvas/CSS (`arc()`, a rotated square, a
   border-only box). **A shape you draw is a made asset — that satisfies the rule
   without needing a new baked atlas.**

Do **not** re-embed a 13-icon PNG atlas for this. Most sites want words; the rest
want a few primitives.

---

## The sweep (52 sites, grouped)

### A. Pure decoration — delete the glyph, no layout change
| Line | Now | → |
|---|---|---|
| 409 | `✦ QUEEN'S REGISTRY ✦` | `QUEEN'S REGISTRY` |
| 542 | `✦ THE BOUTIQUE ✦` | `THE BOUTIQUE` |
| 548 | `⚑ STAGE SELECT ⚑` | `STAGE SELECT` |
| 554 | `⚙ SETTINGS ⚙` | `SETTINGS` |
| 1458 | `BELT ✦` | `BELT` |
| 3176 | `✦ HE WAITED FOR YOU ✦` | `HE WAITED FOR YOU` |
| 3184 | `✦ +250 ✦` | `+250` |
| 4765, 4773 | `✦ SHE RISES AGAIN ✦` | `SHE RISES AGAIN` |
| 4786 | `STAGE N CLEAR ✦` | `STAGE N CLEAR` |
| 4795 | `✦ <trophy>` | `<trophy>` |
| 4800 | `ALL OBJECTIVES COMPLETE ✦` | `ALL OBJECTIVES COMPLETE` |
| 4832 | `NEW BEST RUN ✦` | `NEW BEST RUN` |
| 4913 | `✦ The Wanderer's Atlas` | `The Wanderer's Atlas` |
| 1609, 1612 | `✦` in map / power-up toasts | delete |

### B. Buttons & controls — glyph → word  ⭐ *includes the one he flagged*
| Line | Now | → |
|---|---|---|
| **4806** | **`PROCEED TO STAGE II ▶`** | **`PROCEED TO STAGE II`** ← the reported one |
| 441 | `⚑ STAGE SELECT` | `STAGE SELECT` |
| 442 | `✦ THE BOUTIQUE` | `THE BOUTIQUE` |
| 464–466 | `✦` / `⚑` / `⚙` on the mode cards | delete |
| 484 | `⏸` pause button | draw two rounded bars, or the word `PAUSE` |
| 533 | `⚙&nbsp;&nbsp;SETTINGS` | `SETTINGS` |
| 534 | `↻&nbsp;&nbsp;RESTART RUN` | `RESTART RUN` |
| 535 | `⌂&nbsp;&nbsp;MAIN MENU` | `MAIN MENU` |
| 431, 438 | `✦` how-to key chips | use the existing made key art |

### C. Tally / HUD / economy — glyph → word
| Line | Now | → |
|---|---|---|
| 4789, 4799, 4845 | `◈ Stage` / `◈ <objective>` | drop `◈` (rows are already a grid) |
| 4790 | `♪ Grace Notes` | `GRACE NOTES` |
| 4793 | `◆ Score` | `SCORE` |
| 4801, 4847 | `♪ BANK n · ◆ n` | `BANK n NOTES · n GEMS` |
| 4839 | `+n ♪ +n ◆` | `+n NOTES · +n GEMS` |
| 4857 | `CONTINUE — n ◆` | `CONTINUE — n GEMS` |
| 4900 | `♪ n GRACE NOTES BANKED · ◆ n` | words |
| 4908, 4917 | `♪ <cost>` buy buttons | `<cost> NOTES` |
| 3285 | `♬ High Note Shield` | `High Note Shield` |
| 3884 | `✦ ×2.5` multiplier | `×2.5` |
| 3887 | `◆ n` gems on canvas | draw the gem, or `n GEMS` |
| 4569 | `▣ HOLDING NOTE` | `HOLDING NOTE` |
| 4929 | `♪` / `✦` in mode stats | words |

### D. Genuinely load-bearing marks — draw them (small)
| Line | Now | → |
|---|---|---|
| 4903, 4912 | `●`/`○` shop + atlas pips | filled vs outlined `arc()`, or CSS boxes |
| 5093 | `✓` on cleared stages | `CLEARED` label, or a drawn tick |
| 3804 | `✦` cache beacon (canvas) | draw a 4-point star — it's a world VFX, wants to be art anyway |
| 2865 | `♪` note glyph (canvas) | `TEX.items` already holds the Grace Note sprite — **use it** |
| 3402 | `♪`/`♫` death-bloom particles | same — use the note sprite |
| 4616 | `■ NOTE` / `● YOU` map legend | draw a small square / dot |

---

## Guard so it doesn't regress a third time

The reason this came back is that nothing *checks* for it. Add a pre-deploy gate
in `tools/deploy.sh` that fails on non-ASCII outside comments and the allowed
accents:

- read `index.html`
- allow the accented letters actually used in words (`é È à ç ü ö ñ`), typographic
  punctuation (`— – ‘ ’ “ ” … ·`), `×`, `°`
- allow `═` and `─` (comment box-drawing only)
- **fail the deploy** on anything else non-ASCII

That turns the directive into something enforced rather than remembered.

**One judgement call to confirm:** `·` (middle dot) is used as a separator in
several strings. It reads as typography rather than an icon, so I left it in the
allow-list — say the word if you want it gone too.

## Scope
`index.html` only. Almost entirely string/label edits plus ~4 small draw
routines — no mechanics change. Verify the how-to, mode select, pause, Boutique,
Stage Select, STAGE CLEAR and RUN OVER screens in **both orientations** after.
