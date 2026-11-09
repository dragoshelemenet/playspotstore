#!/usr/bin/env bash
set -euo pipefail
# Run from /workspaces/playspotstore, after unzipping the V34 package.
if ! test -d .git || ! test -f index.html || ! test -f ru.html; then
  echo 'ERROR: Run this installer from the PlaySpotStore Git repository root.' >&2
  exit 1
fi
git pull --ff-only origin main
mkdir -p media
for file in hero-subject-v34.webp hero-sparks-v34.webp hero-symbols-v34.webp; do
  if ! test -s "playspot-v34/media/$file"; then
    echo "Missing bundled image: playspot-v34/media/$file" >&2
    exit 1
  fi
  cp -f "playspot-v34/media/$file" "media/$file"
done
cp -f playspot-v34/playspot-v34.css playspot-v34.css
python3 playspot-v34/patch.py --root .
git add -- index.html ru.html playspot-v34.css playspot-v34/ media/hero-subject-v34.webp media/hero-sparks-v34.webp media/hero-symbols-v34.webp
if git diff --cached --quiet; then
  echo 'V34 is already up to date; no commit required.'
else
  git commit -m 'V34: animated layered high-quality homepage hero (RO + RU)'
  git push origin main
fi
echo 'SUCCESS: three-layer animated hero published. Hard refresh your homepage after Pages deploys.'
