# Client request — proper end-of-stage SCORED TALLY after each RPG boss

**Client, 2026-07-26:** *"I want something like this at the end of each RPG stage
after you defeat a boss. I don't wanna just go onto the next stage — I want an
end-stage summary."*

## The reference

![reference](refs/stage-clear-reference.jpg)

```
                    PROLOGUE 2
                    COMPLETED!

     TIME            02:46/02:30        9680
     ENEMIES               14/14        4300
     DAMAGE                    7        9684

     TOTAL                             13980
```

Classic arcade rank-out. The important structure — this is what makes it feel
like a *reward* rather than a status readout:

1. **Three columns:** `LABEL | achieved/par | POINTS AWARDED`.
2. **Per-metric scoring** — every row pays out its own points.
3. **achieved / par** format so the player instantly sees how they did against a
   target (`02:46/02:30` = ran it in 2:46, par 2:30; `14/14` = every foe cleared).
4. **TOTAL** on its own line after a gap — the sum of the awarded points.
5. Numbers **right-aligned** in fixed columns so they read as a ledger.

---

## What already exists (don't rebuild it)

`showLevelClear()` (index.html ~line 4701) is **already wired and working**:
- fires on boss defeat, sets `GS.ovMode='clear'`, freezes the field
  (`running=false`) so Jandé holds her victory dance behind the overlay;
- reuses `#overlay` / `#ovT` / `#ovM` / `#ovBoard`;
- swaps the primary button to `PROCEED TO STAGE <N> ▶`, hides RESTART;
- handles advance in the `ovMode==='clear'` branch (~line 5017);
- offers the leaderboard name save and banks Grace Notes.

**So the plumbing is done.** This request is a **content + presentation change to
`showLevelClear()`**, not a new screen.

## What's actually missing

Today the board is a **cumulative run status dump** — it shows totals for the
whole run, not what you just did:

```js
bh+='<div class="bd-row"><span>♪ Grace Notes</span><span>'+GS.totalNotes+'</span></div>';  // whole run
bh+='<div class="bd-row"><span>Distance</span><span>'+Math.floor(GS.dist)+'m</span></div>';
bh+='<div class="bd-row"><span>◆ Score</span><span>'+GS.score.toLocaleString()+'</span></div>'; // whole run
```

There is **no per-stage performance, no par comparison, and no per-metric
payout** — which is exactly what the reference is built around.

### Data availability (checked in code)

| Metric | Status |
|---|---|
| **Stage time** | ✅ **free** — `GS.tick` is reset to 0 by `initGS()` (line 849), so stage seconds = `GS.tick/60` |
| **Stage distance** | ✅ free — `GS.dist` also resets per stage (line 853) |
| **Foes defeated this stage** | ❌ **must add** — no kill counter exists |
| **Foes spawned this stage** | ❌ **must add** — needed for the `14/14` denominator |
| **Damage taken this stage** | ❌ **must add** — `GS.hits` exists but isn't a per-stage damage tally |
| **Grace Notes this stage** | ⚠️ `GS.totalNotes` is **cumulative** — needs a per-stage delta |
| **Par time per stage** | ❌ **must add** — a `STAGE_PAR[9]` table |

### Suggested additions
- `GS.kills` — increment in `killFoe`.
- `GS.foesTotal` — increment wherever `genAhead` pushes a foe.
- `GS.dmgTaken` — increment where the player loses a mask/heart.
- `GS.notes0` — snapshot `GS.totalNotes` at `initGS` so stage notes = delta.
- `STAGE_PAR = [...]` — 9 par times. Tune from real playthroughs; `stageEnd=330`
  columns is the natural basis.

All five reset naturally in `initGS()` alongside the existing counters.

---

## Suggested layout (in the game's own voice)

⚠️ **Two binding project rules apply here:**

1. **Music-themed vocabulary is binding** (CLAUDE.md) — so don't ship the literal
   words "ENEMIES/DAMAGE". Use the game's language.
2. **NO STOCK GLYPHS IN GAME UI** (client directive) — and note the *current*
   `showLevelClear` already violates this: it uses `✦ ◈ ♪ ◆ ▶` as visual
   elements. Since this screen is being redesigned anyway, that's a free chance
   to retire them for made assets or plain words.

```
              STAGE I CLEAR
        THE INK WARDEN — SILENCED

  TIME              02:46 / 02:30      9,680
  GRACE NOTES              38 / 44     4,300
  FOES SILENCED            14 / 14     2,800
  UNTOUCHED                      7     9,684
  RESONANCE                    LV 9    1,200

  TOTAL                              27,664
```

- Keep the boss's name in the subtitle — it's the trophy line, and `BOSS_NAME[ai]`
  is already in scope.
- Keep the existing trophies / objectives-multiplier blocks **below** the tally,
  and the `PROCEED TO STAGE <N>` button. Those work; don't disturb them.
- Award points per row, then **`TOTAL` = the sum**, and add that to `GS.score`.
- **Count the total up** rather than printing it — a short roll-up animation is
  most of what makes an arcade tally feel good. Respect
  `SET.reduceMotion` (already in settings) by printing instantly when it's on.

### Layout note
Use a real 3-column grid with `font-variant-numeric: tabular-nums` and
right-aligned numerics so the columns line up. The existing `.bd-row` is a
2-column flex (`<span>` / `<span>`) — it will need a third cell.

---

## Scope
- **Files:** `index.html` only — `showLevelClear()`, `initGS()`, `killFoe`,
  the foe-spawn site in `genAhead`, the player-damage site, plus `.bd-row` CSS.
- **Do not** touch the Royal Runner. This is **RPG-only** — the runner is an
  endless run and has no stage-boss clear.
- Verify in **portrait and landscape** (landscape overlays are already clipping —
  see `docs/LANDSCAPE_FIX_BRIEF.md` #4/#5; this new content is taller, so it
  needs the same short-viewport treatment: the TOTAL and PROCEED button must be
  reachable without scrolling).
