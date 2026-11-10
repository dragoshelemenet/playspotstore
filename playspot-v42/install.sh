#!/usr/bin/env bash
set -euo pipefail
# V42.2 hotfix: continues a partially completed V42 install without deleting work.
# Run: unzip -o playspotstore-v42-fixed-v2.zip -d . && bash playspot-v42/install.sh
if [[ ! -d .git || ! -f index.html || ! -f ru.html || ! -f playspot-v29/generate.py ]]; then
  echo 'ERROR: Open GitHub Codespaces at the PlaySpotStore repository root.' >&2
  exit 1
fi
if [[ "$(git branch --show-current)" != 'main' ]]; then
  echo 'ERROR: Expected to be on the main branch. No changes have been made.' >&2
  exit 1
fi
# Never absorb user changes already staged for another commit.
if [[ -n "$(git diff --cached --name-only)" ]]; then
  echo 'ERROR: There are staged changes. Commit/unstage those before proceeding.' >&2
  exit 1
fi
# Dirty worktree is expected after the first failed V42 attempt. Reject any
# changes outside the paths the failed installer itself could have modified.
python3 -B playspot-v42/preflight.py --root .
if [[ -n "$(git diff --name-only)" ]]; then
  echo 'Continuing the interrupted V42 install; keeping existing product edits.'
  # Fetch is safe for a dirty working tree, unlike pull/merge.
  git fetch origin main
  if ! git merge-base --is-ancestor origin/main HEAD; then
    echo 'ERROR: Your branch is behind origin/main. No reset/overwrite performed.' >&2
    exit 1
  fi
else
  git pull --ff-only origin main
fi
for f in playspot-v40/apply.py playspot-v40/validate.py playspot-v41/editorial-facts.tsv playspot-v40/descriptions.tsv; do
  if [[ ! -s "$f" ]]; then echo "ERROR: Missing $f. Install V41 first." >&2; exit 1; fi
done
cp -f playspot-v42/playspot-v42.css playspot-v42.css
python3 -B playspot-v42/rewrite.py --root . --check
python3 -B playspot-v42/rewrite.py --root .
python3 -B playspot-v40/apply.py --root .
python3 -B playspot-v42/validate.py --root .
python3 -B playspot-v40/validate.py --root .
python3 -B playspot-v29/validate.py --root .
git add -A -- playspot-v42/ playspot-v42.css data/ produse/ ru/produse/ playspot-v29/generate.py
if git diff --cached --quiet; then
  echo 'V42 already installed; no changes to commit.'
else
  git commit -m 'V42: bilingual editorial product copy (meta length hotfix)'
  git push origin main
fi
echo 'SUCCESS: V42 installed and validated. GitHub Pages will deploy normally.'
