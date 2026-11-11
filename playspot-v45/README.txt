PlaySpotStore V45 — Moldova/Chișinău URLs + natural delivery in product copy
============================================================================

This is an intentional URL migration. V44 must already be installed.

WHAT CHANGES
- One canonical product page per existing SKU and language. Product URL now ends
  -chisinau-moldova.html (Romanian), -kishinev-moldova.html (Russian).
  Example: /produse/ps4/sonic-colors-ultimate-ps4-ID-chisinau-moldova.html
- Category pages use helpful slugs like:
  /categorii/jocuri-ps4-chisinau-moldova.html
  /ru/categorii/igry-ps4-kishinev-moldova.html
- Every product description shows its specific title + original genuine
  synopsis + appropriately worded Chișinău handover/Moldova courier options,
  in varied natural orders. Existing V42 editorial impression remains.
- All internal links and homepage JS product URL lookup point to new URLs.
- Canonical, hreflang, OpenGraph URL, Product/Breadcrumb/Offer URL and XML/HTML
  sitemap are updated. No city-specific duplicate product pages.
- Old product/category URLs remain available as immediate HTML redirects
  (with canonical pointing to the new page).
- All prices, SKU, inventory status, product condition, game reviews, and
  existing home animation/category filters remain unchanged.

HOSTING / SEO CAVEAT
GitHub Pages does not natively support configurable HTTP 301 redirects. The
old URLs use <meta http-equiv="refresh" content="0;..."> as a fallback, which
Google can interpret as a redirect, but server-side 301/308 is preferable.
The included url-map.json lists every old/new URL for later setting up real
301 redirects at your DNS proxy/hosting layer (e.g. Cloudflare Rules).
A URL migration can temporarily affect indexing/rankings; city keywords in URLs
are minor signals and never guarantee first-page rankings. Do not change URL
routes repeatedly just to add other cities, or create doorway pages.

INSTALL IN CODESPACES
1. Upload playspotstore-v45-local-urls.zip to the repository's main branch.
2. Run:
   git pull --ff-only origin main && unzip -o playspotstore-v45-local-urls.zip -d . && bash playspot-v45/install.sh

After deployment, submit https://playspotstore.online/sitemap.xml in Google
Search Console and inspect a representative new URL and old redirect.
For future catalog rebuilds, the V29 -> V44 -> V45 hooks automatically rerun
SEO copy, canonical URL migration and sitemap link updates.
