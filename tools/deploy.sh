#!/usr/bin/env bash
# Safe deploy for GitHub Pages.
#
# Publishes ONLY the game to gh-pages: index.html + web/ (externalized assets) +
# icons + manifest + .nojekyll. It rebuilds gh-pages as a fresh ORPHAN each time,
# so the deploy branch can NEVER accumulate history or stray files.
#
# WHY THIS EXISTS: a previous deploy used `git add -A` on gh-pages, which staged
# the whole working tree — including assets/ (Jandé's real reference photos and
# 3D-likeness) — onto the PUBLIC deploy branch, and left them in history. That
# has been purged. Do NOT reintroduce `git add -A` for deploys. Ever.
#
# Usage:  bash tools/deploy.sh          (run from repo root, on your dev branch)
set -euo pipefail

DEV="$(git rev-parse --abbrev-ref HEAD)"
if [ "$DEV" = "gh-pages" ] || [ "$DEV" = "HEAD" ]; then
  echo "Refusing to deploy from '$DEV'. Switch to your dev branch first."; exit 1
fi

# commit index.html/web/ on dev first if you have staged changes — this script
# only PUBLISHES; it does not commit your source branch for you.
# GLYPH GATE (2026-07-26): the no-stock-glyphs directive regressed twice because
# nothing enforced it. Refuse to deploy a build that ships symbol/emoji chars.
python3 tools/glyph_gate.py || { echo "Deploy blocked by glyph gate."; exit 1; }

# FRÉDÉRIC EDITION: a showcase build published alongside the game at /fred/.
# GENERATED from index.html every deploy, so it can never drift from what ships
# to everyone. The public index.html carries none of it — that was the point.
python3 tools/build_fred.py || { echo "Deploy blocked: fred build failed."; exit 1; }

touch .nojekyll

git checkout --orphan _deploy_tmp
git reset -q
git add index.html web .nojekyll apple-touch-icon.png icon-192.png icon-512.png manifest.webmanifest
# DISCOVERABILITY (2026-10-06): SEO/AEO files must be named EXPLICITLY here or
# they simply never reach gh-pages — this script stages a fixed list, never -A.
# Adding one of these to the repo root without adding it to this line ships
# nothing. See docs/SEO_AEO.md.
git add robots.txt sitemap.xml llms.txt social-card.jpg
git add -f fred/index.html          # generated, and .gitignored on the dev branch
git reset -q -- web/_manifest.txt 2>/dev/null || true   # debug file, not served

# GAME I PREVIEW (2026-11-16): /overhaul/ is published from claude/overhaul-bible-2.5 ON TOP of
# gh-pages, so this orphan rebuild used to delete it. The 11-15 22:20 UTC deploy did exactly that:
# the preview and 38 preview-only images went 404 and the client's link broke. Carry the live
# preview over unchanged, with every web/ file it references, and clean the copies up afterwards.
CARRIED=()
git fetch -q origin +refs/heads/gh-pages:refs/remotes/origin/gh-pages 2>/dev/null || true
if git cat-file -e origin/gh-pages:overhaul/index.html 2>/dev/null; then
  if [ ! -e overhaul/index.html ]; then
    mkdir -p overhaul
    git show origin/gh-pages:overhaul/index.html > overhaul/index.html
    CARRIED+=(overhaul/index.html)
  fi
  for f in $(grep -oE 'web/[0-9a-f]+\.[a-z0-9]+' overhaul/index.html | sort -u); do
    if [ ! -e "$f" ]; then
      git show "origin/gh-pages:$f" > "$f" || { echo "ABORT: preview asset $f missing on gh-pages"; git checkout -f "$DEV"; git branch -D _deploy_tmp; exit 1; }
      CARRIED+=("$f")
    fi
  done
  git add -f overhaul/index.html web
  echo "Carried the Game I preview over (/overhaul/ + ${#CARRIED[@]} files)."
fi

# hard guard: abort if anything sensitive slipped into the staging set
if git diff --cached --name-only | grep -iqE 'jande|charref|face_crop|\.blend|\.zip|character_ref|^image-|wrangler|^assets/'; then
  echo "ABORT: sensitive file staged for deploy:"; git diff --cached --name-only | grep -iE 'jande|charref|face_crop|\.blend|\.zip|character_ref|^image-|wrangler|^assets/'
  git checkout -f "$DEV"; git branch -D _deploy_tmp; exit 1
fi

git commit -q -m "Deploy: game assets only"
git push -f -q origin _deploy_tmp:gh-pages
git checkout -f "$DEV"
git branch -D _deploy_tmp
for f in "${CARRIED[@]}"; do rm -f "$f"; done; rmdir overhaul 2>/dev/null || true
git fetch -q origin
git branch -f gh-pages origin/gh-pages 2>/dev/null || true
echo "Deployed to gh-pages ($(git ls-tree -r --name-only origin/gh-pages | wc -l) files, game only)."
