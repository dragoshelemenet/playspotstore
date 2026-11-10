#!/usr/bin/env bash
set -euo pipefail
# Run in the repo root after extracting the V41 archive.
if [[ ! -d .git || ! -f index.html || ! -f ru.html || ! -f playspot-v29/generate.py ]]; then
  echo 'ERROR: Open the PlaySpotStore repository root in GitHub Codespaces.' >&2
  exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'ERROR: Existing tracked changes were detected. Commit or stash them first.' >&2
  exit 1
fi
git pull --ff-only origin main
for f in playspot-v40/apply.py playspot-v40/validate.py playspot-v40.css playspot-v39.css; do
 if [[ ! -s "$f" ]]; then echo "ERROR: V40 baseline missing $f. Install V40 first." >&2; exit 1; fi
done
python3 -B playspot-v41/augment.py --root . --check
python3 -B playspot-v41/augment.py --root .
# V40 has the tested static Product-page builder, including canonical, RO/RU and JSON-LD.
python3 -B playspot-v40/apply.py --root .
python3 -B playspot-v41/validate.py --root .
python3 -B playspot-v40/validate.py --root .
python3 -B playspot-v29/validate.py --root .
# Stage only owned copy and generated product pages; no changes to hero, filters or category UI.
git add -A -- playspot-v41/ data/ produse/ ru/produse/
if git diff --cached --quiet; then
 echo 'V41 is already installed; no changes to commit.'
else
 git commit -m 'V41: extended bilingual product descriptions and improved product SEO'
 git push origin main
fi
echo 'SUCCESS: V41 product descriptions updated. GitHub Pages will deploy as usual.'
