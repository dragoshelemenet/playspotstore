#!/usr/bin/env bash
set -euo pipefail
# Upload ZIP to GitHub, git pull in Codespaces, unzip, then run this installer.
if [[ ! -d .git || ! -f index.html || ! -f ru.html || ! -f playspot-v44/patch.py ]]; then
  echo 'ERROR: Open PlaySpotStore main repository with V44 installed.' >&2; exit 1
fi
if [[ "$(git branch --show-current)" != 'main' ]]; then
  echo 'ERROR: Expected main branch; no changes made.' >&2; exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'ERROR: Tracked local changes detected. Resolve them before installing; no reset/stash performed.' >&2; exit 1
fi
# Safe repeat of the user's explicit Codespaces git pull.
git pull --ff-only origin main
for item in playspot-v29/generate.py playspot-v29/validate.py playspot-v44/validate.py playspot-v42/validate.py playspot-v44.css sitemap.xml sitemap.html ru/sitemap.html; do
  [[ -s "$item" ]] || { echo "ERROR: Baseline V44 missing $item" >&2; exit 1; }
done
# Both plans are dry-run, with strict expected HTML/generator anchors.
python3 -B playspot-v45/compat.py --root . --check
python3 -B playspot-v45/migrate.py --root . --check
python3 -B playspot-v45/compat.py --root .
python3 -B playspot-v45/migrate.py --root .
python3 -B playspot-v45/validate.py --root .
python3 -B playspot-v44/validate.py --root .
python3 -B playspot-v29/validate.py --root .
python3 -B playspot-v45/stage.py --root .
if git diff --cached --quiet; then
  echo 'V45 already installed; no changes to commit.'
else
  git commit -m 'V45: geo-friendly RO/RU catalog URLs with safe redirects and localized product copy'
  git push origin main
fi
echo 'SUCCESS: V45 localized URLs, product copy and sitemap installed.'
