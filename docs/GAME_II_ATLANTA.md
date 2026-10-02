# GAME II — ATLANTA REDESIGN BRIEF

> **STATUS: BRIEF ONLY, NOTHING BUILT.** Direction captured 2026-10-02. Frédéric
> has asked to walk through his notes before implementation begins
> (`docs/CLIENT_NOTES_FREDERIC.md`); this records what the redesign actually
> consists of so that conversation can be about real numbers.

## The direction

**Client, 10-02:** *"The whimsical world of this fairytale game is not right for
the project. On the runner version, those three obstacle types are actually
supposed to be guys that she's avoiding."* And: *"The runner environment should
be places in the city of Atlanta."*

**Frédéric's note, 09-16:** *"World Redesign // Set in real world, running
through Atlanta and what she's ducking, hopping over and dodging are the
proverbial male versions of the Kanker or Gross sisters."*

Both say the same thing. Royal Runner stops being a fairytale and becomes
**Jandé's actual Atlanta**, with the obstacles as men she is dodging.

## ⛔ NOTHING IS REPLACED — THIS IS AN ADDITIVE SECOND ASSET SET

**Client, 10-02:** *"We don't have to remove anything — I'm gonna repurpose all
of this princess aesthetic stuff for another game, so I definitely want to keep
all of the assets. But we're basically gonna be generating a new world and new
assets and even a new Jandé at this point."*

**This is the single most important constraint in this brief, and the existing
tooling violates it.**

`tools/compose_obstacles_all.py` says so in its own docstring: it *"replaces
cells, saves a new sha1, repoints index.html, **deletes the old file**."* Run as
written, it destroys exactly the fairytale obstacle art the client just said he
is keeping. **It must be made additive before it is run again** — write new
atlases alongside the old ones and leave every existing `web/` file in place.

The same applies to every other swap script in `tools/` (`embed_*`,
`compose_*`). Audit each for in-place replacement before use.

### What additive looks like here

The project already has the pattern — `CARDS_ON=false` kept all 38 multiplane
card assets rather than deleting them, so the feature is one flag away from
coming back. Do the same thing at a bigger scale:

| today (keep, untouched) | add alongside |
|---|---|
| `oblow` / `obgate` / `obwall` — fairytale furniture | three new atlases, the Atlanta men |
| `GLWDATA.grounds[9]` — fairytale ground | nine Atlanta surfaces |
| `GLWDATA.props` — pots, globes, topiary | an Atlanta street-furniture sheet |
| `LOOK[9]` — fairytale skies | a second `LOOK` table |
| `bkrun` / `bkjump` / `bkslide` — gown, back view | the new Jandé: tank, shorts, sneakers |
| chaser — the Groom's Shadow | kept; Frédéric wants alternates, also additive |

Then one switch picks the world, the way `CARDS_ON` and `FG_STAGES` already do.
That keeps the princess build fully playable for the other game he wants to
repurpose it into — which is only true if nothing is overwritten on the way.

**One housekeeping consequence:** the shipping checklist audits that `web/`
references exactly equal the files on disk, *"no missing, no orphans."* A kept
-but-unused fairytale set will read as orphans. Either keep both sets referenced
behind the world switch (preferred — it is how `CARD_DATA` stays referenced
while `CARDS_ON` is false), or teach the audit about an intentionally-retained
set. Decide before the first new atlas lands, not after the audit starts failing.

## Tone — and the one architectural consequence of it

**Client, 10-02:** *"All of this is gonna be heavy. Atlanta all in your face.
Atlanta is gonna be very Atlanta."*

Not a generic city with a skyline in the fog. Recognisable, specific, and
unapologetic — the whole point of the locations list is that these are **real
places people will recognise**, so the art has to be confident enough to be
identified, not suggested.

**This makes the two games deliberately diverge,** which is consistent with
Frédéric's *"explore different outfit to further differentiate the games."*
Game I stays the fairytale. Game II becomes her actual life. Treat that split as
the governing principle rather than something to reconcile.

### ⚠ The colour grade is currently GLOBAL, and this breaks that

`CLAUDE.md` carries a binding rule: `--grade` (CSS, the 2D canvas) and `GRADE`
(GLSL, the four fragment shaders) must carry **the same numbers in the same
order** — brightness 0.93, contrast 1.20, saturate 1.34 — because the hero has to
match the world she stands in. Those values were set to answer *"the colours
aren't rich like pixel art colour is rich."*

They are **one setting for the entire game.** A fairytale Game I and an in-your-
face Atlanta Game II are not going to want the same brightness, contrast and
saturation. So the rule has to become **per-mode**: two sets of numbers, with the
canvas and GLSL halves still locked to each other *within* each mode. That is a
small change and a cheap one — but it has to be done deliberately, because
changing one half without the other is a mistake this project has already made
and documented. Spec: `docs/COLOUR_GRADE.md`.

## Locations (client, 10-02)

| # | location | note |
|---|---|---|
| 1 | Home | |
| 2 | Wade Walker Park | |
| 3 | Stone Mountain Park | |
| 4 | Dekald School of the Arts | likely **DeKalb** School of the Arts — confirm spelling before art reference |
| 5 | Track & Field | |
| 6 | Mercedes-Benz Stadium | |
| 7 | Old Apache Kafe | an Atlanta music venue — confirm the exact spelling the client wants on screen |
| 8 | Church | |

### ⚠ EIGHT LOCATIONS, NINE STAGE SLOTS

The runner is hard-wired to **nine** stages — `LOOK[]` has 9 entries,
`GLWDATA.grounds[]` has 9 textures, and all three obstacle atlases are 9 cells
wide. The list has eight. **This needs a decision before any art is made:**

* add a ninth location, or
* let one location run two stages (day/night, or two areas of Stone Mountain), or
* cut the runner to eight stages — the smallest code change, but it desyncs the
  two games, which both currently run nine.

**These read as a life, not a tour** — home, the park, school, the track, the
stadium, the venue, the church. Worth confirming that the stage ORDER is meant to
be that arc, because if so it is also the spine for the Game II story cuts
Frédéric asked for.

## The three obstacles as men

They already map exactly onto his "ducking, hopping over and dodging":

| type | player must | cell size | today | as a man |
|---|---|---|---|---|
| `oblow` | **jump over** | 256×96 | book crate, balustrade, stage riser | someone low — crouched, sprawled, sitting on a stoop |
| `obgate` | **slide under** | 256×192 | table, marble arch, lighting truss | arms braced wide overhead — she goes under |
| `obwall` | **dodge sideways** | 256×224 | bookcase, colonnade, proscenium | standing square, filling the lane |

### ⚠ THE REAL DESIGN RISK: SILHOUETTE READABILITY

This is the thing most likely to bite after the art is paid for.

Right now the three shapes are **different kinds of object**, so they telegraph
the required action instantly at speed — a low crate reads *jump*, an arch reads
*go under*, a solid bookcase reads *go around*. Make all three a man and they all
become roughly **person-shaped**, and the player loses that instant read. In an
endless runner that is not a cosmetic problem; it is a fairness problem.

**So the brief for the art is silhouette first, character second:**

* `oblow` — **wide and low**, nothing above knee height. The silhouette must not
  have a standing head.
* `obgate` — a **clear arch of negative space beneath him**. Both arms up and
  braced, feet apart. The gap is the readable feature, not the man.
* `obwall` — **solid, square, no gap at all**, filling the lane edge to edge.

If the three silhouettes do not read differently in pure black at speed, the
redesign has failed regardless of how good the characters look. Worth testing as
black shapes before any detail is rendered.

## How the men get made — the path already exists

**Client, 10-02:** *"We'd have to basically design guys the same way we designed
the Prince and the villain… she wants them to look like the Gross Sisters from
The Proud Family, purple, since we already have a purple villain chasing you."*

**That path is already built and documented in `tools/`.** This is the single
cheapest fact in this brief: nothing new has to be invented, only drawn.

1. **AutoSprite** generates the poses on a solid-white backdrop.
2. **White-key by flood fill inward from the border** — `compose_prince_as.py`.
   Only white *connected to the edge* is background, so white inside the figure
   survives. That exact care is why the Prince kept his dress shirt.
3. **Compose into the atlas cells** — `compose_obstacles_all.py` already swaps
   new art into cells of `oblow` / `obgate` / `obwall`, writes a new sha1,
   repoints `index.html` and deletes the old file.
4. **Embed** — `embed_obstacles.py`.

Two caveats: `compose_obstacles_all.py` carries a hard-coded Windows path
(`C:\Users\Owner\…`) from the laptop session and needs that parameterised to run
in a cloud session; and stages 4 and 7 use border-only keying because their
bodies are near-white — irrelevant once the cells hold people instead of marble
and cloud, so that special case can go.

## The purple is already ours — we do not need to borrow it

Verified in the pipeline: the chaser is **The Groom's Shadow — purple, top hat,
pink eyes, cape**, at 176×224 over 4 frames. An AutoSprite black-tailcoat
villain was made to replace him and then **deliberately reverted back to the
purple groom** (`tools/revert_chaser_purple.py`). So purple is not an
association this project is reaching for; it is the established colour of *the
men in her past*, chosen once already on purpose.

That makes the three obstacles **lesser shades of the thing chasing her** —
same family, lower rank. The Shadow is the one she cannot outrun; these are the
ones she hops, ducks and sidesteps. That is a stronger idea than the reference
and it is the project's own.

### On the Gross Sisters reference

Take the **archetype** — a trio of purple-toned intimidators who instantly read
as a matched set — not the designs themselves. Those are specific copyrighted
Disney characters, and this ships on a public URL as paid commercial work. It is
the same call already made across this project: **"reskin, don't copy"** is a
binding rule in `CLAUDE.md`, the way Silksong's mechanics were re-expressed as
Jandé's voice with the word itself at zero in shipped text. The brief to the
artist should describe *a trio of purple-toned men who read as a set*, and let
them be Jandé's.

## Full asset inventory

What the runner's per-stage world is actually made of:

| what | count | where | kind |
|---|---|---|---|
| `LOOK[]` — fog, sky, sun, tint, hill height, prop picks | 9 entries | inline table | **numbers only, no art** |
| `GLWDATA.grounds[]` — ground texture per stage | 9 | `web/*.jpg` | art — street, sidewalk, track, turf, car park |
| obstacle atlases | 3 × 9 = **27 cells** | `oblow` 256×96, `obgate` 256×192, `obwall` 256×224 | **art — the men** |
| prop atlas | 1 sheet, 16 prop types | `GLWDATA.props` | art — currently pots, globes, topiary; Atlanta needs street furniture |
| chaser (Purple Guy) | 1 | `TEX.chaser` | art — Frédéric also wants alternate designs |
| her back-view sheets | `bkrun` `bkjump` `bkslide` | 25 frames each, 256×256 | art — the tank/shorts/sneakers outfit |
| wall / ceiling / grass | 3 shared | `GLWDATA` | art, only if interiors are kept |

**One line of that table costs nothing and one costs the project.** `LOOK[]` is
pure numbers — retuning nine skies from fairytale to Atlanta daylight, dusk and
stadium night is an afternoon with no new assets. Everything else is new art.

## What is blocking it

**All of the character art runs through AutoSprite, and AutoSprite is still
locked.** Re-verified 10-02, two ways:

* `python3 tools/autosprite.py ping` — fails, and `$AUTOSPRITE_KEY` is not set
* the claude.ai connector is enabled and its tools load, and `get_account` still
  returns **`Unauthorized: provide an MCP API key`**

Same finding as August: **the key is the only thing in the way.** Nothing else
about the pipeline is broken. `https://www.autosprite.io/apikey`.

Environment art (grounds, props) comes from Blender/Cycles, which is not blocked
but is laptop render time.

## Sequencing, if it goes ahead

1. **Decide the ninth stage**, and whether the order is the life arc.
2. **Black-silhouette test** for the three men before any rendering. Cheapest
   possible way to kill the readability risk.
3. **`LOOK[]` retune** — free, no assets, and it will immediately show whether
   Atlanta reads at all in this engine.
4. Grounds and props.
5. Characters, once the key exists.

Steps 1–3 can happen without AutoSprite and without spending anything.
