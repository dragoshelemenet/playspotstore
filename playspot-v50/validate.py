#!/usr/bin/env python3
"""Checks every V50 product page and idempotent data/meta/image improvements."""
from __future__ import annotations
import argparse
import html
import json
import re
from pathlib import Path
import quality


def validate(root:Path)->None:
    root=root.resolve()
    generator=(root/'playspot-v29/generate.py').read_text(encoding='utf-8')
    assert generator.count('P50_SEO_QUALITY_HOOK')==1
    slugs=json.loads((root/'playspot-v49/slug-index.json').read_text(encoding='utf-8'))
    total=0
    for cat in quality.CATS:
        for lang in ('ro','ru'):
            fp=root/'data'/f'{cat}{"_ru" if lang=="ru" else ""}.json'
            items=json.loads(fp.read_text(encoding='utf-8'))
            for p in items:
                meta=quality.make_meta(p,cat,lang)
                assert p['seo_meta_description']==meta,(cat,lang,p['id'])
                folder='console' if cat=='consoles' else cat
                rel=Path('ru/produse' if lang=='ru' else 'produse')/folder/slugs[cat][str(p['id'])]
                s=(root/rel).read_text(encoding='utf-8')
                m=re.search(r'<meta name="description" content="([^"]+)"',s)
                assert m and html.unescape(m.group(1))==meta,(str(rel),'meta')
                assert len(meta)<=quality.META_LIMIT,(rel,'meta length')
                assert 'seo-detail-description' in s and 'p42-editorial' in s and 'p44-fulfilment' in s,rel
                a=quality.image_alt(p,cat,lang)
                image=re.search(r'<div class="seo-detail-image"><img\b[^>]*?\balt="([^"]*)"',s)
                assert image and html.unescape(image.group(1))==a,(rel,'image alt')
                if lang=='ro':total+=1
            catpage=root/('ru/categorii' if lang=='ru' else 'categorii')/f'{cat}.html'
            markup=catpage.read_text(encoding='utf-8')
            for p in items:
                assert markup.count('alt="'+html.escape(quality.image_alt(p,cat,lang),quote=True)+'"')==1,(cat,lang,p['id'])
    assert total>=279,total
    # Re-running the updater must not change already optimized HTML or data.
    changes,counts=quality.plan(root)
    assert not changes,('V50 not repeat-safe',counts)
    print(f'V50 VALID: {total} products, {2*total} product pages; descriptive image alts and metadata; safe repeated execution.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');a=p.parse_args()
    validate(Path(a.root))
