#!/usr/bin/env bash
set -euo pipefail
# Unzip PlaySpotStore V39 at the repository root, then run this installer.
if [[ ! -d .git || ! -f index.html || ! -f ru.html || ! -f playspot-v29/generate.py ]]; then
  echo 'ERROR: Run this from the PlaySpotStore repository root in Codespaces.' >&2
  exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'ERROR: Tracked files have uncommitted changes; commit or stash them first.' >&2
  exit 1
fi
git pull --ff-only origin main
for file in playspot-v34.css playspot-v35.css playspot-v38.css playspot-v38/patch.py; do
  if [[ ! -s "$file" ]]; then
    echo "ERROR: $file missing. Install V38 (which includes V34/V35) first." >&2
    exit 1
  fi
done
cp -f playspot-v39/playspot-v39.css playspot-v39.css
cp -f playspot-v39/playspot-v39.js playspot-v39.js
python3 -B playspot-v39/patch.py --root . --patch-generator
python3 -B playspot-v39/validate.py --root .
# Don't include unrelated files in the commit.
git add -- index.html ru.html playspot-v39.css playspot-v39.js playspot-v29/generate.py playspot-v39/
if git diff --cached --quiet; then
  echo 'V39 already installed; nothing to commit.'
else
  git commit -m 'V39: 10 percent more floating and animated category navigation'
  git push origin main
fi
echo 'SUCCESS: V39 installed. Hard refresh after GitHub Pages deploys.'
