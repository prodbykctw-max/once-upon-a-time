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
