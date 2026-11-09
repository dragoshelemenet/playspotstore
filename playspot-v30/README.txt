PlaySpotStore V30 — SEO card image/text separation + human-readable sitemap

Requires V29 SEO already installed (repo has playspot-v29/generate.py).

INSTALL from root of GitHub Codespaces repository:
  git pull --ff-only origin main && unzip -o playspotstore-v30-seo-card-fix.zip -d . && bash playspot-v30/install.sh

- Fixes varied image aspect ratios and prevents captions/buttons from overlapping images.
- Applies to all category pages in Romanian and Russian.
- Both the currently served stylesheet and the generator source are patched.
- Regenerates SEO pages with versioned stylesheet URL for fresh browser cache.
- Formats sitemap.xml with indentation; the URL entries are unchanged.
- Leaves item names, prices, Google metadata, robots.txt and Product JSON-LD intact.

The sitemap XML is expected to look like plain text in browsers. A missing XML stylesheet is not a search indexing issue.
