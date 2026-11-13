#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname -- "$SCRIPT_DIR")"
cd "$REPO_ROOT"

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "ERROR: run inside the PlaySpotStore Codespace." >&2
  exit 1
fi
if [[ -n "$(git diff --cached --name-only)" ]]; then
  echo "ERROR: you already have staged changes; commit or unstage them first." >&2
  exit 1
fi

python3 playspot-v52/patch.py
python3 playspot-v52/verify.py
git diff --check
git add -- index.html ru.html playspot-v25.css \
  playspot-v52/install.sh playspot-v52/patch.py playspot-v52/verify.py playspot-v52/README.txt

if git diff --cached --quiet; then
  echo "V52 already installed."
  exit 0
fi
git commit -m "Fix desktop 100 percent zoom header overlap (V52)"
git push origin main
echo "V52 pushed. Refresh the page with Cmd+Shift+R or Ctrl+Shift+R."
