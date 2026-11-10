PlaySpotStore V41 — expanded product descriptions RO / RU

This installer uses existing V40 product summaries as the factual starting point
and supplements them with hand-authored game-specific notes and restrained
information about the type of experience. Do not interpret the text as a
manufacturer data sheet. Where claims about a particular edition are unknown,
no technical specifications, included bonuses, stock, ratings or product
condition are invented. Some misleading earlier descriptions are corrected.

Currently expected inventory: 279 products / 558 rendered language pages.
Individual descriptions are roughly 80–150 words, not a ranking guarantee.
Meta descriptions remain short via the existing V40 generator; Product JSON-LD
uses the longer visible description. Product SKU, price, canonical, hreflang,
links, category filters, home animation and sitemap are preserved.

Contents:
  playspot-v41/editorial-facts.tsv  Specific RO/RU notes by title (editable)
  playspot-v41/augment.py         Repeat-safe JSON description expander
  playspot-v41/validate.py        Checks 279 products + bilingual SEO pages
  playspot-v41/install.sh         Codespaces installer: commit and push

To install from repository root, upload the zip there and run:
  git pull --ff-only origin main && unzip -o playspotstore-v41-expanded-product-seo.zip -d . && bash playspot-v41/install.sh

If you edit product descriptions after V41 and want to regenerate the HTML,
run `python3 -B playspot-v40/apply.py --root .` and re-run the validators.

Official reference for Super Mario Maker 2:
  https://supermariomaker.nintendo.com/
  https://www.nintendo.com/us/store/products/super-mario-maker-2-switch/
Google's helpful content guide (quality matters more than raw word count):
  https://developers.google.com/search/docs/fundamentals/creating-helpful-content
