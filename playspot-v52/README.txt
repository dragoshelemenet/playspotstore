PLAYSPOTSTORE V52 — REAL 100% DESKTOP HEADER FIX
Date: 13 November 2026

ISSUE OBSERVED DIRECTLY IN THE LIVE BROWSER
At 100% zoom, CSS viewport is 1344px, within the old tablet breakpoint
951–1430px. V25 forces the mobile search list item visible even though
V51 displays the full desktop navigation. The unwanted search element
occupied 713px across the header and covered the logo and Spin & Win.
At 90%, the wider CSS viewport no longer matched the old tablet rule.

FIX
- Scope V25's two tablet media queries to (any-pointer:coarse).
- Keep V51's full desktop navigation for mouse/trackpad desktop browsers.
- Preserve the V25 touch-tablet menu and mobile <=950px.
- Update V25 stylesheet query on RO/RU pages so browsers fetch fixed CSS.
- Leave the 90% desktop layout unchanged.
- No modification to hero assets, product pages, sitemap, SEO, prices,
  or Spin & Win behavior.

AFTER UPLOADING THE ZIP TO GITHUB MAIN, RUN IN CODESPACES:
git pull --ff-only origin main && unzip -o playspotstore-v52-desktop-100-fix.zip -d . && bash playspot-v52/install.sh

Then hard-refresh playspotstore.online at 100% and 90% zoom.
The script is idempotent and will not duplicate modifications.
