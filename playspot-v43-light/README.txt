PlaySpotStore V43 Light — natural SEO for NEW + SECOND-HAND games

Why this replaces the earlier V43 draft:
- The earlier V43 used-game package should NOT be installed.
- This V43 Light update recognizes that PlaySpotStore sells both new and used games.
- No false claim that all products, categories, consoles or accessories are used.
- No per-product itemCondition changes; no UsedCondition is added to Product schema.

Changes:
- index.html and ru.html ONLY: short page title, meta description, one existing
  paragraph beneath "Descopera catalogul PlaySpotStore" / "Каталог PlaySpotStore".
- The normal homepage hero, cards, animations, catalog links and visible category
  titles stay unchanged.
- No product JSON, category page, pricing, stock, sitemap, or code generator changes.
- The current V29 generator preserves this paragraph in its existing discovery section.

Install from the repository root in GitHub Codespaces:
  git pull --ff-only origin main && unzip -o playspotstore-v43-light-seo.zip -d . && bash playspot-v43-light/install.sh

This installer refuses to overwrite existing tracked changes. It updates and
checks the two homepages, validates the existing SEO structure, commits and
pushes only its own files. It makes no claim of guaranteed rankings.
