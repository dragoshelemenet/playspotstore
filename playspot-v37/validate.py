#!/usr/bin/env python3
"""V37 smoke tests: 14 localized pages, SEO integrity, one hero box, collapsed extras."""
from pathlib import Path
import argparse
import re
import json

CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')

def validate(root: Path):
    for lang, prefix in [('ro','categorii'),('ru','ru/categorii')]:
        for cat in CATS:
            path=root/prefix/(cat+'.html')
            s=path.read_text(encoding='utf-8')
            assert s.count('class="seo-category-hero p37-hero"')==1, path
            assert s.count('class="p36-filter-panel p37-integrated"')==1, path
            assert s.count('data-p37-toggle')==1 and s.count('data-p37-extras hidden')==1, path
            assert s.count('class="p36-extras" id="p37-advanced-filters" data-p37-extras hidden')==1, path
            assert s.count('data-p36-search')==1 and s.count('data-p36-sort')==1, path
            assert s.count('playspot-v37.css')==1 and s.count('playspot-v37.js')==1, path
            hero=s.split('<section class="seo-category-hero p37-hero">',1)[1].split('</section>',1)[0]
            assert '<h1>' in hero and 'data-p36-search' in hero and 'data-p36-min' in hero, path
            assert 'p36-filter-panel' not in s.split('<section class="seo-list"',1)[0].split('</section>',1)[-1], path
            assert '<div class="seo-grid">' in s and 'class="seo-product-card"' in s, path
            assert s.count('rel="canonical"') == 1 and s.count('hreflang="ro"')==1 and s.count('hreflang="ru"')==1, path
            structured = re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)
            assert structured and json.loads(structured.group(1))['@graph'][0]['@type']=='CollectionPage', path
    gen=(root/'playspot-v29/generate.py').read_text(encoding='utf-8')
    assert gen.count('# P37: restore single-border category filters after V36 generator hook')==1
    assert (root/'playspot-v37.css').is_file() and (root/'playspot-v37.js').is_file()
    print('V37 validation passed: all 14 RO/RU category pages, single hero, dropdown, product links and SEO.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');a=p.parse_args()
    validate(Path(a.root).resolve())
