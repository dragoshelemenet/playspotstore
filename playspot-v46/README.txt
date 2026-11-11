PlaySpotStore V46 — Natural Stable SEO Variations (RO + RU)
==========================================================
Goal: replace repetitive filler with varied, helpful, truthful wording. This is
NOT a script to rotate URL names, cloak content, create doorway city pages, or
bypass search spam detection. Synonym swaps alone do not make pages unique.

V45 was verified installed in the live GitHub repository when this update was
prepared. V45 currently uses -chisinau-moldova / -kishinev-moldova in URL paths.
V46 leaves ALL existing URL names unchanged, to avoid another risky migration.
It preserves canonical URLs, old-page redirects, alternate-language links,
XML sitemap, Product JSON-LD, prices, product condition, availability, reviews,
product IDs, images, homepage animation and category filters.

CONTENT VARIATION
 - 12 opener patterns x 16 factual delivery versions x 4 stable arrangements
   per language (768 base combinations before product-specific text).
 - Eight different order/condition notes, 16 clickable guide link labels,
   and seven category-specific delivery notes per language.
 - A SHA-256 based deterministic selection based on SKU, language and slot,
   fixed permanently for each URL; no random content on subsequent reloads.
 - Every product retains original catalog synopsis and its existing distinct
   editorial gameplay review; the state new/bu is never guessed.
 - Links still point to the same real shopping/delivery guide, and products
   keep one canonical page per language. Descriptions stay human-readable.

HOW TO INSTALL
1. Upload playspotstore-v46-natural-seo-mix.zip into main on GitHub.
2. Open GitHub Codespaces at the playspotstore repository root.
3. Paste:
   git pull --ff-only origin main && unzip -o playspotstore-v46-natural-seo-mix.zip -d . && bash playspot-v46/install.sh

The installer validates V46, V45, V44 and V29, and commits and pushes only
scoped files if all checks pass. Re-running the installer is repeat-safe.
Future full catalog regeneration will reapply V46 after V44 and V45.

Manual caution: Changing existing canonical URLs is a migration, not an SEO
shortcut. If you want to remove the geo suffix later, plan HTTP 301 redirects
through a suitable hosting/proxy provider instead of further random slug changes.
Official Google guidance:
 https://developers.google.com/search/docs/essentials/spam-policies
 https://developers.google.com/search/docs/crawling-indexing/url-structure
