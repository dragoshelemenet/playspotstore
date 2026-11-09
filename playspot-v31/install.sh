#!/usr/bin/env bash
set -euo pipefail
if ! test -d .git || ! test -f index.html || ! test -f playspot-v29/generate.py; then
  echo 'ERROR: Run from the PlaySpotStore repository root (V29/V30 required).' >&2
  exit 1
fi
git pull --ff-only origin main
python3 playspot-v31/patch.py --root .
python3 playspot-v29/validate.py --root .
git add sitemap.xml sitemap.xsl playspot-v29/generate.py playspot-v31/
if git diff --cached --quiet; then
  echo 'V31 already installed; nothing to commit.'
else
  git commit -m 'V31: add human-readable XML sitemap viewer'
  git push origin main
fi
echo 'SUCCESS: sitemap viewer installed. Open https://playspotstore.online/sitemap.xml'
