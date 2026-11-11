#!/usr/bin/env bash
set -euo pipefail
# Upload V46 ZIP to GitHub main, pull in Codespaces, unzip, run this installer.
if [[ ! -d .git || ! -f index.html || ! -f playspot-v45/url-map.json || ! -f playspot-v45/validate.py ]]; then
  echo 'ERROR: Run from PlaySpotStore repository root with V45 installed.' >&2; exit 1
fi
if [[ "$(git branch --show-current)" != 'main' ]]; then
  echo 'ERROR: Expected main branch. No changes made.' >&2; exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'ERROR: Tracked files have local changes. Commit or resolve them first; no reset/stash performed.' >&2; exit 1
fi
git pull --ff-only origin main
python3 -B playspot-v46/mix.py --root . --check
python3 -B playspot-v46/mix.py --root .
python3 -B playspot-v46/validate.py --root .
python3 -B playspot-v45/validate.py --root .
python3 -B playspot-v44/validate.py --root .
python3 -B playspot-v29/validate.py --root .
# Stage owned files only; never include a ZIP uploaded to GitHub accidentally.
python3 -B playspot-v46/stage.py --root .
if git diff --cached --quiet; then
  echo 'V46 already installed. No new changes to commit.'
else
  git commit -m 'V46: natural deterministic product copy and internal link variation'
  git push origin main
fi
echo 'SUCCESS: V46 natural SEO variations installed; canonical URLs remain unchanged.'
