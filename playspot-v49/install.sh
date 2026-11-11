#!/usr/bin/env bash
set -euo pipefail
# Upload ZIP into GitHub main, git pull in Codespaces, unzip, then run.
if [[ ! -d .git || ! -s index.html || ! -s ru.html || ! -s playspot-v29/generate.py || ! -s playspot-v48/cleanup.py ]]; then
  echo 'ERROR: Open the PlaySpotStore main repo root; V47/V48 required.' >&2; exit 1
fi
if [[ "$(git branch --show-current)" != main ]]; then
  echo 'ERROR: Expected Git branch main.' >&2; exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'ERROR: Local tracked changes found. Resolve them first; no git reset/stash is performed.' >&2; exit 1
fi
if [[ -n "$(git diff --cached --name-only)" ]]; then
  echo 'ERROR: Staged changes detected. No unrelated changes will be committed.' >&2; exit 1
fi
git pull --ff-only origin main
python3 -B playspot-v49/shorten.py --root . --check
python3 -B playspot-v49/shorten.py --root .
python3 -B playspot-v49/validate.py --root .
python3 -B playspot-v44/validate.py --root .
python3 -B playspot-v29/validate.py --root .
python3 -B playspot-v48/validate.py --root .
# Stage only owned files; include deletions of old product pages and new pages.
git add -A -- playspot-v49/ playspot-v29/generate.py playspot-v47/validate.py \
  index.html ru.html categorii/ ru/categorii/ produse/ ru/produse/ \
  jocuri-video-chisinau-moldova.html ru/videoigry-kishinev-moldova.html \
  sitemap.xml sitemap.html ru/sitemap.html seo/generated-paths.json
if git diff --cached --quiet; then
  echo 'V49 already installed: nothing to commit.'
else
  git commit -m 'V49: short stable product URLs without repeated catalog IDs'
  git push origin main
fi
echo 'SUCCESS: V49 short product URLs installed and validated.'
