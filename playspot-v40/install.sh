#!/usr/bin/env bash
set -euo pipefail
# Upload ZIP to the repo root, unzip, then run this from GitHub Codespaces.
if [[ ! -d .git || ! -f index.html || ! -f ru.html || ! -f playspot-v29/generate.py ]]; then
  echo 'ERROR: Open the playspotstore repository root in GitHub Codespaces.' >&2
  exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'ERROR: Tracked files have uncommitted changes. Commit or stash them before installing.' >&2
  exit 1
fi
git pull --ff-only origin main
if ! grep -q 'playspot-v39.css' index.html || ! test -f playspot-v37/patch.py; then
  echo 'ERROR: Install the current V39 baseline first.' >&2
  exit 1
fi
cp -f playspot-v40/playspot-v40.css playspot-v40.css
python3 -B playspot-v40/apply.py --root . --check
python3 -B playspot-v40/apply.py --root .
python3 -B playspot-v40/validate.py --root .
python3 -B playspot-v29/validate.py --root .
python3 -B playspot-v37/validate.py --root .
python3 -B playspot-v39/validate.py --root .
# Only stage paths owned by this update.
git add -A -- playspot-v40/ playspot-v40.css playspot-v29/generate.py data/ produse/ ru/produse/
if git diff --cached --quiet; then
  echo 'V40 is already installed: nothing to commit.'
else
  git commit -m 'V40: unique RO/RU product copy, truthful SEO metadata and catalog identifiers'
  git push origin main
fi
echo 'SUCCESS: V40 product SEO published to GitHub. GitHub Pages deployment follows automatically.'
