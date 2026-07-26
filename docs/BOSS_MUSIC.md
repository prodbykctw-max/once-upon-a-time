# Client request — darker, dynamic music during RPG boss fights

**Client, 2026-07-26:** *"Music should change to something darker and dynamic
during boss fights on the RPG."*

## The good news: this is ~90% already built and simply never wired up

`musTick()` (index.html ~line 1361) is the generative score. It **already has a
"darker mode"** — but it is hooked **only to the Royal Runner's chaser**:

```js
var danger = (MODE==='temple' && GS.t3 && GS.t3.chase>0);   // ← runner only
...
ch.forEach(function(iv){                                     // pad flattens a semitone
  var f = root*2*Math.pow(2,(iv + (danger?-1:0))/12); … });
if(danger && s%8===4)
  tone(root*2*Math.pow(2,1/12), 1.2, 'sawtooth', 0.03,0.3,0.8, 0, t);  // tension rub
```

So the **RPG boss fight currently gets no musical change at all** — the same warm
major pad keeps playing while the Shadow of the Groom darkens the screen. The
audio and the art are telling the player different things.

## Quick win (one line)

```js
var danger = (MODE==='temple' && GS.t3 && GS.t3.chase>0)
          || (MODE==='side'   && GS.bossActive);
```

That alone flattens the pad and adds the tension rub during every boss fight.
Ship this first — it's a one-line change and immediately correct.

## Do it properly: drive it from `GS.bossMood`, not a boolean

`GS.bossMood` already exists — a **0→1 eased value** that drives the Shadow of the
Groom wash and vignette (`GS.bossMood += ((bossActive?1:0) - bossMood) * 0.05`).

Using it for audio too means **the score darkens on exactly the same curve as the
screen does** — dread arrives as one event instead of a hard audio flip against a
soft visual fade. That's the difference between "a different track" and "the room
turning on you."

```js
var bm = (MODE==='side' ? (GS.bossMood||0) : 0);       // 0 → 1, already eased
var danger = (MODE==='temple' && GS.t3 && GS.t3.chase>0) || bm > 0.15;
```

### Musical direction (using primitives already in the file)

All of these use the existing `tone()` / `hiss()` / `rootHz()` / `MUS_CH` — no new
audio machinery needed.

| Layer | Now | During a boss (scale by `bm`) |
|---|---|---|
| **Chords** | `MUS_CH=[[0,4,7],…]` — major triad | **Flatten the third to a minor triad** (`0,3,7`). This single interval is what actually reads as "darker" — more than volume or filtering. Blend: `iv - (iv===4 ? bm : 0)` |
| **Root** | `rootHz(1)` = 110 Hz × stage key | Add a **sub an octave down** at `bm` gain — weight, not loudness |
| **Bass pulse** | `s%4===0`, soft sine | Harder attack, slightly longer decay; add `s%4===2` so it drives in eighths |
| **Hats** | ride `GS.speed>6.5` | In side mode `GS.speed` isn't the tension signal — ride `bm` instead so they tighten as the fight escalates |
| **Tension rub** | 1 sawtooth every 8 steps | Gain × `bm`; at `bm>0.8` also add a **minor-second rub** (root × 2^(1/12)) for real unease |
| **Drone** | — | New: a very low `sawtooth` at root/2, gain ≈ `0.02*bm`, long attack — the bed that makes it feel like a boss room |
| **Tempo** | fixed `sd=0.3261` (92 BPM) | Optional: `sd * (1 - 0.06*bm)` ≈ 98 BPM at full dread. **Careful** — `MUS.next` scheduling assumes a stable `sd`; only do this if it stays glitch-free through the resync branch |

### Enrage
The boss state machine has a **RAGE / enrage phase** at low HP. Push `bm` past 1
there (e.g. `bm*1.25`, clamped where it's used) so the final phase is audibly the
peak, not a plateau.

### Resolution on defeat
`GS.bossMood` eases back to 0 by itself once `GS.bossActive` is false, so the
score **lifts on its own** as the boss dies and the STAGE CLEAR tally rises. That
release is worth protecting — don't hard-cut the music on defeat.

## Guardrails
- **Respect the mute channels.** `musTick` already early-returns on `AUD.muted` /
  `AUD.musOff` — keep every new layer inside that guard so the independent
  MUSIC / FX toggles still work.
- **Reduce-motion ≠ reduce-audio.** `SET.reduceMotion` gates ambient visual loops;
  don't gate the boss score on it. If an audio-intensity preference is wanted,
  that's a new setting.
- The score is **generative, not a file** — so this is a handful of conditionals
  inside `musTick`, not a new asset. No size cost.

## Verify
Enter a boss arena on `?stage=0` and confirm: the pad turns minor as the screen
darkens (same curve), the drone comes in under it, hats tighten, enrage is
audibly the peak, and the score lifts as the boss dies. Then confirm the MUSIC
toggle still silences all of it and the FX toggle still doesn't.
