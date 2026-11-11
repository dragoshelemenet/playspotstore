PlaySpotStore V49 — clean canonical product URLs (RO/RU)
=======================================================

GOAL
- Remove the duplicated product name embedded in internal inventory IDs.
- Keep all existing product/category content, V42 editorial details, V44 local
  shopping/pickup/courier messaging, V47 category URLs, and V48 HTML menu.
- Product filename becomes the real title slug, e.g.
  /produse/nintendo/hyrule-warriors-age-of-imprisonment.html
  /produse/ps4/assassin-s-creed-odyssey.html
- No automatic '-chisinau-moldova' suffix on product URLs. Chișinău is already
  in local HTML titles/descriptions, and courier delivery in Moldova is visible.
- RO/RU product slugs use the SAME title slug under different language folders.
- Product IDs remain unchanged inside JSON/catalog and Product JSON-LD.
- If two products share a title slug, a short hash suffix is added deterministically.
- Existing slugs are persisted in playspot-v49/slug-index.json for future rebuilds.
- Canonical, RO/RU hreflang, sitemaps, homepage slugmaps, category product links
  and SEO generated-path manifest are rewritten to the new paths.
- An older V47 validation script is made forward-compatible.

NO REDIRECTS (per owner request)
- Older long product URLs are deleted. They will return HTTP 404 on GitHub Pages.
- This is not the Google-recommended migration approach. If the old URLs were
  crawled, indexed, bookmarked or linked externally, visitors/SEO can be affected.
- A lack of visible indexation does NOT prove Google has never crawled the URLs.
- Prefer genuine permanent 301 redirects when permitted by hosting/user policy.
- No automatic keyword-city pages, no stuffed URLs, no fake stock/ratings.

INSTALL
1. Upload playspotstore-v49-clean-product-urls.zip to GitHub main, repository root.
2. GitHub Codespaces repository root:
   git pull --ff-only origin main && unzip -o playspotstore-v49-clean-product-urls.zip -d . && bash playspot-v49/install.sh

Installer checks a clean working tree, validates canonical pages and sitemap,
commits only version-owned files, and pushes main. Repeat-safe.

Do not run older URL-migration installers (V45/V47) again after V49.
The V29 generator now uses V49 slug-index.json on future rebuilds.
