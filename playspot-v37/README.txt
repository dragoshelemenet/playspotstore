PlaySpotStore V37 — Integrated Search + Collapsible Filters
=========================================================
Builds on installed V36 (and preserves V35/V32/V33 functionality).

- Moves the category search panel INSIDE the existing category hero box.
- No second outer border: just one hero border with PLAYSPOTSTORE · Catalog, title and search.
- Search and sorting stay visible.
- A compact Filtre / Фильтры button expands the price inputs, price bands,
  new-products-only and priced-products-only filters; they are hidden by default.
- Result count and reset stay accessible.
- Applies to 7 categories x RO/RU = 14 pages.
- Preserves all crawlable cards, SEO, canonical and hreflang, sitemap and V35 animations.
- Adds a generation hook immediately after V36's hook so the layout survives catalog rebuilds.
- Repeat-safe installer, safely checks for uncommitted tracked edits.

INSTALL IN CODESPACES (from repository root)
------------------------------------------
git pull --ff-only origin main && unzip -o playspotstore-v37-hero-dropdown.zip -d . && bash playspot-v37/install.sh

This installer performs git pull, checks prerequisites, modifies category pages,
validates them, makes a commit and pushes it to origin/main. This package alone
is NOT deployed until you run the command.
