#!/usr/bin/env bash
set -euo pipefail
if [[ ! -d .git || ! -f index.html || ! -f ru.html ]]; then
  echo 'ERROR: Run this installer from the PlaySpotStore repository root.' >&2
  exit 1
fi
git pull --ff-only origin main
for asset in media/hero-subject-v34.webp media/hero-sparks-v34.webp media/hero-symbols-v34.webp playspot-v34.css; do
  if [[ ! -s "$asset" ]]; then echo "ERROR: Missing V34 asset $asset" >&2; exit 1; fi
done
cp -f playspot-v35/playspot-v35.css playspot-v35.css
cp -f playspot-v35/playspot-v35.js playspot-v35.js
python3 playspot-v35/patch.py --root .
git add -- index.html ru.html playspot-v35.css playspot-v35.js playspot-v35/
if git diff --cached --quiet; then
  echo 'V35 is already installed; nothing to commit.'
else
  git commit -m 'V35: smooth scroll-reactive parallax for layered hero'
  git push origin main
fi
echo 'SUCCESS: V35 scroll parallax installed. Hard refresh after GitHub Pages deploys.'
