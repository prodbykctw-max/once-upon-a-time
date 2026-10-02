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

## Borrowing the Corner Store Dash world technique — YES, the front half

**Client, 10-02:** *"Look at the EBT Presents Corner Store Dash repo. I used a
technique to create the world based off Atlanta using actual overhead map overlay
technology — see if you could borrow that."*

Read it: `prodbykctw-max/EBT-PRESENTS-CORNER-STORE-DASH`, `docs/DRIVE.md` and
`drive/tools/`. **It is real, it is fully scripted, and it is a strong fit —
but only the first half of it.**

### What it actually is

**OpenStreetMap, not Google Maps.** A 1.1 km drive through real downtown
Atlanta — Luckie St → Auburn Ave — routed on OSM data with one-ways respected,
street widths measured from OSM's mapped sidewalks every 10 m, real tram track
and MARTA platforms. Seven scripted steps, nothing hand-tweaked:

| # | step | tool |
|---|---|---|
| 1 | Overpass (OSM) extract | → `drive/osm/*.json` (git-ignored raw data) |
| 2 | **OSM + sampled elevation → `world.json` in local metres** | `build_world.mjs` |
| 3 | Blender blockout from `world.json`; hero buildings, procedural facades, prop scatter | `bl.py`, `blender_blockout.py` |
| 4 | Bake AO + bounce in Cycles (sun stays real-time) | |
| 5 | LODs, per-tile merge, glTF via gltf-transform | `optimize_assets.mjs` |
| 6 | Engine: **three.js (WebGPU/WebGL2) + Rapier** | |
| 7 | Scripted browser QA + screenshots | `tests/qa.mjs` |

Elevation comes from **Open-Meteo (Copernicus DEM)** — free HTTP, no key.

### Why it fits Royal Runner unusually well

**The coordinate model is already the same.** Corner Store Dash runs everything
in *route space* — `s` = metres along the route, `d` = metres across it — so
lanes, obstacles and collisions line up with what's painted on the road. That is
**exactly** Royal Runner's model: distance travelled plus a lane offset. The
route polyline that `build_world.mjs` emits is, with no conceptual translation,
the thing Royal Runner already runs along.

### Where it stops — steps 5 and 6 do NOT transfer

Corner Store Dash renders with **three.js + Rapier, consuming glTF with meshopt
and KTX2**. Royal Runner is the hand-written **GLWORLD** engine: a simple
projection (`sx = W/2 + wx*s`, `s = 300/(300+z)`) over flat textures, with no
glTF loader, no physics engine, no LODs and no PBR. The baked city cannot be
dropped in. The choice is:

* **(a)** use the OSM data to drive **baked art** for GLWORLD's existing texture
  slots — grounds, props, obstacle atlases — and keep the engine, or
* **(b)** port Royal Runner to three.js, which is a rewrite.

**(a) is the realistic path, and the back half of it already exists in THIS
repo.** `tools/bake_world.py` already bakes the Royal Runner world pack, and
`tools/blender/` already holds `outdoor_worlds.py`, `obstacles3d.py`,
`ground_tiles.py`, `ground_pbr.py` and `outdoor_props.py`. So the join is:

> **Corner Store Dash steps 1–3 → Jandé's existing bake tools → GLWORLD's
> existing texture slots.** Borrow the OSM front end; the Blender back end is
> already written here.

Step 2 is the piece genuinely worth lifting as-is: `build_world.mjs` turns an
OSM extract plus an elevation grid into one `world.json` of roads, widths,
building footprints and heights, and a route polyline, in local metres — *"one
source of truth for both the Blender build and the game engine."*

### Two practices to copy, not just the code

**Never build over landmarks.** The storefront row in Corner Store Dash is
fictional and sits on an ordinary commercial lot; the SCLC headquarters, Prince
Hall Masonic Building, Ebenezer Baptist and the King Center are all left exactly
as they are, and `blender_hero_row.py` **prints every OSM lot it clears** so the
list can be checked after any placement change. Carry that discipline over.

**OSM attribution is a licence condition, not a courtesy.** `build_world.mjs`
carries `'Map data © OpenStreetMap contributors (ODbL); elevation Copernicus DEM
via Open-Meteo'`. OSM is ODbL — if Jandé's runner ships on OSM-derived geometry,
**that attribution has to appear in the game too.** Easy to forget, and this is
paid commercial work on a public URL.

### ⚠ HOME IS FICTIONAL — the client raised this and he is right

**Client, 10-02:** *"Except for her home — it's gonna be a home-ish type of
environment, but we're not gonna use our real house, because we don't want her
actual personal information given out like that."*

**Correct, and the pipeline makes it easy to get wrong**, because it pulls real
footprints from real coordinates by default. A real residential address in a
public promotional game is doxxing, and it cannot be taken back once deployed.

The precedent is already in Corner Store Dash: the hero row is a **fictional
building placed on a real street**. Do the same — a representative Atlanta
residential block, a house that is invented. Everything about it should read as
hers without being locatable.

Worth a quick pass over the rest of the list for the same reason: the public
venues are the point and should be recognisable, but **"Church"** deserves the
same question as Home if it is her actual congregation. Separately,
**Mercedes-Benz Stadium** is a trademarked name — depicting the building is
ordinary, putting the branding on screen in a commercial promo is a question for
the client, not a blocker.

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

### ✅ THE COURTSHIP-GESTURE SET (client, 10-02) — this is the answer

**Client:** *"To jump over could be somebody on their knee trying to offer a ring
in marriage. To go under could be somebody holding out a bouquet for her. Side
swipe left or right for one guy, and they react by turning that way, trying to
give her their bouquet or get a hug."*

**Take this.** It is better than a generic trio of bullies for two reasons, and
the first one is structural rather than a matter of taste.

**1. It solves the readability problem below, by construction.** The three
gestures naturally occupy three different heights, which is exactly what the
three cell shapes need:

| gesture | natural silhouette | required action | cell |
|---|---|---|---|
| down on one knee, ring out | **low and wide, no standing head** | jump | `oblow` 256×96 |
| bouquet held out at arm's height | **a horizontal arm with clear space beneath** | slide under | `obgate` 256×192 |
| stood up, arms open for a hug | **solid, square, fills the lane** | dodge sideways | `obwall` 256×224 |

A proposal is low, an offering is mid, an embrace is full-body. The gesture set
and the gameplay verbs line up on their own — nothing has to be forced.

**2. The gameplay verb becomes the story.** The song is *the promise was a lie.*
She spends the entire run **hurdling proposals, ducking bouquets, and sidestepping
men who want to hold her.** Every obstacle is a romantic gesture she refuses.
That is the strongest idea in this redesign and it costs nothing to adopt.

**It also fixes the secondary risk for free.** Three purple men could still read
alike at speed even with different silhouettes — but the **props carry the
accent colour**. A gold ring and a bright bouquet against the purple are the
tell, readable before the figure is.

**One real cost to price: the reaction.** *"They react by turning that way"*
needs more than one drawing. Today each obstacle is a **single static cell** per
stage — `FX.drawImage(TEX.obwall, ai*256, 0, 256, 224, …)`. A turn-to-follow
needs extra frames per obstacle (wider atlas or a second row) plus logic in
`drawT` to pick the frame from how close she is and which side she passed. Not a
blocker, and worth it — but it is an engine change, not just art.

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

## The Groom's Shadow — "he's just a blob", and the history says why

**Client, 10-02:** *"The purple groom guy, he kind of is — he's just a blob. We
never improved on him in the first place."*

**Confirmed by looking at the shipped art.** Four frames at 176×224, and he is a
Blender primitive assembly: sphere head, flat slab shoulders, cylinder arms, cone
body, two pink dots for eyes, no hands. The four frames are nearly identical, so
there is barely an animation either.

**And the git history explains it — this is the useful part.** The pipeline shows
three states in order:

1. the original **Blender primitive** purple groom — top hat, pink eyes, cape;
2. `embed_chaser.py`: *"Replaces the Blender primitive chaser. Source is an
   AutoSprite spritesheet"* — a proper character model went in;
3. `revert_chaser_purple.py`: *"Restore the ORIGINAL purple Groom's Shadow… 
   replacing the AutoSprite black-tailcoat villain."*

**The revert was a COLOUR decision that cost the craft.** The AutoSprite figure
was better built but came back in a black tailcoat; going back to purple meant
going back to the primitive blob. Nobody chose the blob — they chose the purple,
and the blob came with it.

**So the brief is not "redesign him", it is "stop making that trade":** an
AutoSprite-quality figure that is *also* purple, top hat, pink eyes, cape. Both
at once. That was always available; it just was not asked for.

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
