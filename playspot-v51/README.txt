PLAYSPOTSTORE V51 — DESKTOP HEADER + NORMAL ZOOM LAYOUT
13 November 2026

WHAT IS FIXED
- Desktop with a mouse/trackpad (without touch-pointer capability) keeps the visible CONTACT /
  CUM COMAND / JOCURI PS4 / JOCURI PS5 / NINTENDO / XBOX / CONSOLE /
  ACCESORII navigation at normal 100% browser zoom.
- At widths 1180 CSS px and above: compact one-row desktop header.
- At widths 951–1179 CSS px: two-row desktop header, all links still visible.
- Spin & Win is in the header layout flow on normal desktop widths,
  so it cannot cover CONTACT, including at 90% browser zoom.
- The homepage hero, tagline, and six category tiles use a compact desktop
  layout similar in density to the desired 80% view.
- Touch-capable tablets, including tablet + trackpad, and mobile <=950px
  retain their hamburger menu.
- Romanian and Russian homepages are updated together.
- No changes to product URL structure, canonical, hreflang, prices, SEO data,
  product templates, discount campaign, or spin prizes.

ROOT CAUSE
Existing V25 tablet CSS switched every viewport 951–1430 CSS px to a
hamburger regardless of pointer type; neon-v5-fixes.js moved the nav element
outside its header under the same breakpoint. V51 uses pointer-aware logic.

INSTALL IN GITHUB CODESPACES AFTER UPLOADING ZIP TO THE REPOSITORY ROOT
git pull --ff-only origin main && unzip -o playspotstore-v51-desktop-header-fix.zip -d . && bash playspot-v51/install.sh

TEST AFTER DEPLOYMENT
- Set desktop browser zoom to 100%, 90%, and 80%.
- Check full header links + search and click Spin & Win.
- Resize a desktop window to ~1050px: links should move to second row.
- Check phone width and touch iPad: hamburger should still open.
- Check /ru.html for the same layout.
- Hard refresh to clear cached CSS/JS.

INSTALLER NOTES
- Runs static assertions on both languages and CSS/JS breakpoints.
- Refuses to combine unrelated already-staged Git changes.
- Stages only V51-related files, commits, and pushes.
- Safe to run again; repeated installations do not duplicate CSS links.
