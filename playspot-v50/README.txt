PlaySpotStore V50 — SEO Quality + Offline Crawl Audit
====================================================

GOALS
- Fix awkward mid-phrase meta snippets on 558 product pages in Romanian and Russian.
- Keep each product's real title, platform, and unique gameplay synopsis; include
  Chișinău/Moldova context naturally without claiming every item is second-hand.
- Add contextual alternative text to hero images and category card images.
- Audit 576 sitemap pages, canonical links, locale alternates, Product JSON-LD,
  hero images, and links between product/category pages.
- Generate playspot-v50/AUDIT.md and audit.json with truthful offline findings.

NOT CHANGED
- 279 product URLs (V49), 14 category URLs, or the canonical sitemap list.
- Product prices, stock, item condition, reviews, images or visual layout.
- V48 static HTML menu, page design, animations, JS product search and filters.
- No speculative GTIN/brand, availability, shipping costs, or physical shop address.

HOW TO INSTALL
1. Upload the ZIP to GitHub main repo root.
2. Open GitHub Codespaces repo root and run:
   git pull --ff-only origin main && unzip -o playspotstore-v50-seo-quality-audit.zip -d . && bash playspot-v50/install.sh
3. Read playspot-v50/AUDIT.md for further work. Read GSC Indexing/Pages after Google
   has crawled the pages; this offline audit cannot know live index coverage.

No URL migration or redirects. Each run is deterministic, with safeguards against
staging unrelated work, and a catalog regeneration hook that restores the patch.
