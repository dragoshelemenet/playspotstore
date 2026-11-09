#!/usr/bin/env bash
set -euo pipefail
if [[ ! -d .git || ! -f index.html || ! -f ru.html || ! -f playspot-v29/generate.py ]]; then
  echo 'Run from playspotstore repository root, after installing V29 SEO.' >&2
  exit 1
fi
# Always update the active branch before modifying the catalog.
git pull --ff-only origin main
python3 playspot-v30/fix_cards.py
python3 playspot-v29/generate.py --root .
python3 playspot-v29/validate.py --root .
python3 - <<'PY'
from pathlib import Path
root=Path('.')
css=(root/'seo/site.css').read_text(encoding='utf-8')
assert css.count('/* PlaySpotStore V30: fixed-image SEO cards')==1
assert 'object-fit:contain!important;' in css
samples=list((root/'categorii').glob('*.html'))
assert samples
assert '/seo/site.css?v=20261109-v30' in samples[0].read_text(encoding='utf-8')
sitemap=(root/'sitemap.xml').read_text(encoding='utf-8')
assert sitemap.startswith('<?xml') and '\n  <url>' in sitemap
print('V30 check passed: CSS, SEO cache refresh, readable sitemap')
PY
git add -A seo/site.css playspot-v29/seo.css playspot-v29/generate.py playspot-v30/ sitemap.xml categorii/ produse/ ru/categorii/ ru/produse/ index.html ru.html
if git diff --cached --quiet; then
  echo 'V30 already installed; no new changes.'
else
  git commit -m 'V30: prevent image/text overlap in SEO catalog cards'
  git push origin main
fi
echo 'SUCCESS: V30 SEO cards and sitemap formatting are deployed.'
