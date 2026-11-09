#!/usr/bin/env bash
set -euo pipefail
# Unzip V37 at PlaySpotStore repository root, then run this installer.
if [[ ! -d .git || ! -f index.html || ! -f ru.html || ! -f playspot-v29/generate.py ]]; then
  echo 'ERROR: Run from the PlaySpotStore Codespaces repository root.' >&2
  exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'ERROR: Uncommitted changes found. Commit/stash them before installation.' >&2
  exit 1
fi
git pull --ff-only origin main
if [[ ! -f playspot-v36/apply.py || ! -f playspot-v36.js ]]; then
  echo 'ERROR: V36 is required. Install PlaySpotStore V36 first.' >&2
  exit 1
fi
cp -f playspot-v37/playspot-v37.css playspot-v37.css
cp -f playspot-v37/playspot-v37.js playspot-v37.js
python3 -B playspot-v37/patch.py --root . --patch-generator
python3 -B playspot-v37/validate.py --root .
python3 -B playspot-v29/validate.py --root .
git add -A -- playspot-v37/ playspot-v37.css playspot-v37.js playspot-v29/generate.py categorii/ ru/categorii/
if git diff --cached --quiet; then
  echo 'V37 already installed; nothing to commit.'
else
  git commit -m 'V37: integrated hero search and collapsible category filters'
  git push origin main
fi
echo 'SUCCESS: V37 installed. Refresh category pages after GitHub Pages deploys.'
