#!/usr/bin/env python3
"""PlaySpotStore V34: replace one static homepage image with 3 real animated layers."""
from pathlib import Path
import re
import argparse

STYLE = '<link rel="stylesheet" href="playspot-v34.css?v=20261109-v34">'
LAYERS = '''<div class="hero-art p34-hero-art"><div class="p34-layers" role="img" aria-label="PlaySpotStore – consolă PlayStation, controller și simboluri gaming neon animate">
<img class="p34-layer p34-main" src="media/hero-subject-v34.webp" width="1500" height="612" alt="" aria-hidden="true" decoding="async" fetchpriority="high">
<img class="p34-layer p34-sparks" src="media/hero-sparks-v34.webp" width="1500" height="612" alt="" aria-hidden="true" decoding="async" fetchpriority="low">
<img class="p34-layer p34-symbols" src="media/hero-symbols-v34.webp" width="1500" height="612" alt="" aria-hidden="true" decoding="async" fetchpriority="low">
</div></div>'''

HERO_PATTERN = re.compile(r'<div\s+class="hero-art">\s*<img\b[^>]*\bneon-hero-v2\.webp[^>]*>\s*</div>', re.I)


def patch(root: Path):
    root = root.resolve()
    for path in [root/'index.html', root/'ru.html']:
        if not path.is_file():
            raise RuntimeError(f'Missing page: {path}')
        source = path.read_text(encoding='utf-8')
        # Do not alter other parts of the existing page, catalog, or SEO elements.
        if path.name == 'ru.html':
            label = 'PlaySpotStore — неоновая игровая приставка, геймпад и символы PlayStation'
        else:
            label = 'PlaySpotStore – consolă PlayStation, controller și simboluri gaming neon animate'
        layers = LAYERS.replace('PlaySpotStore – consolă PlayStation, controller și simboluri gaming neon animate', label)
        if 'class="hero-art p34-hero-art"' in source:
            updated = source
        else:
            updated, count = HERO_PATTERN.subn(lambda _: layers, source, count=1)
            if count != 1:
                raise RuntimeError(f'Expected exactly one original hero illustration in {path.name}')
        # Stylesheet loaded after all existing site CSS, including V25/tablet styles.
        if STYLE not in updated:
            if '</head>' not in updated:
                raise RuntimeError(f'Cannot find head in {path.name}')
            updated = updated.replace('</head>', '  '+STYLE+'\n</head>', 1)
        if updated != source:
            path.write_text(updated, encoding='utf-8')
        print(f'OK: {path.name} — layered hero and stylesheet')
    for asset in ['hero-subject-v34.webp','hero-sparks-v34.webp','hero-symbols-v34.webp']:
        if not (root/'media'/asset).is_file():
            raise RuntimeError(f'Missing WebP asset: media/{asset}')
    print('OK: three 1500 x 612 lossless WebP layers present; no changes to SEO/sitemap.')

if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    args=ap.parse_args()
    patch(Path(args.root))
