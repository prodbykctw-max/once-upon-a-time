# GAME I OVERHAUL: BASILICA Production Bible 2.5 + Narrative Bible v2

> **STATUS: PREVIEW, not public.** Built 2026-11-01 on branch
> `claude/overhaul-bible-2.5` (base: the dev branch at `b221ca6`). It publishes to
> **`/overhaul/`** beside the public game via `tools/build_overhaul.py`. The public
> Jandé game at the site root is untouched.
>
> Sources (Frédéric De Jesus, Oct 30 2026):
> - *ONCE UPON A TIME: Master Production Bible 2.5 - Developer Handoff* (Drive `14FPi-XgPa0NScqYOyqUvb7slCuCU6Mwd`)
> - *ONCE UPON A TIME: Narrative Bible - Master Script v2* (Drive `1WYiYxieznOfqZqWHHGRbQb5D_HcrA5J8`)
>
> In his cover email he asked to talk the doc through before changes were made. The
> client chose to build it on Nov 1. That is why it ships as a preview only.

Scope picked by the client for this pass:
1. Rename & recast
2. Story cuts + VS cards
3. Free Bookmarks
4. Controls + Guard

Everything else in the bible is listed below as **NOT BUILT**.

---

## Architecture (read before touching it)

- **Chapters vs worlds.** `CH[]` holds the 11 chapters. `GS.ch` is the chapter. **`GS.ai` is still the
  painted WORLD** (0–8), so every art/backdrop table keeps working unchanged.
  `initGS(n)` takes a **chapter** and sets `GS.ai = CH[n].env`. Bosses use `CH[n].art` as their atlas row.
- **Story sequencer.** `storyRun(steps, done, opt)` drives the body-level `#story` overlay. Step types:
  - `['P'|'S'|'O'|'B'|'F', line]`: dialogue, waits for a tap.
  - `{act}`: a stage direction that changes the world.
  - `{bg, ms}`: a full-screen card drawn on `#stPage`.
  - `{wait}` / `{beat}`: a timed pause.

  - `{bg, ms, xf}`: `xf` is the crossfade length in frames. The outgoing frame is snapshotted and dissolved.

  Timed beats count down on the **story clock** inside `stFrame` (`ST.waitMs`, and `t` for every card is
  `ST.bgT` in 60ths of a second, scaled by real frame time). They never use `setTimeout`, and they never
  count raw rAF calls, which would double every animation on a 120 Hz phone.
- **Cinematic layer (11-02).** Everything the player sees during a cut is drawn by one block in front of
  the sequencer:
  - `panelBG(key, o)` draws a painted panel with a slow push and pan toward a focal point (`fx/fy` in image
    space), motes and a vignette. On a tall screen the 16:9 plate becomes a cinema band over a blurred copy of
    itself, so the subject is never cropped away.
  - The **cast** (`castKey`, `castSet`, `castDraw`) puts large portraits behind the dialogue box: Princess on
    the left and S/O/B/F on the right. The speaker is lit and lifted, the listener dims, and each line gets a
    small hop. The expression comes from the line itself (`exprP` / `exprS`). Princess wears the storybook
    gown (`pb_*`) until the `transform` act clears `PRO.pre`, then the adventurer (`pr_*`).
  - The cards are `coverCard`, the six `PRO_PANELS`, `flipCard`, `makePageBG`, `XFORM_BG`, `vsCard`,
    `revealCard`, the `p_merge` panel in `SCRIPT[10].final`, `herCard` and `ENCORE_BG`.
    A card that shows full-screen people sets `.noCast`, and `revealCard` sets `.noCastR`.
  - The in-world Storykeeper is the painted cutout (`drawSKWorld`). He stands front-facing, and on
    `skGesture` he becomes the pointing pose aimed forward. `drawSK` (code-drawn) is only the fallback.
  - Art lives in `ART_SRC`, 37 files in `web/`. The images were generated in Figma, in the style of Frédéric's
    reference board, and cut out with rembg (`isnet-anime`). Busts are baked once with a faded bottom edge
    (`castImg`).

  `GS.cut = true` pauses `update()` while the world keeps drawing. `storyEnd()` clears held keys and touches,
  so nothing leaks into play. Every cut has SKIP, and Escape also skips. `{act}` steps listed in
  `V2ACT_SKIPSAFE` still run on skip, so a skip never leaves the world half-told.
- **Script.** `SCRIPT[ch]` is the Narrative Bible v2 transcribed verbatim, with keys
  `intro / reveal / boss / defeat / trans`. Chapter XI also has `t1 / t2 / final`.
  `PROLOGUE_TALK`, `TRANSFORM_TALK` and `ENCORE_TALK` hold the bookends.
  **Do not paraphrase lines.** Narrative §8A lists cut lines that must not come back.
- **Flow per chapter (Narrative §9):**
  1. Level card, then control.
  2. Intro cut once she passes column 10. Storykeeper stands in the world.
  3. First-ever foe reveal: the reveal foe is force-spawned at column ~49.
  4. Bookmarks at 34% and 68% of the chapter.
  5. Gate, then bookmark, then boss cut, then VS card, then the fight.
  6. Defeat cut with the boss held on its first defeat frame, then the collapse.
  7. CHAPTER COMPLETE tally (CONTINUE STORY / REPLAY CHAPTER).
  8. Transition cut, then the next chapter.
- **Boss deaths outside the melee block** (Soundwave, Full Voice) are caught by a second check right after
  `v2Tick`. Without it the defeat flow never started for a non-melee kill.
- **Persistence** lives in `localStorage['ouat2']`: `learned`, `revealed`, `clears`, `save {ch,x}`, `reg`, `done`.
  It is separate from the `jande_*` keys on purpose. Every Pages project on this account shares one origin.

## Chapter → world → boss map

| # | Chapter | World (`env`) | Boss | Atlas row | Reveal foe |
|---|---|---|---|---|---|
| I | Once Upon a Page | 0 Library | The Warden | Ink Warden | Instigator |
| II | First Light Meadow | 1 Meadow | The Doubt | **stand-in:** Blossom Revenant, cool tint | Suspicion |
| III | The Petal Mile | 2 Petal Mile | The Sentinel | Thistle Ogre | Impulse |
| IV | Rose Waltz | 3 Rose Waltz | The Thorn Queen | Thorn Queen | Grudge |
| V | Afterglow | 5 Wishing Glade (dusk) | The Spark | Blossom Revenant | none |
| VI | Halfway Ever After | 6 Golden Hour | The In-Between | Toadstool Warlock | Spiral |
| VII | Open Doors | 8 Palace lights (night) | The Grey Area | **stand-in:** Toadstool Warlock, greyscale | Receipt |
| VIII | Mirror Lake | 4 Mirror Lake | The Wraith | Lake Wraith | none |
| IX | The High Ground | 7 Sky Gardens | The Sovereign | Scarecrow King | none |
| X | Into the Storm | 7 Sky Gardens + storm overlay | The Tempest | Storm Titan | none |
| XI | Her | 0 Library + violet vignette | Princess | hero sprites, desaturated | none |

The Groom Who Lied is **retired**: not referenced by any chapter, and the art is kept in the atlas.

Foes keep their movement code and are renamed only:

| Old foe | New name |
|---|---|
| goblin | Instigator |
| raven | Suspicion |
| sprite | Impulse |
| Bramble Knight | Grudge |
| Wisp Swarm | Spiral |
| Rose Wraith | Receipt |

## Abilities (Bible §6) and controls (§10)

| Verb | Learned | Keys | Touch | Pad |
|---|---|---|---|---|
| Mic Check | I | Z / J / X | MIC | X / Y |
| Soundwave | I | tap C (or K) | tap VOICE | B |
| Guard + Perfect Note | II | hold C | hold VOICE | hold B |
| Bass Drop | III | in air: Down + Z | in air: swipe down | stick down + X |
| Second Wind | IV | hold Q | hold SECOND WIND (appears when hurt and Resonance ≥ 20) | LT |
| Full Voice | VI | E (costs 90) | FULL VOICE (appears at ≥ 90) | RT |
| Jump | — | Space / Up / W | JUMP, or swipe up anywhere | A |
| Dash (kept; not in bible) | — | Shift | double-tap a direction | bumpers |

Ability behaviour:
- **Perfect Note:** a hit landing in the first 10 ticks of Guard is negated. It gives +15 Resonance and
  staggers the attacker: foes freeze for 70 ticks, and bosses are knocked into WAIT and opened (Sentinel).
- **Guard strain:** Guard costs nothing (§6), but three ordinary blocks in quick succession break it. She is shoved back and can't raise it for about a second; Perfect Notes never add strain. Without this, holding VOICE made her untouchable. (Decision for BASILICA, see below.)
- **Second Wind** is never on Down any more. That was the accidental-heal risk §10 calls out.
- **Full Voice** is never automatic now. It used to fire on any strike with a full meter.
- **Soundwave** does half damage to bosses.

## Boss identities (first pass, §8)

- **Doubt:** two decoys orbit it. Only the real one casts a ground shadow (the one fair tell). Strikes and
  Soundwaves pop decoys, which come back after ~4 s.
- **Sentinel:** frontal hits are blocked unless it is mid-CHARGE/SLAM or opened by a Perfect Note.
  Hits from behind always land.
- **Spark:** moves 1.5× faster.
- **In-Between:** jumps between the two ends of the arena every ~3 s.
- **Grey Area:** 2–4 doors (more as its HP drops). It vanishes into one and steps out of another.
- **Wraith:** backs off when she rushes or dashes at it. Walking in patiently works.
- **Sovereign:** fights from a raised throne ledge, reachable from the left platform or by Soundwave.
  Below 50% the throne breaks and it drops to the floor.
- **Tempest:** under 30% HP the storm absorbs Soundwaves ("GET CLOSE"), so she has to finish it in melee.
- **Princess:** uses the full toolkit (walk, Mic Check, Soundwave, Guard, Bass Drop, one heal, Full Voice
  after the first cycle).
  - Threshold I and II dialogue play at 66% and 33% of cycle one.
  - Zero HP is never victory. She rises at full health.
  - After the second "win" the score cuts out, the colours drain, and the final cut plays. Control is
    removed: "Again?", then "No.", then the merge.
  - Then HER / COMPLETE flickers to CONTINUE, Her Encore plays (blank book, THE END scratched through),
    the credits run, and the game returns to the title.

## Placeholders (need BASILICA art or decisions)

- **Princess** is still the existing heroine sprite set (Jandé likeness). The Adventurer Princess (§5) needs
  new sheets. The transformation is played as a page/ink/notes burst on the existing sprite.
- **Storykeeper** ~~is drawn in code~~. **Done 11-02:** painted portraits (8 expressions), a standing cutout and
  a pointing cutout, generated to the bible's description (§2): young, contemporary, hooded, page-texture
  coat, gold thread, fountain pen. **Redrawn 11-02 (client: "all characters Black, it's Atlanta"):** a Black
  man with rich deep-brown skin, in the same anime style as Princess. 12 images: 8 busts, 2 world cutouts, the
  blank-page panel and the Encore panel. **Still open:** the bible (§2) models his face and grooming on Frédéric,
  and no reference photo has been supplied yet.
- **All human characters are Black (client, 11-02).** The man in the memories was already drawn as a Black man
  and was left as he is. In the boss atlas the Thorn Queen (row 3) and the Blossom Revenant (row 2, also used by
  The Doubt and The Spark) had their pale skin recoloured to deep brown on all 9 frames. The Toadstool Warlock
  (row 5, The In-Between and The Grey Area) followed on client request: only his face and hands are deep brown.
  His white beard, grey side hair, eyes, moss collar and the mushroom stalk stay exactly as drawn. The client
  said "brown everywhere" meaning the brown was bleeding where it didn't belong. A pass that browned the beard
  too was wrong and was reverted. The Grey Area still shows him in black and white, because that chapter's `tint` is
  `grayscale(1)` on purpose. Row 8, The Groom Who
  Lied, is not used by Game I and was left alone; it is the live game's finale boss.
- **Princess's look (client, 11-02):** she is a Black woman with rich deep-brown skin, matching Jandé, and
  platinum-white hair as on Frédéric's board. The first art pass came out light golden-tan, because the
  prompt said "golden-tan" and lightened the board. All 27 Princess images were regenerated. **Every Princess
  prompt must state the skin explicitly** ("rich deep-brown skin, clearly deep brown, not tan").
- **Princess portraits and cards. Done 11-02:** 8 adventurer expressions, 8 storybook-gown expressions and a
  full-body battle pose for the VS card. **Still open:** her *gameplay* sprite is still the Jandé sheet set,
  so the world figure does not yet match the portraits. This needs new run, jump and attack sheets.
- **Prologue memories. Done 11-02:** six painted panels (together, the dance, an ordinary morning, the balcony,
  the bench, apart on the bridge), the blank page, the transformation, the merge and the Encore. They replace
  the fifteen code-composed vignettes.
- **Doubt and Grey Area** run on tinted stand-in atlas rows.
- **Worlds V, VI, VII, IX, X and XI** reuse existing paintings (see the map above).
- **Credits** list BASILICA and PRODBYKCTW only. Full credits are BASILICA's call.

## Removed or changed from the Jandé build

- **Removed:**
  - The placeholder lyric line under the floor (`drawLyric`) and the distance readout. HUD §10 allows no persistent text.
  - The ability bar, the LV bar and the chapter track from the in-run HUD. The chapter track is still in pause.
  - The paid gem continue in Game I. The runner (Game II) keeps it.
- **Changed:**
  - Score in the HUD is replaced by the Grace Note count.
  - Power-ups whose names collided with the new verbs: FULL VOICE (refill) is now DEEP BREATH, and
    BELT IT OUT is now TURN IT UP.
  - Jandé removed from game-facing copy: the title is now "Once Upon a Time / Game I"; the registry copy is
    neutral, pending Frédéric's text; the default leaderboard name is STORYTELLER.
- **Unchanged:** the Royal Runner (Game II) is untouched and reachable from the title's "ROYAL RUNNER — GAME II" link.

## NOT BUILT in this pass (bible items outside the four picked)

- **Storybook UI (§9).** Missing: spreads, Grace Note counts per chapter, Hidden Page / Perfect Pitch flags,
  completion %. Today "Storybook" is a chapter list.
- **Hidden Pages:** all 11 (§4). **Postgame:** Her Encore unlocks, Dress playable, The Archive, Boss Rush.
- **Settings and accessibility (§10):** control size/position, assists, text size, reduced flashing as its
  own toggle. The storm lightning is off under Reduce Motion today.
- **Art direction:** environment and platform art direction (§19), and the Adventurer Princess and other
  new art (§5, §21).
- **Game feel (§11):** hit-pause tuning and a unique Perfect Note sound beyond the current burst.
- **Game II.** Out of the bible's scope.

## Open decisions for BASILICA

1. **XP/levels** still run underneath (hearts and damage grow with kills). The bible rules out %-upgrades.
   Keep them, or remove them?
2. **Dash** is not in the ability table. Keep it?
3. **World reuse** for V/VI/VII/IX/X/XI until new environments exist. OK?
4. **Guard strain** (three ordinary blocks break Guard): keep it, or prefer a resource cost?
5. **Line of sight (Sept notes)** is unchanged. It still conflicts with the zoom directive.

## Saves
- **The story save** (`V2S.save`) only moves forward. Replaying an earlier chapter from the Storybook never rewinds it.
- Beating a boss saves the next chapter right away, so quitting on the tally does not lose the clear.
- **Continue from Bookmark** uses the run's own last bookmark (`RUN_BM`). Pause → RESTART CHAPTER resets it.
- The `?bg=1` viewer steps WORLDS (0–8). It never saves and never plays cuts.

## Independent review (2026-11-01)
A second-model review found 13 defects, 7 of them reproduced by running the game. All 13 are fixed in the same branch:
- the final cut could fire after leaving to the title and mark the game beaten (now a game-clock countdown, not a timer);
- the tap that closed a cut clicked whatever was underneath (clicks are eaten for 450 ms);
- a held key skipped a whole scene and leaked into play (key repeats are ignored, and keys held through a cut stay dead until released);
- a Storybook replay overwrote the story save;
- a clear was not saved until CONTINUE STORY;
- the bg viewer was broken and wrote saves;
- pause-restart did not reset the bookmark;
- there was no gamepad path through cuts (A/X advance, B/Start skip);
- Guard made her invulnerable (now strain);
- latched inputs fired after cuts;
- dash fired on left/right corrections;
- the mirror Princess wore the player's power-ups;
- Royal Runner showed Game I labels and a dead pause button.

Found afterwards while recording the walkthrough video: leaving a run while a story scene was playing carried the scene into the next run. Fixed: `storyAbort()` runs on title, new run and pause → exit.

## Verification (2026-11-01, headless Chromium, 1280×720 and iPhone 13)

- **Full prologue:** 15 vignettes, then the blank-page dialogue, then the transformation, then control.
- **Chapter I in full:** intro, Instigator reveal, gate bookmark, Warden cut, VS card, defeat cut, tally,
  CONTINUE STORY, transition, Chapter II.
- **All ten bosses II–X** fought and defeated, each through its defeat cut and tally, with no page errors.
- **Chapter XI:** reveal, VS, Threshold I/II, two false victories, final cut, merge, HER / COMPLETE /
  CONTINUE, Encore, THE END crossed out, credits, title.
- **Death:** STORY INTERRUPTED appears in about 1 s. Continue respawns at the bookmark (col 112) with 3 of 5 hearts.
- **Touch:** swipe-up on the d-pad jumped (y 362 → 225). VOICE, SECOND WIND and FULL VOICE render in
  portrait, and controls hide during cuts.
- **Checks:** the glyph gate is clean, `tools/check.cjs` passes, and no duplicate top-level names exist in
  the game IIFE.
