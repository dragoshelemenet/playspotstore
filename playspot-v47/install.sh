#!/usr/bin/env bash
set -euo pipefail
# Upload ZIP to GitHub main, git pull in Codespaces, unzip ZIP, run this script.
# V47 restores original product/category URLs without redirects.
if [[ ! -d .git || ! -f index.html || ! -s playspot-v45/url-map.json || ! -s playspot-v29/generate.py ]]; then
  echo 'ERROR: Open PlaySpotStore main repository with V45 installed.' >&2; exit 1
fi
if [[ "$(git branch --show-current)" != 'main' ]]; then
  echo 'ERROR: Expected branch main.' >&2; exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'ERROR: Tracked changes found. Do not use git reset; resolve these first.' >&2; exit 1
fi
git pull --ff-only origin main
python3 -B playspot-v47/restore.py --root . --check
python3 -B playspot-v47/restore.py --root .
python3 -B playspot-v47/validate.py --root .
python3 -B playspot-v44/validate.py --root .
python3 -B playspot-v29/validate.py --root .
# Only version-owned and catalog paths; never stage uploaded ZIPs or unrelated work.
git add -A -- playspot-v47/ playspot-v29/generate.py playspot-v44/patch.py playspot-v44/validate.py playspot-v42/validate.py data/ index.html ru.html \
  jocuri-video-chisinau-moldova.html ru/videoigry-kishinev-moldova.html \
  sitemap.xml sitemap.html ru/sitemap.html \
  produse/ ru/produse/ categorii/ ru/categorii/
if git diff --cached --quiet; then
  echo 'V47 already installed; no new changes.'
else
  git commit -m 'V47: restore clean product/category URLs without redirects'
  git push origin main
fi
echo 'SUCCESS: V47 original canonical URLs restored without redirects.'
