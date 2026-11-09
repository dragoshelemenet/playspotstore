#!/usr/bin/env python3
"""V39 smoke-check for the two static SEO homepages."""
from pathlib import Path
import argparse
import re

CATS = ('ps4','ps5','nintendo','xbox','console','accessories')

def validate(root):
    root = root.resolve()
    for home, prefix in (('index.html','/categorii/'), ('ru.html','/ru/categorii/')):
        s = (root/home).read_text(encoding='utf-8')
        head = s.split('</head>',1)[0]
        assert all(head.count('playspot-v'+v+'.css') == 1 for v in ('34','35','38','39')), home
        assert head.index('playspot-v38.css') < head.index('playspot-v39.css'), home
        assert s.count('playspot-v39.js') == 1, home
        assert s.count('class="category-deck"') == 1, home
        links = re.findall(r'<a\s+class="category-tile ([^"]+)" href="([^"]+)"[^>]*><img\s+[^>]+>', s)
        assert len(links) == len(CATS), (home, links)
        assert tuple(cat for cat,href in links) == CATS, home
        for cat,href in links:
            dest = 'consoles' if cat == 'console' else cat
            assert href == prefix+dest+'.html', (home,cat,href)
        assert 'p29ProductSlugs' in s and 'id="catalog-seo"' in s, 'SEO catalog missing'
    css = (root/'playspot-v39.css').read_text(encoding='utf-8')
    js = (root/'playspot-v39.js').read_text(encoding='utf-8')
    for check in ('--p34-up: -5.5px', '--p38-float-y: -5.5px', 'prefers-reduced-motion', 'p39-opening'):
        assert check in css, check
    for check in ('event.defaultPrevented', 'event.metaKey', 'event.ctrlKey','event.shiftKey', 'event.altKey', 'window.location.assign', 'pageshow'):
        assert check in js, check
    assert 'addon39 = root / "playspot-v39"' in (root/'playspot-v29/generate.py').read_text(encoding='utf-8')
    print('V39 VALID: two language homepages, 12 category hrefs, float amplitudes and native navigation safe-guards')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.')
    validate(Path(p.parse_args().root))
