PlaySpotStore V40 — unique, truthful product descriptions RO/RU

Goals:
* Replace the 203 repeated placeholder descriptions while retaining existing editorial descriptions.
* 194 distinct, game-specific copy pairs in RO and RU; reused only for the same title on another platform.
* Short, page-specific meta descriptions that start with the gameplay/theme instead of generic store boilerplate.
* Surface existing catalog ID and platform as product facts; add the internal catalog ID to Product JSON-LD as sku.
* No fabricated availability, ratings, condition, release dates, warranties, specifications or GTIN.

Files:
  playspot-v40/descriptions.tsv = editable RO/RU editorial descriptions by title
  playspot-v40/apply.py = curate JSON, generate product pages and patch generator (repeat-safe)
  playspot-v40/validate.py = structural + copy + canonical + schema checks
  playspot-v40/install.sh = GitHub Codespaces installer (git commit and push)

Installation from repository root:
  git pull --ff-only origin main && unzip -o playspotstore-v40-unique-product-seo.zip -d . && bash playspot-v40/install.sh

Important: use title-specific descriptions, not search-engine keyword stuffing. Verify future product details against manufacturer/game sources before adding unsupported specifics.
