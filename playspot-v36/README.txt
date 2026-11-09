PlaySpotStore V36 | INTEGRATED CATEGORY SEARCH & PRICE FILTERS

Features
- On-page instant product name search on all 7 RO + 7 RU category pages.
- Min/max MDL price, quick price ranges, sort by price/title/new, new/has-price checkboxes.
- Live result count, reset, empty-results feedback, responsive gaming-neon styling.
- Removes the generic introductory paragraph from category hero and replaces generic SEO descriptions with short meaningful snippets.
- Keeps all cards and product links in HTML for Google; filtering happens in browser only.
- Auto-runs after later playspot-v29/generate.py catalog rebuilds.
- Does not modify the homepage's V34/V35 animations or existing product pages.

INSTALL (from root of your GitHub Codespaces checkout):
1. Upload playspotstore-v36-category-search.zip into the repository root.
2. Run:
   git pull --ff-only origin main && unzip -o playspotstore-v36-category-search.zip -d . && bash playspot-v36/install.sh
3. Hard refresh the category page after GitHub Pages finishes deployment.

NOTE: If Git reports local modifications, commit or stash them first (installer intentionally refuses to clobber them).
Example: https://playspotstore.online/categorii/nintendo.html
Russian: https://playspotstore.online/ru/categorii/nintendo.html
