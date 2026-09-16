# CLIENT NOTES — Frédéric De Jesus (BASILICA), received 2026-09-16

> **STATUS: REVIEW ONLY. NO IMPLEMENTATION.** Frédéric: *"Before any additional
> work or changes are made, I'd like for us to connect and walk through these
> notes together."* Client: *"we're not making any changes until then… we're
> gonna start making changes when he's available hopefully sometime next week."*
>
> Nothing in this document has been built. It exists so the walkthrough starts
> from verified facts instead of impressions.

He also flags that **several items name story cuts, sequences, dialogue and
on-screen copy that still need writing** — the notes mark where those moments
go and what they must accomplish, not the final scripts.

---

## Checked before the call

Four of his items are answerable from the build right now. Three change what the
conversation should be about.

### ❓ "Stage 8 and onward has no music" — DOES NOT REPRODUCE

Tested by counting the oscillators the music scheduler actually creates during
4 seconds of real play, on **the Frédéric edition build**, started directly at
each stage:

| stage | 0 | 3 | 6 | 7 | 8 |
|---|---|---|---|---|---|
| oscillators / 4s | 12 | 16 | 14 | 18 | 16 |

That is the correct rate everywhere — the scheduler runs 8th notes at 92 BPM, so
~12 steps in 4s, and stage 8 is indistinguishable from stage 0. `STAGE_KEYS` has
nine entries indexed `%9`, so there is no missing-key bug either.

**But there is something real underneath it.** There are no per-stage
compositions. The whole score is **one four-chord progression transposed by a
semitone table**, and that table is `[0,3,5,7,2,8,10,5,7]` — **stage 8 reuses
stage 3's key and stage 9 reuses stage 4's.** So the last two stages are the only
ones that introduce nothing new to hear.

**Take to the call:** is he reporting *silence* (a bug reachable some way I
haven't found — likely mid-session or through the boss→next-stage path, which I
could not drive in the harness) or *sameness* (the finale having no music of its
own)? Those are completely different jobs. If it is sameness, the fix is unique
keys/progressions for the late stages, which is cheap.

### ❓ "Checkpoints // so you don't start all the way over when you lose" — ALREADY EXISTS, BUT IT COSTS

There is a continue system: `CHECKPOINT` (stage) + `CHECKPOINT_X` (her exact x,
recorded every frame), restored on continue. **It is not free.** `MAX_CONTINUES`
is 5 and each one costs gems on a rising scale (`continueCost() = RUN_CONTINUES+1`).

**Take to the call:** he may have run out, or never seen it as a checkpoint
because it reads as a paid revive. Making it free — or free for the first N — is
a small change. Building a *new* checkpoint system is not needed.

### ❓ "What are the words at bottom during gameplay?" — ANSWERED

`drawLyric`. Five placeholder taglines on a 15-second rotation at 30% opacity,
seated in the undercroft band below the floor:

1. *"Once upon a time…"*
2. *"The song was a promise. The promise was a lie."*
3. *"Her voice is the only ring she needs."*
4. *"She turned heartbreak into a headline."*
5. *"JANDÉ – Once Upon A Time"*

**These are placeholders, not the song.** "Actual song lyrics" has been an open
thread awaiting the client since July. His "Determine copy" note is the same ask.

### ⚠ "Widen line of sight (while playing)" — CONFLICTS WITH AN EARLIER CLIENT DIRECTIVE

This is the one item that contradicts something already delivered on request.

Read-ahead is currently **9.3 tiles** in portrait. The reference figure is
NES/Mario at **~9.6**, so the game sits essentially on it. Widening the view
means zooming out, which makes Jandé smaller — and the character scale is at
`BASE 0.92 / VIEW_W 440` (hero 70px portrait / 79px landscape) **because the
client asked for it**: *"Can we zoom in on the characters a bit more? Jandé and
the enemies definitely deserve to be seen clearly."*

**Take to the call:** these two asks pull opposite ways and someone has to
choose. Options are (a) keep the zoom and widen only in landscape, (b) trade
hero size back for view, (c) a dynamic camera that pulls out when she runs — the
most work, and the only one that gives both.

---

## OVERALL

| item | what it touches | notes |
|---|---|---|
| Load screen → impressive hero cover image | new art asset | Straightforward to wire once the art exists. **The art is the job.** |
| Queen's Registry / Pick Game / Stage Start — rewrite copy | DOM screens | Cheap to change. Blocked on copy, not code. Watch the two-tier typography rule: Storyboo is display-only, body text uses `var(--body)`. |
| Determine copy | — | Writing task |
| Add story cuts (start & end of both games) | **new system** | There is no cutscene framework. Needs a sequencer (text/art/timing/skip), then content per beat. Sizeable, and the biggest non-art build in the notes. |
| What are the words at bottom | — | **Answered above.** |

## GAME I (Action RPG)

| item | what it touches | notes |
|---|---|---|
| Starting / boss / ending story cuts + script | cutscene system | Same framework as above |
| **Idle dance → less chaotic (ballerina spin)** | **protected art** | `dance` is on the do-not-modify list of Jandé's original side-view art. This needs a **new sheet**, which means AutoSprite → **blocked on `$AUTOSPRITE_KEY`** |
| Minion & boss intro sequence (Street Fighter VS style) + snippy remark | new UI + art + script + a gameplay pause | Real feature. Also a design question: a pause on **every new minion type** will interrupt the run repeatedly — likely wants to be once per type per stage |
| Movement: joystick vs d-pad vs finger-direction | touch input rework | Doable. `CTRL_TOP` is measured, not guessed — anything laid out against the bottom must use it |
| **Swipe up to jump** | touch input | Small and high value. Worth noting the runner already uses swipes, so this also makes the two games consistent |
| Button placement | touch layout | Cheap |
| Checkpoints | — | **Exists, costs gems — see above** |
| Widen line of sight | camera/zoom | **Conflicts with the zoom directive — see above** |
| Stage 8+ no music | audio | **Not reproduced — see above** |

## GAME II (Royal Runner)

| item | what it touches | notes |
|---|---|---|
| Starting / ending story cuts + script | cutscene system | As above |
| **World redesign → real-world Atlanta, obstacles as "male Kanker sisters"** | **the whole of Game II's art** | **By far the largest item in the notes.** Royal Runner is a hand-written WebGL world (GLWORLD) with nine themed stages, plus obstacle, chaser and prop art. Re-theming to a real city means new environment art for all nine, new obstacle set, new antagonist designs. This is a project phase, not a task — it should be scoped and priced on its own |
| Different outfit for Game II (tank, shorts, sneakers) | new sprite sheets | `bkrun` / `bkjump` / `bkslide` are back-view and **not** protected, so this is allowed. Needs AutoSprite → **blocked on the key** |
| Purple Guy / Ghost of Relationships Past — alternate designs | chaser art | AutoSprite |
| Purple Guy first-appearance sequence + remark | same system as the Game I VS sequence | Build once, use in both |

---

## What this adds up to

**Three buckets, and they have very different shapes:**

1. **Cheap, do-now once decided** — copy rewrites, button placement, swipe-to-jump,
   free checkpoints, unique keys for the late stages.
2. **Real features** — the cutscene/story framework and the VS-intro sequence.
   Both are build-once-use-many; doing the VS sequence and the story cuts on one
   shared sequencer is the efficient order.
3. **A phase of its own** — the Game II Atlanta redesign. Should not be folded in
   with the rest.

**One thing worth doing before the call, because it unblocks several items at
once:** every new-art item here — the idle dance, the Game II outfit, the Purple
Guy redesigns, and more jump frames — runs through AutoSprite, which is blocked
only on `$AUTOSPRITE_KEY`. Nothing else stands in the way. Key page:
`https://www.autosprite.io/apikey`.

**Still outstanding from before these notes:** EmailJS credentials (sign-ups
still fall back to `localStorage`, so the email-capture goal is not yet live),
and rotating the Cloudflare and AutoSprite tokens.
