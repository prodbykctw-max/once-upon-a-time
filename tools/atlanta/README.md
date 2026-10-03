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
