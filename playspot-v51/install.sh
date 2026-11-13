#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname -- "$SCRIPT_DIR")"
cd "$REPO_ROOT"
if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "ERROR: run this inside the PlaySpotStore GitHub Codespace." >&2
  exit 1
fi
if [[ -n "$(git diff --cached --name-only)" ]]; then
  echo "ERROR: you already have staged changes. Commit/unstage them first so this installer does not mix projects." >&2
  exit 1
fi

python3 playspot-v51/patch.py
python3 playspot-v51/verify.py
git diff --check

git add -- index.html ru.html neon-v5-fixes.js playspot-v51.css \
  playspot-v51/install.sh playspot-v51/patch.py playspot-v51/verify.py playspot-v51/README.txt

if git diff --cached --quiet; then
  echo "V51 is already installed; no commit needed."
  exit 0
fi
git commit -m "Fix desktop header zoom, navigation and Spin & Win spacing (V51)"
git push origin main
echo "V51 installed and pushed. Reload site with Ctrl+Shift+R / Cmd+Shift+R."
