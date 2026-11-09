#!/usr/bin/env bash
set -euo pipefail
# Run from repository root after uploading the ZIP there.
if ! test -d .git || ! test -f index.html || ! test -f ru.html; then
  echo 'ERROR: Run this script from the PlaySpotStore repository root in Codespaces.' >&2
  exit 1
fi
# Requirement from earlier updates: always pull first.
git pull --ff-only origin main
python3 playspot-v29/generate.py --root .
python3 playspot-v29/validate.py --root .
# Avoid sweeping in unrelated modifications from the working tree.
git add -A index.html ru.html robots.txt sitemap.xml playspot-v24.js seo/ playspot-v29/ categorii/ produse/ ru/categorii/ ru/produse/
if git diff --cached --quiet; then
  echo 'SEO pages already up to date; nothing to commit.'
else
  git commit -m 'V29: static bilingual SEO catalog, product pages and sitemap'
  git push origin main
fi
echo 'SUCCESS: V29 static SEO pages and site navigation have been generated and published.'
