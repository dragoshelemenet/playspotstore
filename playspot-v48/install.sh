#!/usr/bin/env bash
set -euo pipefail
# Upload zip to main repository, then use the one-line command from README.
if [[ ! -d .git || ! -f index.html || ! -f ru.html || ! -f playspot-v29/generate.py ]]; then
  echo 'ERROR: Run at the PlaySpotStore repository root in Codespaces.' >&2; exit 1
fi
if [[ "$(git branch --show-current)" != main ]]; then
  echo 'ERROR: This installer expects the main branch.' >&2; exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'ERROR: Tracked changes found. No reset/stash performed.' >&2; exit 1
fi
# Intentional additional safe pull (the user's command also begins with git pull).
git pull --ff-only origin main
python3 -B playspot-v48/cleanup.py --root . --check
python3 -B playspot-v48/cleanup.py --root .
python3 -B playspot-v48/validate.py --root .
python3 -B playspot-v47/validate.py --root .
python3 -B playspot-v29/validate.py --root .
git add -- index.html ru.html playspot-v29/generate.py playspot-v48/
if git diff --cached --quiet; then
  echo 'V48 is already installed; no new commit.'
else
  git commit -m 'V48: remove duplicate legacy JS category navigation and popups'
  git push origin main
fi
echo 'SUCCESS: V48 static HTML SEO navigation, no duplicate menu.'
