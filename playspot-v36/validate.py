#!/usr/bin/env python3
"""Validate the V36 generated category UI, SEO links and no duplicated assets."""
import argparse
import json
import re
from pathlib import Path
from apply import CATS,START,END


def validate(root):
    for lang,prefix in [('ro','categorii'),('ru','ru/categorii')]:
        for cat in CATS:
            path=root/prefix/(cat+'.html')
            s=path.read_text(encoding='utf-8')
            assert s.count(START)==s.count(END)==1, f'{path}: duplicate V36 widgets'
            assert s.count('playspot-v36.css')==s.count('playspot-v36.js')==1,f'{path}: duplicate/missing assets'
            assert '<p>Descoperă produsele PlaySpotStore din categoria' not in s, f'{path}: RO boilerplate shown'
            assert '<p>Посмотрите товары PlaySpotStore в категории' not in s, f'{path}: RU boilerplate shown'
            for attr in ('data-p36-search','data-p36-min','data-p36-max','data-p36-sort','data-p36-new','data-p36-priced','data-p36-count','data-p36-reset'):
                assert attr in s, f'{path}: missing {attr}'
            count=len(re.findall(r'<article class="seo-product-card">',s))
            assert count>0, f'{path}: product cards missing'
            assert len(re.findall(r'<a href="/(?:ru/)?produse/',s))>=count, f'{path}: individual product links lost'
            assert s.count('rel="canonical"')==1 and 'hreflang="ro"' in s and 'hreflang="ru"' in s
            ld=re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)
            assert ld and json.loads(ld.group(1))['@graph'][0]['@type']=='CollectionPage'
    source=(root/'playspot-v29'/'generate.py').read_text(encoding='utf-8')
    assert source.count('# P36: keep search filters after each catalog regeneration')==1
    print('V36 VALIDATED: 14 category pages, RO/RU UI, no boilerplate, product links and generator persistence.')

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',default='.');args=a.parse_args()
    validate(Path(args.root))
