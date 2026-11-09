PLAYSPOTSTORE V29 — FULL STATIC SEO CATALOG (RO + RU)

UPLOAD: playspotstore-v29-seo-pages.zip into your Codespaces repository root.
RUN:
git pull --ff-only origin main && unzip -o playspotstore-v29-seo-pages.zip -d . && bash playspot-v29/install.sh

What it does:
- Reads current data/*.json as the ONLY product source.
- Builds an actual HTML URL for every product and every category, in RO/RU.
- Adds canonical URLs, hreflang pairs, metadata, product JSON-LD, breadcrumb data.
- Builds /sitemap.xml with localized URLs and /robots.txt with the correct domain.
- Corrects the wrong playstationspot.store domain in the existing homepages.
- Makes homepage category tiles, menu links, and product links crawlable real URLs.
- Preserves existing homepage design, Spin & Win, analytics counter and sales sections.

The number of generated pages depends on the catalog. At build: 279 products => 558 product URLs, 14 categories, 2 homepages, total 574 URLs.

IMPORTANT: Re-run after updating product JSON:
python3 playspot-v29/generate.py --root .
git add -A index.html ru.html seo/ sitemap.xml robots.txt playspot-v24.js playspot-v29/ categorii/ produse/ ru/categorii/ ru/produse/
git commit -m "Refresh product SEO pages" && git push origin main

Google Search Console: https://search.google.com/search-console
Submit: https://playspotstore.online/sitemap.xml
SEO improvements help crawlability; Google controls ranking and indexing.

No historic visitor counts, stock status, customer reviews or new prices are made up.
If some product photos are hosted externally, those hosts may block their loading.
