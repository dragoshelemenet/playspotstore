#!/usr/bin/env bash
set -euo pipefail
# After extracting playspotstore-v38-category-float.zip into the repo root,
# run: git pull --ff-only origin main && bash playspot-v38/install.sh
if [[ ! -d .git || ! -f index.html || ! -f ru.html ]]; then
  echo 'ERROR: Run from the playspotstore repository root in Codespaces.' >&2
  exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'ERROR: You have uncommitted changes. Commit or stash them first.' >&2
  exit 1
fi
git pull --ff-only origin main
if ! grep -q 'playspot-v35.css' index.html || ! grep -q 'playspot-v35.css' ru.html; then
  echo 'ERROR: Install V35 first. V38 only animates category images.' >&2
  exit 1
fi
cp -f playspot-v38/playspot-v38.css playspot-v38.css
python3 -B playspot-v38/patch.py --root .
python3 -B playspot-v38/validate.py --root .
git add -A -- index.html ru.html playspot-v38.css playspot-v38/
if git diff --cached --quiet; then
  echo 'V38 already installed; no new commit required.'
else
  git commit -m 'V38: subtle floating animation on homepage category artwork'
  git push origin main
fi
echo 'SUCCESS: V38 category image floating enabled. Hard refresh when GitHub Pages updates.'
