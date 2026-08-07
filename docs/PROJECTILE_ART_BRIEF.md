# Boss projectiles → AutoSprite painted pass (client-directed)

**Client, 2026-07-26:** *"The projectiles are cool but I want that shit spot-on
with the person's matter… same quality as the boss sprite."*

> ## ✅ EXECUTED — cloud session, via AutoSprite MCP-over-HTTP
> Network policy opened + Bearer key → drove the API directly. All nine pieces
> generated (`painted` style; 6 turbo best-of-4, 3 ultra), backgrounds removed
> with the semantic remover, bbox-trimmed and composed into a 9x96 atlas at
> `web/e80b77732c0e.webp` (24 KB), registered as `TEXDATA.proj`. `drawBoss` now
> draws the painted piece (pages/petals tumble, everything else flies
> velocity-oriented; thin silhouettes get a size bump) with the canvas
> primitives kept as the not-yet-loaded fallback. Verified: TEX.proj loads
> (864px), zero page errors, all 55 web refs resolve.

He's applying the project's own Working Principle #3 (DEVELOPMENT_RECORD):
**"Art quality has a medium ceiling — when the bar is the painted sprite, use the
render pipeline, not more code."** The current projectiles are canvas primitives
(the `_bbi` switch in `drawBoss`, index.html ~4562). Code-drawn shapes will never
match the painted bosses. This brief gets them regenerated properly.

## Interim fix already shipped (cloud session)
The Ink Warden page was **invisible**, not merely thin: it was drawn as a
near-black rect (`BOSS_GORE[0]='26,20,34'`) on the dark library backdrop, with
even its glow in the same near-black. Now: cream paper with dark-ink writing and
edge, torn silhouette, ~24×18, tumbling, paper-cream glow. Readable — but still
a primitive. This brief supersedes it.

## AutoSprite generation — 9 pieces

Style anchor: **match the painted boss atlas** (same painterly storybook look).
Each piece is the boss's own matter, reads as a real object at ~28px on screen.

| # | Boss | Piece | Notes |
|---|---|---|---|
| 0 | Ink Warden | **torn page** | cream/aged paper, handwriting lines, ink-wet torn edge, a drip |
| 1 | Thistle Ogre | **barbed thorn** | woody green-brown, directional (points right) |
| 2 | Blossom Revenant | **cherry petal** | pink, slight curl, translucent edge |
| 3 | Thorn Queen | **rose thorn** | deep red-on-green, sharper/eleganter than #1 |
| 4 | Lake Wraith | **water droplet** | teardrop with tail, specular highlight |
| 5 | Toadstool Warlock | **spore cluster** | purple puffball with drifting motes |
| 6 | Scarecrow King | **straw bundle** | golden stalks, loose ties, frayed ends |
| 7 | Storm Titan | **lightning shard** | jagged blue-white bolt fragment, hot core |
| 8 | The Groom | **dark ember** | black-red coal with inner fire, ash flecks |

## Sprite spec (matches the engine's atlas conventions)
- One horizontal strip, **9 cells at 96×96**, transparent, painted style.
- Author each **facing RIGHT** (the draw code rotates to the velocity angle —
  keep that; it's what makes shards streak and pages tumble).
- Centered in cell, ~70% fill; leave alpha padding.
- Key/normalize/compose via the usual pipeline → content-addressed
  `web/<sha1>.webp` → add `TEXDATA.proj` → web-ref audit.

## Wiring (replaces the primitive switch, keeps the physics)
In `drawBoss` bullets loop: keep the glow + `rotate(_ang)`; replace the `_bbi`
switch body with one `drawImage(TEX.proj, _bbi*96,0,96,96, -14,-14,28,28)`.
Keep the Ink Warden's tumble (`rotate(A*0.15)`) and the spore/ember orbit motes
if desired as cheap sweetening on top. Delete the primitives.

## Getting AutoSprite access for the CLOUD session (optional)
This session has internet (via proxy) but **no AutoSprite connection** — that
lives on the laptop. Two ways to give it to the cloud session:
1. **MCP connector** (best): claude.ai → Settings → Connectors → add the
   AutoSprite MCP server → its `create_character`/`generate_spritesheet` tools
   appear here and the cloud session can run this brief end-to-end.
2. **API key**: if AutoSprite exposes a plain HTTP API, paste the key in chat
   (never commit it) and the cloud session can call it directly.
Otherwise: run this brief from the laptop session as usual.
