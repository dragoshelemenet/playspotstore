#!/usr/bin/env bash
set -euo pipefail
# Run from PlaySpotStore repository root after uploading/extracting V32.
if ! test -d .git || ! test -f index.html || ! test -f ru.html || ! test -f playspot-v29/generate.py; then
  echo 'ERROR: Open the PlaySpotStore repository root in Codespaces (V29 required).' >&2
  exit 1
fi
git pull --ff-only origin main
python3 playspot-v32/patch.py --root .
python3 playspot-v29/generate.py --root .
python3 playspot-v29/validate.py --root .
python3 playspot-v32/validate.py --root .
# Stage only generated SEO assets + installer, no unrelated user files.
git add -A -- index.html ru.html robots.txt sitemap.xml sitemap.html ru/sitemap.html playspot-v29/generate.py playspot-v32/ seo/ categorii/ produse/ ru/categorii/ ru/produse/
if git ls-files --error-unmatch sitemap.xsl >/dev/null 2>&1; then git add -A -- sitemap.xsl; fi
if test -f playspot-v24.js; then git add -- playspot-v24.js; fi
if git diff --cached --quiet; then
  echo 'V32 already installed; nothing to commit.'
else
  git commit -m 'V32: plain XML sitemap for crawlers and separate HTML sitemap'
  git push origin main
fi
echo 'SUCCESS: plain XML sitemap for Google at https://playspotstore.online/sitemap.xml'
echo 'Human site map at https://playspotstore.online/sitemap.html'
