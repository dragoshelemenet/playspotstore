PlaySpotStore V31 FIX — Sitemap viewer installer repair
=======================================================
Fixes: Could not find the V29 sitemap write command
Cause: V30 changed sitemap generation from ET.ElementTree(rootxml).write(...) to tree.write(...).

Replace the failed V31 installer with this ZIP (it overwrites playspot-v31/patch.py):
  git pull --ff-only origin main && unzip -o playspotstore-v31-fixed.zip -d . && bash playspot-v31/install.sh

Changes:
- Keeps original /sitemap.xml with all URL entries intact.
- Adds /sitemap.xsl for human-readable sitemap display in browsers with XSLT support.
- Updates playspot-v29/generate.py to retain the stylesheet instruction on future regenerations.
- Safe to run again; the processing instruction and generator hook are installed only once.
- Runs playspot-v29/validate.py before committing/pushing.

Does not change catalog SEO URLs, robots.txt, hreflang, or products.
