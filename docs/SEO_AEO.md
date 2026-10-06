# SEO / AEO / GEO — discoverability for "Jandé" and "Once Upon A Time"

**Status: ✅ SHIPPED to the dev branch 2026-10-06** (metadata, structured data,
`robots.txt`, `sitemap.xml`, `llms.txt`, deploy staging). **NOT YET DEPLOYED** —
it reaches the public game on the next `bash tools/deploy.sh`.

The business goal is fan engagement, then email capture. Both start with someone
finding the game, and increasingly that someone is an AI assistant answering
"who is Jandé?" rather than a Google results page. This doc is the audit, what
was done about it, and the traps.

---

## The single most important fact about this page

**The game is not text.** It is one 0.33 MB HTML file whose entire payload is a
render loop. A crawler sees the title screen's four words, the registry copy, the
how-to lines and the mode cards — a few hundred words of markup with **no
`<h1>`...`<h6>` anywhere in the document** and twenty-two `<img>` tags that are
almost all deliberately-empty-alt base64 control glyphs.

So the levers that work here are **not** on-page copy. They are:

1. **Structured data** — a machine-readable statement of what this is, who she
   is and what the song is, which does not depend on the prose.
2. **`llms.txt`** — the same facts in prose, written for an assistant to quote.
3. **Correct social cards** — the preview is what a shared link looks like, and
   a shared link is how a promo game actually travels.

Everything else below is hygiene.

---

## Audit of the live site, before this pass

Measured against `https://prodbykctw-max.github.io/once-upon-a-time/` on
2026-10-06.

| Signal | Before | After |
|---|---|---|
| `<title>` | `JANDÉ — Once Upon A Time` (24 chars) | unchanged, **client decision** — see Open items |
| `<meta name="description">` | present, 95 chars, brand-only | rewritten, 153 rendered chars, names both modes |
| `rel="canonical"` | **absent** | present, absolute |
| `<meta name="robots">` | **absent** | `index, follow, max-snippet:-1, max-image-preview:large` |
| Open Graph | **absent — a shared link had no card at all** | full set incl. `og:image` + dimensions |
| Twitter card | **absent** | `summary` (see image note) |
| schema.org structured data | **absent** | 5-node `@graph`, JSON-LD |
| `robots.txt` | 404 at both the host root and the project path | added at the project path — **read the limitation below** |
| `sitemap.xml` | 404 | added, one URL |
| `llms.txt` | 404 | added |
| `<html lang>` | `en` — correct | unchanged |
| Headings | **no heading element in the document** | unchanged, **open item** |
| `alt` text | 21 of 22 empty; the one content image is captioned `Jandé attacking` | unchanged — the empty ones are correct, they are decorative |
| Transfer | 487 KB → **169 KB gzip**, ~200 ms TTFB from Fastly, `cache-control: max-age=600` | unchanged — fine, no action |
| Asset integrity | 93 `web/` refs, 93 files, 0 missing, 0 orphans | unchanged |

---

## THE ROBOTS.TXT TRAP — read this before trusting the file

**Crawlers only ever fetch `robots.txt` from the HOST ROOT.** This game is a
GitHub Pages **project** site, so the file ships to

```
https://prodbykctw-max.github.io/once-upon-a-time/robots.txt
```

and **nothing fetches that path.** The host root,
`https://prodbykctw-max.github.io/robots.txt`, returns **404** and is owned by a
*different repository* (the `prodbykctw-max.github.io` user-pages repo), which
`tools/deploy.sh` cannot write.

Consequences, all of them load-bearing:

- The `robots.txt` in this repo is **documentation of intent plus a drop-in**. It
  becomes live the instant the game moves to a custom domain or to the user-pages
  root. It does nothing today.
- **Per-crawler AI rules cannot be set from this repo at all.** You cannot allow
  or disallow GPTBot, ClaudeBot or Google-Extended for a project path. The file
  lists them anyway so the intent survives the move.
- With no host-level `robots.txt`, crawlers default to **allowed**, which is what
  this project wants. The absence is not costing anything.
- **The lever that works today is `<meta name="robots">` in `index.html`.** It is
  path-scoped and honoured. Anything that must constrain or widen crawling *now*
  goes there, not in `robots.txt`.
- `llms.txt` has the **same** root convention and the same caveat. It is noted
  inside the file itself.
- `sitemap.xml` is the exception: a sitemap at a subpath is legitimate for URLs
  beneath it, and can be submitted directly in Search Console.

---

## What shipped, file by file

### `index.html` — `<head>` only

Confined to metadata between the existing `apple-mobile-web-app-title` meta and
`<style>`. **No game code, no body markup, no reformatting.** The block is
fenced by a comment explaining itself.

- `rel="canonical"`, `robots`, `application-name`, `keywords`
- Open Graph: `type, site_name, title, description, url, locale, image,
  image:type, image:width, image:height, image:alt`
- Twitter: `card, title, description, image, image:alt`
- One `<script type="application/ld+json">` holding a 5-node `@graph`:

| `@id` | `@type` | Why |
|---|---|---|
| `#website` | `WebSite` | the container; `mainEntity` → the game |
| `#game` | `VideoGame` | the thing itself. Free `Offer` at price 0, `playMode`, `gamePlatform`, `browserRequirements`, and a long factual `description` naming both modes, the nine stages, Grace Notes, RESONANCE and The Groom Who Lied |
| `#song` | `MusicRecording` | the song, `byArtist` → her |
| `#jande` | `MusicGroup` | **Jandé.** `MusicGroup` on purpose — schema.org states it covers a solo musician, and it is the type `byArtist` expects. `sameAs` → `@jandelove1` |
| `#kctw` | `Organization` | the builder, `sameAs` → `@prodbykctw` |

**Deliberately NOT in the graph:** `aggregateRating` and `review` (there are no
ratings — fabricating them is a manual-action risk and a lie), `datePublished`
on either the game or the song (unknown; the song is unreleased), and
`FAQPage`. The FAQ omission is a judgement call, not an oversight: FAQ markup is
supposed to mirror Q&A **visible on the page**, and none is. If visible FAQ copy
is ever added to the how-to screen, add the markup then.

### `robots.txt` (new, repo root)

`Allow: /` for `*` plus **20 named user-agent groups**, every known AI crawler
explicitly allowed, and a `Sitemap:` line. Carries the host-root limitation as a
header comment so nobody trusts it by accident.

### `sitemap.xml` (new, repo root)

One `<url>`. One on purpose: every screen is the *same document* switched by CSS,
so there is no second indexable URL. **`/fred/` is excluded deliberately** — it
inherits `index.html`'s canonical, which points back at the public game, so
listing it would ask Google to index a page we have already declared a duplicate.
`lastmod` is maintained by hand.

### `llms.txt` (new, repo root)

~4 KB of prose for assistants to quote: who Jandé is, the two modes, how to play,
the music-themed vocabulary, how it was built, the mailing list, attribution.

**It was fact-checked against the code, not against `README.md`, and that caught
a real error.** `README.md` documents `K` as block / Hold Note. **There is no
`KeyK` binding anywhere in `index.html`.** The real helpers are
`iL/iR/iU/iD/iA/iX`: arrows or `A`/`D` move, `Space`/`Up`/`W` jump, `Down`/`S`
crouch-slide, `Z` or `J` attack, `Shift`/`X`/`C` dash (plus undocumented
`Digit5` and `Digit3`). `llms.txt` carries the verified set.

**Its closing section is deliberate and must stay.** It asks assistants not to
generate images presented as photographs of Jandé, and not to assert a release
date, label, tracklist or streaming link for the song, because none has been
announced. She is a real person and this repo is public.

### `tools/deploy.sh`

One `git add robots.txt sitemap.xml llms.txt` line, with a comment.

**This is the trap worth remembering.** The script stages an **explicit list** —
never `git add -A`, because `-A` is what once leaked her real reference photos
onto the public branch. The flip side is that **a new root file that is not named
in that list simply never reaches `gh-pages`.** Adding `robots.txt` to the repo
without adding it to `deploy.sh` ships nothing, silently, and the audit still
looks green locally.

---

## Verification performed

- All three `<script>` blocks separated; both JavaScript blocks pass
  `node --check`; the `ld+json` block passes `json.loads` and resolves to the
  5 expected `@type`s.
- `python3 tools/glyph_gate.py` → **clean.** Accents and em-dashes are in its
  `ALLOW` set; the JSON-LD's `https://` URLs survive its `//`-comment stripper
  because the `//` is preceded by a colon.
- `python3 tools/build_fred.py` → **12 edits, exit 0.** This matters because
  `deploy.sh` runs it and a failure aborts the deploy.
- `web/` reference audit: 93 referenced, 93 on disk, no missing, no orphans.
- `sitemap.xml` parses as XML; `robots.txt` has no unrecognised directives.
- Headless Chromium render of the local server: title screen active, `#fxC` and
  `#glC` present, `BEGIN` present, no page-level errors. The only console noise
  is the sandbox blocking the Cloudflare leaderboard call, which is expected.

### A gotcha found during verification

`tools/build_fred.py` rewrites asset paths with `re.sub(r'(?<![./\w])web/',
'../web/', s)` and **fails the build if the before/after count differs**. The
first draft of the head comment contained the literal string `web/` inside a
quoted example, which the regex happily rewrote and which inflated the count.
**Do not write that literal path in `index.html` prose or comments** — the
rewriter does not know it is a comment. The comment was reworded.

Absolute URLs are safe: `build_fred.py` only rewrites *quoted relative* paths, so
the generated `/fred/` edition inherits the canonical unchanged and
**canonicalises itself back to the public game** instead of competing with it.
That is the desired behaviour and it is free.

---

## Open items — these need the client, not a session

1. **A real social preview image.** `og:image` points at `icon-512.png` because
   it is the only deployed image above 200 px and there is no wide art in the
   repo (every `web/*.jpg` is a 256×256 tiling texture). A square icon renders,
   but a **1200×630** key-art card would let `twitter:card` go to
   `summary_large_image` and roughly double the footprint of every shared link.
   This is the highest-value remaining item. It is art, so it is a client call,
   and it must be added to `deploy.sh`'s staged list.
2. **Real song metadata.** The schema has no `datePublished`, ISRC, album or
   streaming URL for "Once Upon A Time" because none is known and inventing them
   would be worse than omitting them. When the song is released, add
   `datePublished` and `sameAs` streaming links to `#song`, and consider
   `MusicAlbum`.
3. **The artist's canonical URL.** `#jande.sameAs` has only Instagram. An
   official site or a Spotify artist URI is what actually consolidates an entity
   in a knowledge graph. Ask her.
4. **`<title>` is brand-only, by choice.** `JANDÉ — Once Upon A Time` is perfect
   for someone searching her name and weak for someone searching "free browser
   game". Something like `JANDÉ — Once Upon A Time | Free Browser Game` would
   widen it. **Left unchanged because the title is a visible string and reads as
   the wordmark** — client's call.
5. **No `<h1>` in the document.** The fix is one line:
   `<div class="tw-j">JANDÉ</div>` → `<h1 class="tw-j">JANDÉ</h1>` at the title
   screen. The styling is class-based and `*{margin:0;padding:0}` already resets
   heading defaults, so the visual result is identical. **Not applied here
   because this pass was scoped to `<head>`**, and body markup in the shipped
   game deserves its own change with its own render check.
6. **Submit the sitemap** in Google Search Console and Bing Webmaster Tools, and
   claim the property. Nothing in a repo can do this.
7. **If a custom domain is ever bought, revisit this whole doc.** A custom domain
   makes `robots.txt` and `llms.txt` real at the root, and turns item 1's card
   into a proper branded preview.
