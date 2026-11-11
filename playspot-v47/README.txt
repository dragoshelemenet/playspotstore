PlaySpotStore V47 — restore clean original URLs, NO redirects
==============================================================

This update is intended for a site where V45 (the -chisinau-moldova URL migration)
is already installed. V46 may or may not be installed.

- Restores all 558 original bilingual product URLs and 14 original category URLs.
- Removes the 572 generated geographic URL files instead of redirecting them.
- Restores canonical, hreflang, schema Product.url, sitemap and homepage product
  search/category links to the original stable URLs.
- Keeps game-specific editorial content and existing local delivery language.
- Saves each localized visible product description in data/*.json so that future
  V29 product page rebuilds retain this content even after V45 URLs are gone.
- Disables V45 and V46 legacy regeneration hooks so the old geo migration does
  not run again. Existing V44 SEO category/delivery functionality remains.
- Never invents itemCondition, ratings, stock, courier fees, or guarantees.
- Does not edit robots.txt, home hero animation, product prices or inventory IDs.
- Can be run again safely and checked with --check.

NOTE: No redirects was explicitly requested. The removed geographic URLs will
return 404 on GitHub Pages. If Google or third-party pages have already indexed
or linked to them, rankings or traffic may be lost; HTTP 301 redirects are the
recommended approach when moving already-discovered URLs.

Install in Codespaces after uploading the ZIP to GitHub main:
  git pull --ff-only origin main && unzip -o playspotstore-v47-clean-urls-no-redirects.zip -d . && bash playspot-v47/install.sh
