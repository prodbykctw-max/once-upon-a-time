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
touch .nojekyll

git checkout --orphan _deploy_tmp
git reset -q
git add index.html web .nojekyll apple-touch-icon.png icon-192.png icon-512.png manifest.webmanifest
git reset -q -- web/_manifest.txt 2>/dev/null || true   # debug file, not served

# hard guard: abort if anything sensitive slipped into the staging set
if git diff --cached --name-only | grep -iqE 'jande|charref|face_crop|\.blend|\.zip|character_ref|^image-|wrangler|^assets/'; then
  echo "ABORT: sensitive file staged for deploy:"; git diff --cached --name-only | grep -iE 'jande|charref|face_crop|\.blend|\.zip|character_ref|^image-|wrangler|^assets/'
  git checkout -f "$DEV"; git branch -D _deploy_tmp; exit 1
fi

git commit -q -m "Deploy: game assets only"
git push -f -q origin _deploy_tmp:gh-pages
git checkout -f "$DEV"
git branch -D _deploy_tmp
git fetch -q origin
git branch -f gh-pages origin/gh-pages 2>/dev/null || true
echo "Deployed to gh-pages ($(git ls-tree -r --name-only origin/gh-pages | wc -l) files, game only)."
