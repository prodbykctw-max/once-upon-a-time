# Atlanta world build (Game II)

Turns real Atlanta places into `world.json` in **local metres**, which is what
both Blender and the Game II renderer read. Adapted from the technique in
`prodbykctw-max/EBT-PRESENTS-CORNER-STORE-DASH` (`drive/tools/build_world.mjs`),
whose one idea worth copying is exactly that: *one source of truth for both the
Blender build and the game engine.*

```bash
node tools/atlanta/resolve_locations.mjs      # names -> OSM ids + coords
node tools/atlanta/build_world.mjs mbs 350    # one location -> world/mbs.json
blender --background --python tools/atlanta/blender_blockout.py -- mbs
python3 tools/atlanta/test_blockout.py       # geometry tests, no Blender needed
```

## The blockout

`blender_blockout.py` turns `world/<key>.json` into a massing model and saves
`blender/<key>_blockout.blend`. Idempotent — it rebuilds from an empty file
every run.

**Three things carried from the source project because they are hard-won:**
one object per building (later passes need per-building facades and LODs, and
the draw-call budget is met by merging per tile at *export*, not here); roads
merged per highway class into a single mesh, which is where draw calls are
actually saved; and **the winding fix** — rings are forced counter-clockwise
before extruding, or the solidified normals point inward and every building
renders inside-out, which looks exactly like a lighting bug and is not one.

**Three changed on purpose:** no hard-coded laptop path (the repo is derived
from the script's own location, with a `JANDE_ROOT` override); the ground is a
**flat plate** and named `ground_FLAT_no_elevation_data`, because our extractor
does not fetch an elevation grid yet and Atlanta is not flat — Stone Mountain
least of all; and the route is a **`ROUTE_CANDIDATE`** drawn along the longest
way in the extract, not an authored one, so nobody mistakes it for a decision.

**Guessing happens in one place, visibly.** The extractor emits `h: null` rather
than inventing a height. The blockout fills it from a per-kind table, flags the
object `height_estimated`, prefixes the name `EST_`, and gives it an **orange**
material — so a glance at the viewport separates what is surveyed from what is a
guess. The same goes for road widths: `lanes` is used when OSM gives it, and the
report says how many ways fell back to a class width.

**It reports against the budget rather than leaving it to export.** Triangle
count is printed every run, with a warning past 500k.

### Testing it without Blender

Blender is not installed in the cloud container, and the bugs in a blockout
script are not Blender bugs — they are geometry bugs. `test_blockout.py` stubs
`bpy`/`bmesh`, runs the real script against a world built of deliberately awkward
shapes (a clockwise ring closed by a repeated vertex, a building with no height,
a degenerate two-point ring, a way with no lane count), and asserts on the
geometry it produced. **10 checks, all passing.**

## What was measured, so nobody re-learns it

**Geocode with Nominatim, pull geometry with Overpass.** A name-regex search over
a metro bbox on Overpass took 65 s and then rate-limited; Nominatim answered the
same question in **0.76 s** with the OSM id and a bounding box.

**Overpass mirrors, from this container:**

| endpoint | behaviour |
|---|---|
| `overpass.kumi.systems` | **works** — but queues; 65 s for a trivial query |
| `overpass.private.coffee` | works, same queuing |
| `overpass-api.de` | resets the connection ~7.5 s in, every time |

**From THIS cloud container, the bulk fetch does not complete — and it is the
network, not the code.** The failure signature is consistent and measurable:

| route | result |
|---|---|
| Nominatim (small, sub-second replies) | **works every time** |
| `overpass.kumi.systems` / `private.coffee` | reach the server; queries **504 after ~64 s** or 429 |
| `overpass-api.de` | relay closes the tunnel after ~8 s, `517 B sent, 39 B received` |
| `download.geofabrik.de` (static `.osm.pbf`) | **same relay signature**, closed after 7 s |

The pattern is that **short requests succeed and long or large transfers get
dropped**, which is exactly what an Overpass query is — it queues server-side
before it answers. The query itself is valid: a 504 means the server accepted it
and ran out of time, not that it refused it.

**So run `build_world.mjs` where the connection is ordinary — the laptop.** It
caches every result to `cache/`, so the extract can be produced once there and
carried over. This is almost certainly how the source project's own
`drive/osm/auburn.json` was made; that file is git-ignored and was never fetched
in CI.

**They also rate-limit hard.** Two queries in quick succession earns HTTP 429 across
mirrors, and 503 under load. Both clear in tens of seconds — the helper backs off
30 s on 429/503/504 and caches every result to `cache/` so a query is never run
twice.

**HTTP 406 is not a server problem — it is a malformed query.** `out geom tags;`
is invalid Overpass QL (`out geom;` already carries tags). It answers 406, which
looks exactly like a server fault. The helper now bails immediately on 406 rather
than retrying, and says why.

## Rules that are not negotiable

**OSM is ODbL.** Every `world.json` carries
`Map data © OpenStreetMap contributors (ODbL)`, and **that attribution has to
appear in the shipped game**, not just in the data file.

**Home is fictional.** Client: *"we're not gonna use our real house, because we
don't want her actual personal information given out like that."* It is never
geocoded — a fictional house on a representative street, the same way Corner
Store Dash puts a fictional storefront row on a real block. The same question
applies to "Church" if it is hers.

**Never build over landmarks.** Carried over from the source project, whose
`blender_hero_row.py` prints every OSM lot it clears so the list can be checked.

**Heights are never invented.** A building with no `height` and no
`building:levels` is emitted with `h: null`. Downstream decides what to do with
that; the extractor does not guess.

## Location status

| location | status |
|---|---|
| Wade Walker Park | `way/34775500` |
| Stone Mountain Park | `relation/1447405` |
| DeKalb School of the Arts | `way/1412872982` |
| Mercedes-Benz Stadium | `way/536744534` |
| Home | **fictional by design** — never geocoded |
| Track & Field | **needs the client** — which track? |
| Church | **needs the client** — and is sensitive if it is hers |
| Old Apache Kafe | **not in OSM** under any spelling tried. The client's own "Old" is the clue: the venue has closed, so it has to be built from reference rather than map data |
| 9th location | still to come |

## It works — and the User-Agent was the whole problem

`overpass.openstreetmap.fr` answers in **~1.5 s**. The earlier wall of
429/503/504s had two causes and neither was the query:

1. **Node's `fetch` sends a bare User-Agent and Overpass instances refuse it.**
   The identical query got HTTP 200 under `curl` and **403** under `fetch`. It
   reads as "this mirror is blocking us" and is nothing of the kind. Every
   request now sends a real UA, the same courtesy Nominatim's policy asks for.
2. The other mirrors genuinely are saturated. `.fr` is first in the list now.

Four locations extracted, in seconds each:

| location | buildings | surveyed height | ways | km |
|---|---|---|---|---|
| Mercedes-Benz Stadium | 43 | **7** | 473 | 29.9 |
| DeKalb School of the Arts | 50 | **1** | 129 | 13.2 |
| Wade Walker Park | 54 | **0** | 71 | 11.2 |
| Stone Mountain Park | 3 | **0** | 20 | 9.1 |

Blockout triangle counts are **tiny** — 2.4k at Wade Walker, 2.0k at Stone
Mountain — against a 500k budget. Massing is not where the budget goes; facades,
props and the crowd are.

## What the previews show that the numbers do not

`python3 tools/atlanta/preview.py` draws each extract top-down. Three things
only visible by looking:

* **Height data is almost absent** — 8 surveyed heights across 150 buildings.
  Nearly every building will be an estimate, which means **the facade pass
  carries the realism**, not the massing.
* **Stone Mountain at 450 m from the park centroid is nearly empty** — the
  centroid of a 3.7 km park lands on the mountain, where little is mapped. That
  location needs a specific spot chosen (the lawn, the walk-up trail, the
  plaza), not the centre.
* **DeKalb School of the Arts has a running track**, clearly visible in the
  plan. "Track & Field" is one of the two locations still waiting on the client
  — the DSA track may well be it, which would answer the question for free.

## The three.js viewer — the real geometry, standing up

```bash
python3 -m http.server 8000
# open /tools/atlanta/viewer/index.html?loc=mbs
# drag orbit · scroll zoom · R runner eye · O overview · , . move along the route
```

`viewer/city.js` is **the first piece of the Game II renderer**, not a throwaway.
It reads the same `world.json` the Blender blockout reads — which is the whole
point of the format — and extrudes it with `MeshStandardMaterial`, a sun, a sky
and real shadows.

**It merges by material, not by object.** The blockout keeps one object per
building because facades and LODs need that; the runtime does the opposite,
because 50 buildings would be 50 draw calls before a single prop exists.

| location | draw calls | triangles | route |
|---|---|---|---|
| Mercedes-Benz Stadium | 6 | 5,739 | 759 m |
| DeKalb School of the Arts | 6 | 2,607 | 2,484 m |
| Wade Walker Park | 6 | 2,432 | 1,089 m |
| Stone Mountain Park | 6 | 1,968 | 1,967 m |

Against budgets of **150 draw calls and 500k triangles**. Massing costs
essentially nothing; the budget is there for facades, props and the crowd.

### Two things the runner camera caught that the overview hid

Both were invisible from above and obvious at eye level. **Judge surfaces and
light from the camera the game is played on.**

* **Ground and road were nearly the same luma** (0x23231f vs 0x2b2b30). From
  above, fine. At eye level, half the frame was an undifferentiated black sea.
  Asphalt now reads dark *against* a lighter ground.
* **Shadows went pure black.** A hemisphere light at 1.05 with a 2.6 sun left
  the sun's shadow with nothing filling it. Outdoors the sky *is* the fill, so
  the hemisphere now carries the intensity and the sun came down to match.

### What this preview does and does not prove

**Proves:** the pipeline runs end to end — real OSM → `world.json` → three.js
with real materials — the scale is right, and the budget has enormous headroom.

**Does not prove anything about how it will look.** This is massing. No
textures, no props, no trees, no kerbs, no crowd. It is bare because it *is*
bare, and 142 of 150 buildings carry a guessed height, so **the facade pass is
where the realism actually arrives.**

## The facade pass — and the limit it exposes

```bash
node tools/atlanta/fetch_pbr.mjs     # CC0 wall/road/roof scans from Poly Haven
python3 tools/atlanta/make_facades.py # composite them into facade trim sheets
```

Buildings are no longer flat-shaded boxes. Walls are **built by hand rather than
extruded**, because `ExtrudeGeometry` gives you the shape but not the UVs — and
the UVs are the entire point. U runs along the wall in metres, V runs up it in
metres, each divided by the trim sheet's real tile size, so **a 3.2 m storey is
a 3.2 m storey on screen** and window rows land on the floors the building
actually has.

Three styles, chosen by height: brick low-rise (≤12 m), concrete mid-rise
(≤32 m), glass tower above. Roads get CC0 asphalt, pavements concrete. Still
only **8 draw calls and 5,248 triangles** at Mercedes-Benz Stadium.

**The tile size lives in the filename** — `brick_lowrise_14.4x9.6m.jpg` — and
the viewer parses it. There is exactly one place that knows how big a sheet is,
so the UVs cannot drift out of step with the art.

**Windows are drawn, not photographed.** No signage, no brands, no recognisable
interiors — nothing to clear before shipping. (The source project carries a live
note to paint real chip brands out of a photographed facade; this avoids that
class of problem entirely.)

One scale trap worth recording: a Poly Haven wall scan covers about 2 m of real
wall. Stretched once across a 14 m facade tile, the bricks come out a metre
each and the building reads as a toy. `reps` tiles the base so a brick is a
brick.

### ⚠ What facades CANNOT fix: landmarks

Put the render next to a photograph of Mercedes-Benz Stadium and the limit is
obvious. The real building is a **faceted shell with a triangulated glass
curtain wall and an eight-petal aperture roof**. OSM gives a footprint and the
single number `height=93`. Extruded, that is a flat-topped drum.

**No texture fixes a wrong silhouette.** A landmark *is* its shape.

So the detail pass is two tracks, which is what the source project does too:

| | how | covers |
|---|---|---|
| **Generic buildings** | extrusion + procedural facade trim sheets | 42 of 43 here, and nearly everything at the other locations |
| **Hero landmarks** | modelled individually, photo-referenced, UV-projected | the stadium, the Stone Mountain carving, the school frontage, Apache |

The generic track is done and cheap. The hero track is per-building art, and
it is the only route to a building that reads as *that* building.

## Hero landmarks — `viewer/heroes.js`

A registry keyed by OSM id. `buildCity` skips any building with a hero builder
and calls the builder instead, handing it the **real footprint** — so a hero
still sits exactly on its surveyed outline and only its shape is bespoke.

Mercedes-Benz Stadium is the first: a flared skirt, a **leaning glass curtain
wall**, a faceted white shell tapering in, and an **eight-petal aperture roof**
pinwheeling to an open oculus. 16 facets, flat-shaded on purpose — the real
building is folded panels, and smooth normals would put the drum back.

Whole location: **12 draw calls, 5,294 triangles.**

### Two lighting bugs, both diagnosed rather than guessed

**Metal and glass render BLACK with no environment.** The curtain wall came out
pure black. A `MeshStandardMaterial` at metalness 0.78 is almost entirely
reflective, and with `scene.environment` unset there is nothing to reflect.
A painted sky/ground gradient through `PMREMGenerator` fixes it and lifts every
other material at the same time.

**Then it was STILL black, and neither obvious cause was it.** A headless probe
confirmed the environment was bound and the face normals pointed outward. Two
real reasons:

* **Glass is a dielectric, not a metal.** At high metalness the reflection is
  tinted by the base colour, so a dark blue base returns a dark reflection.
  Architectural glass is low-roughness with its brightness coming from Fresnel —
  low metalness, very low roughness, lifted `envMapIntensity`.
* **The lean is not decoration.** A vertical mirror reflects the horizon and the
  ground; a leaning one catches the sky. Near-vertical glass renders dark
  whatever the material says. ~11° of inward lean is what makes it read.

### The triangulated lattice

Added, and it is the single biggest step. Without it the glass is a smooth
leaning surface that could belong to any arena; the **big diagonal members are
what people actually picture**. Thin strips pushed 0.9 m proud of the glass
along each facet's own normal, so they catch the sun separately from it, with
the diagonals zigzagging per row *and* per facet so the triangles chevron
around the building instead of all leaning one way.

Cost: **one draw call and 256 triangles.** 13 and 5,550 for the whole location.

### Third pass — what actually made it read

Client, on the second pass: *"the stadium doesn't look like that at all."*
Correct. Four things were wrong, and three of them were structural rather than
matters of detail:

* **The lattice triangles were far too small.** Three rows produced a fine mesh
  like window mullions. In the photograph there are only five or six triangles
  across the entire face, each spanning nearly the full height of the glass.
  **One row, heavy members** — this is primary structure, not glazing bars.
* **The glass/shell boundary was a flat ring.** On the real building the white
  shell comes **down in points between the glass panels**, and that chevron is
  its signature line after the roof. `bandGeometry` now takes per-vertex
  heights, which is what makes a zigzag boundary possible at all.
* **It was a figure of revolution.** A uniformly scaled ring is a drum however
  it is textured. Fixed per-facet radius and rim-height profiles break the
  symmetry repeatably — no randomness, so the model is identical every load.
* **The roof was closed.** Eight triangles meeting at a point make a tent, which
  is the opposite of this building. The roof is now an **annulus with a real
  hole**, pinwheeled against the outer ring, with the bowl visible below.

Also down from 16 facets to **12**: at sixteen the panels get small enough to
read as a cylinder again.

### Fourth pass — what four reference angles changed

Client: *"look at multiple photos, multiple angles."* Right, and working from a
single photograph had produced three wrong readings that one more view
corrected immediately:

* **It is LOW AND WIDE, roughly 1:4 against its footprint.** OSM's `height=93`
  is to the **top of the highest point**, not the main mass — used as the body
  height it builds a tower. The body is now 0.74 of that, with only the peaks
  reaching 93.
* **The crown is a SAWTOOTH, not a rim.** The top alternates hard between peaks
  and valleys. A gently varying rim just reads as a wobbly drum.
* **The plan is a STAR, not a polygon.** Each white blade has a crease running
  down it, and a crease down a blade means the plan zigzags in and out. 24
  facets with a weak jitter reads as a cylinder; 24 with a strong alternation
  (±4.5%) reads as folded metal. That single change is what finally gave the
  shell its folded quality.
* The chevron also had to go **extreme** — white planes sweeping from the crown
  almost to the ground between tall glass wedges, rather than a band with a
  wobble.

The crown's sawtooth runs on a longer wavelength than the fold (a peak every
four facets), so each peak spans two folded blades, and the glass and crown
profiles are deliberately out of phase.

**15 draw calls and 5,558 triangles for the entire location.**

### Fifth pass — stop guessing, sweep the shape

Client: *"that shit doesn't look good."* Fair. Four passes of editing one
constant per render was the wrong method for a question that is **visual**, so
the stadium's shape became URL-tunable:

```
?loc=mbs&F=24&jit=0&pw=1&peak=1.12&gmax=0.78&gmin=0.42&ovh=1.10&apex=0.60
```

Variants now render **side by side against a photograph**, which settled in
three sweeps what four passes of reasoning had not:

* **THE WHITE IS A ROOF, NOT A WALL.** This was the real error, and it survived
  four passes. The white panels are a **shallow sloping roof that OVERHANGS the
  glass** and rises inward to the peaks. Built as vertical blades they read as a
  crown of spikes; built as an overhanging roof they read as the building.
  `ovh` is how far the roof's outer edge projects past the glass beneath it.
* **The star fold was wrong once the roof was right.** The ±4.5% plan jitter
  from the fourth pass existed to make a *wall* look folded. Over a sloping roof
  it reads as crumple — 0.03 and 0.05 both look damaged next to 0. Now 0.
* **The glass wall carries more height than the roof.** At 0.26–0.62 the roof
  ate the building; 0.42–0.78 is the split the photographs show.
* 24 facets with peaks every facet — a clean jagged edge rather than spikes.

**The method is the point, and it generalises:** a shape question is settled by
rendering candidates against the reference, not by reasoning about the
reference. The same sweep harness should drive every hero that follows.

### Honest state

Tall glass wall under a sloping faceted roof with a jagged overhanging edge,
big structural triangles, open aperture, low wide stance. Against three
reference angles the silhouette and the material relationship both hold. Still
absent: entry canopies and ground-level detail, the halo board, and the logo
(deliberately — see below).

**The logo is deliberately absent.** The three-pointed star is a trademark.
Depicting the building is ordinary; reproducing the mark as an asset in a
commercial game is a different question and is the client's to answer, not
something to slip in.

## Terrain, and painting the ground

Every location now carries a real elevation grid (Open-Meteo, Copernicus DEM —
free, no key, ~0.75 s a call, paced to stay inside the per-minute limit):

| location | relief |
|---|---|
| Stone Mountain Park | **240 m** |
| Wade Walker Park | 45 m |
| Mercedes-Benz Stadium | 32 m |
| DeKalb School of the Arts | 16 m |

**Ground cover is PAINTED on the terrain, not laid over it.** Laying coarse area
polygons on a hill makes them cut straight through it — Wade Walker came out as
unbroken green with every road swallowed. Painting per vertex leaves nothing to
z-fight with and nothing to drape. The terrain mesh is subdivided finer than the
elevation grid (×3) so cover boundaries stay sharp; the DEM limits height
detail, not colour detail.

Buildings sample the **minimum** ground height under their footprint and sink
1 m, so nothing gapes on its downhill side. Roads sample per vertex, because a
road laid flat across a hill floats at one end and buries itself at the other.

### Three bugs worth keeping

**A cache keyed on less than its inputs does not fail loudly.** Widening the
Overpass query to pull `bare_rock` changed nothing — every location returned its
old cached answer and the element counts looked identical. The query is part of
the cache key now (sha1, 8 chars).

**A coloured detail map eats vertex colours.** Cover is carried by vertex
colour and `map` *multiplies* it, so a tan concrete scan turned granite tan,
grass tan, everything tan. It reads exactly like "the painting is broken" when
the painting was fine. A detail map over a tinted surface must be **neutral** —
grain only. Generated in-canvas from a fixed seed, so no asset and no variation
between loads.

**The terrain was never counted.** It is the biggest mesh in every scene and was
added without touching `stats.tris`, so every triangle figure quoted before this
was short. Real numbers: **29–33k triangles, 6–15 draw calls**, against 500k and
150.

## Filling the world from open sources

**Searched before assuming, which I should have done first.** The honest answer
to "nearly indistinguishable" needed a sourcing pass, not more tuning:

| source | what it gives | licence | status |
|---|---|---|---|
| **OSM nodes** | trees, traffic signals, bollards, gates, hydrants, bus stops, flagpoles, benches, billboards | ODbL | **in use** — 139 props at the stadium alone |
| **OSM `building:part`** | multi-part building massing | ODbL | present in Atlanta; not yet consumed |
| **Open-Meteo / Copernicus DEM** | terrain | free, no key | in use |
| **Poly Haven** | PBR surfaces | CC0 | in use |
| **Wikimedia Commons** | reference photographs | CC0 only | in use, projected |
| **Sketchfab** | a downloadable **CC-Attribution** Mercedes-Benz Stadium, 4,642 faces | CC BY | **found; download needs a free account** (`84c4ef1b46bf448580932bd382afe6e1`) |

The stadium model is the answer to the landmark problem and it is **free** —
CC Attribution, credit in the game's credits and nothing more. The Sketchfab
download endpoint needs OAuth, so it is one sign-in away rather than a purchase.

### Street furniture — `viewer/props.js`

One `InstancedMesh` per type, so 96 trees cost **one draw call**. Shapes are
deliberately simple — at runner speed a tree is a trunk and a mass of leaves.
Variation is hashed from the instance index, so a street never reshuffles
between loads but never looks stamped either.

### Four bugs this pass, each found by measuring rather than guessing

**The camera was underground.** Once terrain had real elevation, a runner eye
pinned to `y=1.75` absolute sat below the hill — which renders as a black lower
half and reads as a shader fault. Eye height is relative to the ground beneath
her, always.

**Roads cut through hills.** Same lesson as the areas, learned twice: an OSM way
can run 50 m between nodes, and a ribbon built straight between two terrain
samples passes through everything in between. Anything draped on terrain is
subdivided first, finer than the terrain's own detail.

**The terrain skirt was a black wedge.** A flat plane at (min height − 2) fills
the lower frame from a low camera. Removed — the terrain mesh now simply extends
past the sampled grid, where `heightAt` already clamps, so the border joins
seamlessly with no step.

**Ribbons had no UVs at all.** A material with a `map` and no `uv` attribute
samples one corner texel for the entire surface, so every footway rendered as a
flat dark shape. Three guesses missed it; a raycast named it in one call. Roads
and pavements now carry real asphalt and real concrete.

**Also:** not every three.js primitive is indexed — `IcosahedronGeometry` is not,
and assuming an index threw at load, which looks like a data problem and is a
geometry-API one.

---

## The shareable preview — one link, phone-ready

**Live:** <https://claude.ai/artifact/Pz6DWYWGciRUXmcdo2FLu2> — all four locations,
orbit and runner-eye, no checkout and no local server.

Four things stood between the local viewer and a link, all of them measured
(`029b95f`).

**Asset base.** Paths were `'../art/...'` and `'../world/...'` in four files,
correct only when the page sits in `tools/atlanta/viewer/` with its assets one
level up. A published bundle is flat, so the same `'../'` walks off the top of
the site and 404s every texture. `viewer/base.js` derives the prefix from the
document's own directory instead, so **one `index.html` serves both layouts** —
verified identical: 24 draws / 153,377 tris at MBS from either. A build flag
would have meant two `index.html` files, and they would have drifted.

**FOV is VERTICAL, so a phone held upright is a telephoto lens.** three.js
`camera.fov` is the vertical angle and horizontal follows the aspect: at
390x844 that is aspect 0.46, so a 58 deg vertical is **29 deg horizontal**. The
runner view on a phone was a corridor of tarmac with the stadium cropped clean
out of frame, which reads as "the city is missing" and is a lens choice. Widen
vertical until horizontal stays usable, capped at 82 so the near ground does not
fisheye; landscape keeps the 58 it was framed for.

**Where the run starts is measured, not 0.12 for everything.** Sampled a 7x9 ray
grid along each route at 0.1 steps and took the point where the location's own
geometry actually fills the frame:

| location | start `t` | what fills the frame there |
|---|---|---|
| mbs | 0.55 | hero 21% (at 0.12 it was **0%** — empty road) |
| dsa | 0.30 | footways 33%, terrain 17% |
| wade | 0.30 | roads 30%, terrain 24% |
| stonemtn | 0.20 | terrain 62% — the dome |

Past ~0.4 the DSA and Stone Mountain routes leave the extract and the frame goes
**78–94% sky**. So these are also the last point that still has a world in it.

**Touch.** Pointer events already covered drag; pinch-to-zoom did not exist and a
phone has no wheel, so zoom was simply unreachable — it now comes off the second
pointer. `R`/`O`/`,`/`.` likewise had no on-screen equivalent, so the entire
runner-eye view was unreachable on the device the link is actually opened on.
`canvas` needs `touch-action:none` or a drag scrolls the page, not the camera.

### Two cascade bugs, both found by measuring instead of looking

**A media query is not more specific than the rule it overrides.** The mobile
block sat ABOVE the base rules; equal specificity, later wins, so `#pick` kept
`top:12px` AND got `bottom:66px` and stretched into 350px vertical pills. The
block must stay last in the stylesheet.

**A stack whose height depends on wrapping cannot be laid out with constants.**
Three fixed elements on hand-picked `bottom` offsets collided at 390px, and again
at 360px once the buttons wrapped to two rows. The bottom is one flex column now
(`#dock`, `display:contents` on wide). Measured pairwise overlap at 1000x600,
390x844 and 360x640: **none**, and no page scroll at any of them.

## The stadium model — blocked on exactly one credential

Searched rather than assumed. Across all of Sketchfab, **one** model matching
"mercedes benz stadium" is both downloadable and licensed:

| uid | licence | faces | author |
|---|---|---|---|
| `84c4ef1b46bf448580932bd382afe6e1` | CC Attribution | 4,642 | notmrsus |

The one titled "Game Ready Asset (FREE)" (`b3b4dbae…`) is **not** downloadable —
`isDownloadable:false`, empty licence object — so the word FREE in a title is not
a licence. Measured, not read off the page.

`GET https://api.sketchfab.com/v3/models/<uid>/download` answers **HTTP 401**;
Sketchfab's own docs require an `Authorization` header (`Token <API_TOKEN>` or an
OAuth bearer). There is no anonymous route and none was attempted. The session
reads **`SKETCHFAB_TOKEN`** from the environment; `env | grep -i sketchfab` is
empty, so this is one environment variable away, not a research problem.
