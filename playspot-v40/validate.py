#!/usr/bin/env python3
"""Verify product copy, internal catalog IDs and crawled RO/RU structured data."""
from __future__ import annotations
import argparse
import html
import json
import re
from pathlib import Path

CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')
SITE='https://playspotstore.online'


def validate(root:Path)->None:
    root=root.resolve()
    generator=(root/'playspot-v29/generate.py').read_text(encoding='utf-8')
    for token in ('p40-product-facts', "'sku':str(ro_item['id'])",'playspot-v40.css'):
        assert token in generator, f'V40 generator hook absent: {token}'
    assert (root/'playspot-v40.css').is_file(), 'V40 product CSS missing'
    product_count=0
    seenids=set()
    metabodies=set()
    for cat in CATS:
        ros=json.loads((root/'data'/f'{cat}.json').read_text(encoding='utf-8'))
        rus=json.loads((root/'data'/f'{cat}_ru.json').read_text(encoding='utf-8'))
        ruid={str(p['id']):p for p in rus}
        assert len(ros)==len(rus)==len(ruid) and {str(p['id']) for p in ros}==set(ruid),cat
        product_count+=len(ros)
        for ro in ros:
            pid=str(ro['id'])
            assert pid not in seenids, 'Duplicate ID '+pid
            seenids.add(pid)
            for lang,p in [('ro',ro),('ru',ruid[pid])]:
                desc=p.get('description','')
                assert isinstance(desc,str) and len(desc.strip())>=12, f'Empty description: {pid}/{lang}'
                assert not desc.lower().startswith(('adăugat recent. confirmă starea','новое поступление. уточняйте состояние')),f'Generic copy: {pid}/{lang}'
                # The permalink is retained; identify it by the stable internal catalog ID.
                directory = root/('ru/produse' if lang=='ru' else 'produse')/('console' if cat=='consoles' else cat)
                candidates=list(directory.glob('*.html'))
                matches=[]
                for path in candidates:
                    # The structured data is in original HTML, not JS-injected.
                    text=path.read_text(encoding='utf-8')
                    if f'"sku":"{pid}"' in text:matches.append((path,text))
                assert len(matches)==1,f'Product page not found uniquely for {pid}/{lang}: {len(matches)}'
                path,content=matches[0]
                assert content.count('rel="canonical"')==1,path
                assert content.count('hreflang="ro"')==1 and content.count('hreflang="ru"')==1,path
                assert content.count('class="p40-product-facts"')==1,path
                assert content.count('playspot-v40.css')==1,path
                assert html.escape(desc,quote=True).replace('&#x27;','&#x27;') in content or html.escape(desc,quote=False).replace("'",'&#x27;') in content, f'Description not in HTML: {path}'
                raw=content.split('<script type="application/ld+json">',1)[1].split('</script>',1)[0]
                graph=json.loads(raw)['@graph']
                product=graph[0]
                assert product['@type']=='Product' and product['sku']==pid and product['description']==desc, path
                assert 'availability' not in product and 'aggregateRating' not in product,path
                meta=re.search(r'<meta name="description" content="([^"]+)"',content)
                assert meta, path
                metatext=html.unescape(meta.group(1))
                assert metatext.startswith(f"{p['title']} | {product['category']}: "), f'Meta must begin with product and category: {path}'
                assert desc[:min(12,len(desc))] in metatext, f'Meta must include real product copy: {path}'
                if (lang,metatext) in metabodies: raise AssertionError('Repeated full meta description: '+str(path))
                metabodies.add((lang,metatext))
    assert product_count>=279, f'Unexpected product count {product_count}'
    for name in ('index.html','ru.html'):
        h=(root/name).read_text(encoding='utf-8')
        assert 'playspot-v39.css' in h and 'p29ProductSlugs' in h, f'Homepage SEO/animation missing {name}'
    print(f'V40 VALID: {product_count} products / {product_count*2} RO+RU pages, distinct metadata, rich data, SEO links, stable catalog IDs')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='.')
    validate(Path(parser.parse_args().root))
