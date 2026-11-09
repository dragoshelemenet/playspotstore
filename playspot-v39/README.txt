PlaySpotStore V39 — Floating +10% & Category Click Feedback

Requires: V38 already installed in the GitHub repo.
Scope: index.html and ru.html homepage category cards. No edits to product/catalog pages.

What changes:
- Increases floating translation in the 3-layer V34 hero by precisely 10%.
- Increases the independent 6 category image float amplitude by ~10%.
- Keeps cards, text and borders stable; no new images, video or layout changes.
- Adds a 245ms neon press + image pop when opening a homepage category in the same tab.
- Ctrl/Cmd/Shift/Alt-click, open in new tab, middle-click, back/forward and Reduce Motion are preserved.
- Maintains a generator hook to keep the changes through future SEO catalog regeneration.

Codespaces install:
1. Upload playspotstore-v39-floating-click.zip to repo root.
2. Run:
   git pull --ff-only origin main && unzip -o playspotstore-v39-floating-click.zip -d . && bash playspot-v39/install.sh

Installs (pushes to main automatically) after checks succeed. Repeat-safe.
