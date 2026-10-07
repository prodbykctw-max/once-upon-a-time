# Presentation set — Jandé: Once Upon A Time, Game II (Atlanta)

For showing Jandé and Frédéric. **Everything here is generated** — the scripts
in `tools/atlanta/present/` are the source of truth.

## What's in it

**18 stills** (`stills/`, 1600×900) — three per location:
`_1_establishing` (close drone), `_2_street`, `_3_runner` (what the game is
actually played at).

**12 videos** (`video/`, 960×540 H.264) — two per location:
`_play` is 12 s of the real game, stepping the actual run loop one frame at a
time, so it is the real route, the real obstacles and the real speed with Jandé
in frame. `_flyover` is a 15 s descent from inside the city down to rooftop
height.

| location | OSM | level |
|---|---|---|
| Mercedes-Benz Stadium | `way/536744534` | 346 m / 72 s |
| Old Apache Kafe | `way/144417817` (Third St NW) | 306 m / 64 s, 3 corners |
| DeKalb School of the Arts | `way/1412872982` | 362 m / 75 s, 3 corners |
| Track & Field | `way/1560248370` (Napoleon B. Cobb Stadium) | 362 m / 75 s, 3 corners |
| Wade Walker Park | `way/34775500` | 432 m / 90 s |
| Stone Mountain Park | `relation/1447405` | 432 m / 90 s |

## Regenerating

```bash
python3 -m http.server 8000                        # from the repo root
node tools/atlanta/present/stills.cjs              # ~3 min
node tools/atlanta/present/render.cjs mbs apache   # one worker, any locations
```

`video/` is **gitignored** — ~45 MB a set, and stale the moment a route or the
world changes. The stills are committed because they are small and worth
diffing.

Run three workers in parallel, not six. Measured on this container: one process
is 4034 ms/frame, three in parallel are 7687 ms/frame each — **1.57× total, not
3×**, because the software rasteriser already spreads one render across all four
cores. Both scripts skip anything already encoded, which matters: this set took
three attempts, twice interrupted by a container restart.

## What this is, honestly

A **blockout with a lighting and ground pass** — not finished art. Buildings are
OSM massing with three facade trim sheets between them; most carry none. What is
real: the street network, the building footprints and surveyed heights, the
terrain (Copernicus DEM), the land use, and the crowds and traffic driving the
actual road graph.

Still to build: per-building facades, ambient occlusion, road markings, and
density where OSM has gaps.
