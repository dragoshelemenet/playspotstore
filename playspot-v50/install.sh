#!/usr/bin/env bash
set -euo pipefail
# Upload the zip into GitHub main, then run from Codespaces repository root.
if [[ ! -d .git || ! -s index.html || ! -s ru.html || ! -s playspot-v29/generate.py || ! -s playspot-v49/slug-index.json ]]; then
  echo 'ERROR: Open the PlaySpotStore repository with V49 already installed.' >&2; exit 1
fi
if [[ "$(git branch --show-current)" != 'main' ]]; then
  echo 'ERROR: Expected main branch.' >&2; exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" || -n "$(git diff --cached --name-only)" ]]; then
  echo 'ERROR: Tracked/staged changes detected; commit or resolve them first. No reset/stash.' >&2; exit 1
fi
git pull --ff-only origin main
python3 -B playspot-v50/quality.py --root . --check
python3 -B playspot-v50/quality.py --root .
python3 -B playspot-v50/validate.py --root .
python3 -B playspot-v50/audit.py --root .
# Prior validators catch regressions in SEO, local text, category filters and URLs.
python3 -B playspot-v49/validate.py --root .
python3 -B playspot-v44/validate.py --root .
python3 -B playspot-v29/validate.py --root .
python3 -B playspot-v48/validate.py --root .
git add -A -- playspot-v50/ playspot-v29/generate.py data/ produse/ ru/produse/ categorii/ ru/categorii/
if git diff --cached --quiet; then
  echo 'V50 already installed; no further changes.'
else
  git commit -m 'V50: clean product snippets, meaningful image alt and static crawl audit'
  git push origin main
fi
echo 'SUCCESS: V50 SEO quality patch installed; see playspot-v50/AUDIT.md.'
