#!/usr/bin/env bash
set -euo pipefail
# V43 Light: new + second-hand in natural homepage SEO wording only.
if [[ ! -d .git || ! -f index.html || ! -f ru.html || ! -f playspot-v29/validate.py ]]; then
  echo 'ERROR: Open the PlaySpotStore repository root in GitHub Codespaces.' >&2
  exit 1
fi
if [[ "$(git branch --show-current)" != 'main' ]]; then
  echo 'ERROR: Expected branch main. No changes made.' >&2
  exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'ERROR: Tracked files have local changes. Commit or resolve them first; no reset was performed.' >&2
  exit 1
fi
# A second pull is harmless if the outer command has already updated the branch.
git pull --ff-only origin main
python3 -B playspot-v43-light/patch.py --root . --check
python3 -B playspot-v43-light/patch.py --root .
python3 -B playspot-v43-light/validate.py --root .
python3 -B playspot-v29/validate.py --root .
git add -A -- index.html ru.html playspot-v43-light/
if git diff --cached --quiet; then
  echo 'V43 Light already installed; nothing to commit.'
else
  git commit -m 'V43 Light: natural homepage SEO for new and used games'
  git push origin main
fi
echo 'SUCCESS: V43 Light homepage-only SEO installed.'
