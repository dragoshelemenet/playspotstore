V42 HOTFIX (2026-11-10): fixed installer on generators containing both category_html and product_html.
The previous V42 archive stopped at a duplicate template anchor; no catalog changes were written.

PLAYSPOTSTORE V42 — GAMEPLAY IMPRESSIONS & BETTER PRODUCT SEO

V42 replaces the long generic V41 product copy with:
- a concise, title-specific factual synopsis;
- a separately labelled editorial gameplay-impression section that draws on
  267 V41 curated factual source notes + 76 specially written player-focused
  editorial angles (with varied, genre-specific editorial commentary for all
  other titles);
- short, individual <meta name="description"> / OG / Twitter descriptions;
- 279 catalog products, displayed in 558 bilingual RO/RU SEO HTML pages.

These are EDITORIAL DESCRIPTIONS, not verified user reviews or claims that our
editor personally played each game. No invented star ratings, Product.review,
aggregateRating, verified purchase labels, stock details, product condition,
platform specifications, or technical performance metrics.

Keep existing public URLs, SKU IDs, prices, images, canonical, hreflang,
Product JSON-LD and category search/filters/homepage animations unchanged.

INSTALL from repository root after uploading the ZIP:
git pull --ff-only origin main && unzip -o playspotstore-v42-fixed.zip -d . && bash playspot-v42/install.sh

After editing product data by hand, run:
python3 -B playspot-v40/apply.py --root .
then re-run validation. Do not run the old V41 augment.py after installing
V42; that tool is meant for its original V40->V41 upgrade.

EDITING CONTENT:
- playspot-v42/review-angles.tsv: 76 hand-written, bilingual review angles
- playspot-v41/editorial-facts.tsv: 267 title-specific fact notes
- playspot-v40/descriptions.tsv: 194 first-sentence factual summaries
- data/<category>.json + data/<category>_ru.json: public inventory SEO copy

SEO rationale:
https://developers.google.com/search/docs/fundamentals/creating-helpful-content
https://developers.google.com/search/docs/appearance/snippet

This does not guarantee ranking; individual content should be reviewed for
accuracy against the actual editions/items available in the shop.

V42.2 HOTFIX (meta description length)
- V29 generator truncates HTML meta description to 165 characters.
- The earlier V42 copy builder could generate 166+ characters, failing V42 validate.
- This archive caps the generated SEO metadata at 160 characters.
- Running the installer after a failed V42 attempt is supported without deleting local
  changes. Only interrupted V42 edits to product JSON/HTML and generator are allowed.
- IMPORTANT: Because the failed install left tracked files modified, do not run
  a separate git pull, reset, or stash. After uploading the new ZIP run:
  unzip -o playspotstore-v42-fixed-v2.zip -d . && bash playspot-v42/install.sh
