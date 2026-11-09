PlaySpotStore V35 - scroll-reactive parallax for V34 hero

Install: git pull --ff-only origin main && unzip -o playspotstore-v35-scroll-hero.zip -d . && bash playspot-v35/install.sh

Moves the existing three lossless WebP layers independently based on scroll progress while preserving V34's passive floating loop.
Smooth and limited: max 23 px main, 17 px sparks, 43 px symbols on desktop; less on phones/tablets.
No new images, no GIF, no video. Uses passive scroll listeners and requestAnimationFrame. Supports reduced motion.
RO and RU homepage updated. Regenerating SEO pages with V29 preserves the homepage hero.
