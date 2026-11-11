PlaySpotStore V48 — Delete duplicate JavaScript menu, retain real SEO HTML menu

Root cause: a legacy script fetches data/categories.json and categories_ru.json
and appends popup-only category links to #main-menu. It tests the old category
URLs, so after the SEO URL updates it no longer recognizes the real HTML links.
Result: duplicate PS4/PS5/Consoles/Accessories items in desktop/mobile menus.

This patch:
 - removes the redundant dynamic category menu fetch and popup click handlers;
 - removes four obsolete category-modal elements and their unused helpers;
 - preserves the existing static HTML menu, SEO category deck, product search,
   mobile hamburger, product-detail modal, Spin & Win, SEO pages, data and prices;
 - adds an idempotent generator hook to prevent the old menu from returning;
 - edits ONLY index.html, ru.html and playspot-v29/generate.py.

Run in GitHub Codespaces from the repo root after uploading the ZIP to GitHub:
  git pull --ff-only origin main && unzip -o playspotstore-v48-menu-cleanup.zip -d . && bash playspot-v48/install.sh

The script will commit/push on main only after all applicable checks pass.
