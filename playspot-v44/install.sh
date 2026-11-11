#!/usr/bin/env bash
set -euo pipefail
# Upload ZIP to GitHub repository main, git pull in Codespaces, unzip, then run.
if [[ ! -d .git || ! -f index.html || ! -f ru.html || ! -f playspot-v29/generate.py ]]; then
  echo 'ERROR: Run from the PlaySpotStore repository root.' >&2; exit 1
fi
if [[ "$(git branch --show-current)" != 'main' ]]; then
  echo 'ERROR: Expected branch main. No changes made.' >&2; exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'ERROR: Local tracked changes detected. Commit or resolve them first; no reset will be performed.' >&2; exit 1
fi
# Safe repeat even when the user already ran 'git pull' before unzip.
git pull --ff-only origin main
for file in playspot-v40/apply.py playspot-v42/validate.py playspot-v37/patch.py playspot-v29/validate.py; do
  if [[ ! -f "$file" ]]; then echo "ERROR: Missing expected baseline: $file" >&2; exit 1; fi
done
cp -f playspot-v44/playspot-v44.css playspot-v44.css
python3 -B playspot-v44/patch.py --root . --check
python3 -B playspot-v44/patch.py --root .
python3 -B playspot-v44/validate.py --root .
python3 -B playspot-v29/validate.py --root .
# Only updated tracked catalog pages + this version's own files.
git add -u -- index.html ru.html data/ categorii/ ru/categorii/ produse/ ru/produse/ playspot-v29/generate.py playspot-v29/validate.py playspot-v32/human_sitemap.py sitemap.xml
git add -- playspot-v44/ playspot-v44.css jocuri-video-chisinau-moldova.html ru/videoigry-kishinev-moldova.html sitemap.html ru/sitemap.html
if git diff --cached --quiet; then
 echo 'V44 already installed: no changes to commit.'
else
 git commit -m 'V44: natural Moldova and Chisinau local SEO for catalog'
 git push origin main
fi
echo 'SUCCESS: V44 Moldova SEO installed and validated.'
