PlaySpotStore V32 — crawler-first sitemap
===========================================
- /sitemap.xml contains standard XML with canonical URLs + RO/RU hreflang; NO XSLT dependency.
- /robots.txt references the canonical XML sitemap.
- /sitemap.html and /ru/sitemap.html are separate no-JS HTML sitemaps grouped by platform.
- Homepage and all generated category/product pages link to their human-language HTML sitemap.
- Re-running playspot-v29/generate.py regenerates both XML and HTML sitemaps from data/*.json.
- No invented timestamps, prices, availability, robots metrics, or fake indexing claims.

Run from the repository root:
  git pull --ff-only origin main && unzip -o playspotstore-v32-crawler-sitemap.zip -d . && bash playspot-v32/install.sh

After publishing, submit https://playspotstore.online/sitemap.xml in Google Search Console.
This improves discovery but does not guarantee Google will index/rank every page.
