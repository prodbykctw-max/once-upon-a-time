# AUTOSPRITE PRODUCTION BRIEF — Whimsical Princess Environment Pack
Execute in the session with autosprite.io access. Goal: replace the pixel
mood-board kit (`walls_whimsy.png` etc.) with AutoSprite-generated painterly
versions of the SAME 9 rooms. The pixel kit is the approved color/mood
anchor — match its palette per room, exceed its detail.

## Global style string (append to every prompt)
"whimsical fairytale game background art, soft painterly style, bright
pastel palette, warm sunshine lighting, magical sparkles, clean silhouettes,
no text, no watermark, no characters, game asset"

## A. WALL/BACKDROP TILES (9) — one per room
Output per tile: landscape or square, min 512px tall; will be cropped/scaled
to atlas cells 144x192 (portrait crop from center-interest area).
Opaque backgrounds (these ARE the background).

0 SUNLIT LIBRARY: "cozy castle library wall at morning, honey-gold wooden
  bookshelves with pastel storybooks, tall arched window with sunbeams and
  floating dust, butterflies"
1 ROSE GARDEN: "royal palace rose garden, manicured green hedge wall full of
  pink roses, white marble balustrade, blue sky with puffy clouds and doves"
2 BLOSSOM PROMENADE: "cherry blossom trees in full bloom over a red lacquered
  garden bridge railing, pink petals drifting, soft blue sky"
3 CRYSTAL BALLROOM: "princess ballroom wall, blush pink and lavender panels,
  tall gilded mirrors, crystal chandelier with glowing candles, gold trim"
4 FOUNTAIN PLAZA: "sunlit palace courtyard, tiered white marble fountain with
  sparkling water arcs and a faint rainbow in the mist, classical statue"
5 SWAN LAKE TERRACE: "palace terrace overlooking a glittering lake, two white
  swans, weeping willow strands, marble balustrade, golden afternoon light"
6 STARLIGHT CONSERVATORY: "glass greenhouse at dusk, indigo sky with stars
  through the panes, hanging luminous pink flowers, drifting fireflies"
7 GALLERY OF DREAMS: "dreamy palace gallery wall in pale lilac, gilt-framed
  paintings of castles and clouds, golden sun medallion, floating sparkles"
8 SUNSET STAGE: "outdoor concert stage at golden-hour sunset, lighting truss
  with colorful beams, falling confetti, silhouetted crowd holding up glowing
  phone lights, warm pink-orange sky" (THE FINALE — spend extra iterations)

## B. FLOOR TILES (9) — square, tileable if possible, 256px+
0 honey parquet · 1 garden flagstones w/ moss joints · 2 pink-petal-strewn
boards · 3 polished ballroom marble w/ gold inlay · 4 sunlit plaza cobble ·
5 pale terrace stone w/ water sheen · 6 glass/ivory tile soft glow ·
7 lavender dream carpet · 8 warm stage boards
Prompt pattern: "seamless game floor texture tile, top-down, {desc}" + global.

## C. DECOR PROPS (9) — TRANSPARENT background, portrait, min 256px tall
0 reading lectern with open storybook and candle · 1 rose topiary in gold
planter · 2 paper lantern on red post · 3 gold candelabra with lit candles ·
4 small marble cherub fountain · 5 potted luminous flower · 6 white swan
statue · 7 gilt easel with dream painting · 8 stage spotlight on tripod
Prompt: "single {item}, fairytale prop, isolated on transparent background,
game asset sprite" + global. Run remove_asset_background if edges are dirty.

## D. AMBIENT SPRITES — TRANSPARENT, small
fairy (2 wing poses, glowing) · songbird (2 wing poses) · sparkle ·
falling petal · butterfly. Tiny, readable at 24px.

## Processing spec (Pillow, after download)
1. Walls: center-crop to 3:4, resize to 144x192 (LANCZOS — these are
   painterly now, NOT nearest), assemble 9-cell horizontal atlas 1296x192.
2. Floors: square-crop, resize 96x96, atlas 864x96.
3. Decor: trim transparent bounds, fit into 144x240 with bottom-aligned
   contact point, atlas 1296x240.
4. Ambient: fit 16px grid cells scaled x4 like current ambient_whimsy.png.
5. QUANTIZE atlases (PIL convert P, 128-256 colors) before base64 — keeps
   index.html size sane. Target: full pack < 400KB base64.
6. Save finals into assets_whimsy/ as walls_as.png / floors_as.png /
   decor_as.png / ambient_as.png + a preview contact sheet, COMMIT to the
   dev branch, show the user the preview BEFORE embedding into index.html.

## QA gates (from the design principles — binding)
- Readability: obstacles/chaser must pop against every backdrop. Backdrops
  stay soft/low-contrast in the play corridor's center band; detail lives
  at the edges. If a generation is too busy, regenerate with "soft focus
  background, muted center".
- The chaser stays DARK. Do not brighten The Groom's Shadow.
- Palette continuity: sample each room's dominant hues from
  whimsy_preview.png and steer generations toward them (STAGES pc/ac update
  comes from these).
- No text/watermarks/characters in any environment tile.
