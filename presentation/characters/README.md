# The RPG cast — Jandé: Once Upon A Time

For showing Jandé and Frédéric. **Everything here is generated from the shipped
atlases in `web/`** — no character on these sheets was redrawn, and no number
beside one was written from memory. Each figure is the sprite the game loads at
runtime; each constant was read out of `index.html` or measured off the pixels.

## What's in it

| file | what it is |
|---|---|
| `JANDE-RPG-CAST.pdf` | 8 pages, A4 — the whole cast, for sending |
| `01-jande-hero.png` | Jandé's 13 animation slots, every frame |
| `02-foe-roster.png` | the 6 foe types, 6 frames each, with behaviour and bleed |
| `03-the-nine-bosses.png` | the 9 bosses, stage / HP / aura |
| `04-boss-frames.png` | all 81 boss cells — 4 idle + 5 defeat × 9 |
| `05-groom-defeat-fix.png` | before/after of the reversed defeat sequence |

## The cast, in full

**Jandé** — 13 sheets. Ten side-view (`idle run jump attack dash block dance
refrain belt downstrike`, 75 frames, cells 154px tall) and three back-view for
Royal Runner (`bkrun bkjump bkslide`, 25 frames each at 256×256). The side art
faces **right**; left is a mirror.

**Six foes** — one atlas, `web/e3bc36ab1807.webp`, 4896×152, cells 136×152,
six frames per type. They are introduced on a schedule, which is the real
information: goblin from stage 1, raven 2, sprite 4, knight 5, wisp 6, wraith 8.
All six share one 52×58 collider anchored at the feet; the drawn size differs
per type so the painting reads at speed.

**Nine bosses** — one atlas, `web/78f95835ae52.webp`, 1800×2520, cells 200×280,
row = stage, 4 idle frames then 5 defeat frames. HP runs 7, 9, 11, 13, 15, 17,
19, 21 and then **28** for the Groom. Two are airborne (Blossom Revenant,
Lake Wraith) and use drift-and-shoot patterns instead of jump and slam.

**Not in the cast:** the old `spawnE` creature set — cupids, fairies, imps,
wraiths, fallen angels, sorcerers, gargoyles, bears, lions, dragons, golems.
Its only caller is `buildLevel`, which nothing calls. Verified by grep; the
source's own comment at `index.html:1294` says the same. It is dead code.

## What this found

Laying all 81 villain cells side by side showed something playing never did:
**the Groom's defeat sequence ran backwards.** Measured two ways across the
whole atlas — every other boss drives its alpha-weighted centroid down the cell
(+14.6px on the Ink Warden to +111.4px on the Storm Titan) and sheds coverage
(−1.9 to −43.3 points); row 8 alone travelled **up** (−20.7px) and **gained**
coverage (+4.9). Silhouette IoU against each villain's own standing pose agrees:
the other eight finish least like themselves, the Groom finishes most like
himself (0.505, the highest of his five). So on the climax of the whole game he
collapsed into frame and then stood back up. Fixed — `bi===8` now indexes those
five cells 8→4. Also verified in passing: all 13 hero sheets match their
declared geometry exactly, and all 36 foe cells and 81 boss cells carry real
art with no empties.

## Regenerating

The PNG sheets, each independent:

```bash
python3 -I presentation/characters/src/charsheet.py   # 01 — Jandé
python3 -I presentation/characters/src/foesheet.py    # 02 — foes
python3 -I presentation/characters/src/boss3.py       # 03 — the nine
python3 -I presentation/characters/src/bosssheet.py   # 04 — every boss frame
python3 -I presentation/characters/src/groom.py       # 05 — the defeat fix
```

They need Pillow, the game's own Storyboo face (`web/435323e92ad8.ttf`) for
headings, and Lora / GeistMono for body and data.

The PDF comes from the web version, `src/cast.html`, printed by headless
Chromium — so the page and the document never drift apart:

```bash
python3 -I presentation/characters/src/crops.py   # cut the transparent portraits
python3 -m http.server 8421 --directory presentation/characters/src
node presentation/characters/src/pdf.cjs          # writes JANDE-RPG-CAST.pdf
```

`cast.html` is also published as a shareable web page. It carries its own print
stylesheet (`@media print`), which is what gives the PDF its page breaks — edit
the page, not the PDF.
