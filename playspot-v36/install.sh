#!/usr/bin/env bash
set -euo pipefail
# Run from PlaySpotStore Codespaces repository root after extracting the V36 zip.
if [[ ! -d .git || ! -f index.html || ! -f ru.html || ! -f playspot-v29/generate.py ]]; then
  echo 'ERROR: Run from the PlaySpotStore Codespaces repository root with V29+ installed.' >&2
  exit 1
fi
# Protect against overwriting uncommitted local changes to existing tracked files.
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'ERROR: You have uncommitted tracked edits. Commit or stash them first.' >&2
  exit 1
fi
git pull --ff-only origin main
cp -f playspot-v36/playspot-v36.css playspot-v36.css
cp -f playspot-v36/playspot-v36.js playspot-v36.js
python3 -B playspot-v36/apply.py --root . --patch-generator
python3 -B playspot-v36/validate.py --root .
python3 -B playspot-v29/validate.py --root .
# Stage only our own CSS/JS, modified generator and category pages, and the installer.
git add -A -- playspot-v36/README.txt playspot-v36/install.sh playspot-v36/apply.py playspot-v36/validate.py playspot-v36/playspot-v36.css playspot-v36/playspot-v36.js playspot-v36.css playspot-v36.js playspot-v29/generate.py categorii/ ru/categorii/
if git diff --cached --quiet; then
  echo 'V36 already installed; nothing new to commit.'
else
  git commit -m 'V36: integrated RO RU category search and price filters'
  git push origin main
fi
echo 'SUCCESS: V36 installed. Visit /categorii/ps5.html or /ru/categorii/ps5.html after Pages deploy.'
