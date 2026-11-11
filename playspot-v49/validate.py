#!/usr/bin/env python3
"""V49 validation of canonical product URLs, schema, RO/RU pairing and local SEO."""
from __future__ import annotations
import argparse
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

SITE='https://playspotstore.online/'
CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')
NS={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','x':'http://www.w3.org/1999/xhtml'}
JSONLD=re.compile(r'<script type="application/ld\+json">(.*?)</script>',re.S)


def validate(root:Path):
    root=root.resolve()
    slugs=json.loads((root/'playspot-v49/slug-index.json').read_text(encoding='utf-8'))
    migrations=json.loads((root/'playspot-v49/old-to-new.json').read_text(encoding='utf-8'))
    assert set(slugs)==set(CATS)
    generator=(root/'playspot-v29/generate.py').read_text(encoding='utf-8')
    assert 'P49_CLEAN_PRODUCT_URL' in generator and 'productslug=p49_slug(cat,item)' in generator
    assert 'P48_STATIC_SEO_MENU_ONLY' in generator and 'P44_MOLDOVA_SEO_HOOK' in generator
    assert len(migrations)>=558,('Missing original URL map',len(migrations))
    for old,new in migrations.items():
        assert not (root/old).exists(),('Old long URL still present',old)
        assert (root/new).is_file(),('New product URL missing',new)
        assert not new.endswith(('-chisinau-moldova.html','-kishinev-moldova.html'))
    docs=ET.parse(root/'sitemap.xml').findall('s:url',NS)
    urls={}
    for node in docs:
        loc=node.find('s:loc',NS)
        assert loc is not None and loc.text.startswith(SITE)
        path=loc.text[len(SITE):]
        assert path not in urls,'Duplicate sitemap URL '+path
        urls[path]=node
        assert len(node.findall('x:link',NS))==3,('Missing sitemap hreflang',path)
        if path:assert (root/path).is_file(),('Sitemap references missing file',path)
    assert not (set(migrations)&set(urls)),('Old URL still in XML',set(migrations)&set(urls))
    assert set(migrations.values()).issubset(urls),'Missing new canonical URLs in XML'
    total=0
    product_pages=[]
    for cat in CATS:
        ro=json.loads((root/'data'/f'{cat}.json').read_text(encoding='utf-8'))
        ru=json.loads((root/'data'/f'{cat}_ru.json').read_text(encoding='utf-8'))
        a={str(p['id']):p for p in ro};b={str(p['id']):p for p in ru}
        assert set(a)==set(b)==set(slugs[cat])
        assert len(a)==len(ro)==len(ru)
        assert len(set(slugs[cat].values()))==len(a)
        total+=len(a)
        folder='console' if cat=='consoles' else cat
        for pid,item in a.items():
            name=slugs[cat][pid]
            assert name.endswith('.html') and re.fullmatch(r'[a-z0-9][a-z0-9-]*\.html',name)
            for lang,p in (('ro',item),('ru',b[pid])):
                prefix='ru/' if lang=='ru' else ''
                rel=f'{prefix}produse/{folder}/{name}'
                assert rel in urls,('Product missing from sitemap',rel)
                source=(root/rel).read_text(encoding='utf-8')
                product_pages.append(source)
                assert source.count('rel="canonical"')==1,(rel,'canonical')
                assert f'<link rel="canonical" href="{SITE}{rel}">' in source,rel
                assert '<h1>' in source and 'class="p42-editorial"' in source,rel
                assert 'p44-fulfilment' in source,('Local purchase info lost',rel)
                for code in ('ro','ru'):
                    target=f'{"ru/" if code=="ru" else ""}produse/{folder}/{name}'
                    assert f'hreflang="{code}" href="{SITE}{target}"' in source,(rel,code)
                    assert any(n.get('hreflang')==code and n.get('href')==SITE+target for n in urls[rel].findall('x:link',NS)),('XML alternate',rel,code)
                match=JSONLD.search(source)
                assert match,('Missing Product structured data',rel)
                graph=json.loads(match.group(1))['@graph']
                product=next(p for p in graph if p.get('@type')=='Product')
                assert product['sku']==pid and product['url']==SITE+rel,rel
                assert product['name']==p['title'] and product['description']==p['description'],('Product data changed',rel)
                assert 'aggregateRating' not in product and 'availability' not in product,rel
                assert '<meta http-equiv="refresh"' not in source,rel
                assert rel in (root/'seo/generated-paths.json').read_text(encoding='utf-8') if (root/'seo/generated-paths.json').is_file() else True
    assert len(urls)==2*total+18,('Unexpected sitemap count',len(urls),total)
    assert len(product_pages)==2*total
    for page,lang in [('index.html','ro'),('ru.html','ru')]:
        source=(root/page).read_text(encoding='utf-8')
        assert 'id="main-menu"' in source and 'class="p29-seo-links"' in source
        assert 'function openCategoryModal(' not in source,('Legacy menu reappeared',page)
        assert source.count('window.p29ProductSlugs=')==1
        m=re.search(r'window\.p29ProductSlugs=(\{.*?\});',source,re.S)
        assert m
        js=json.loads(m.group(1))
        for cat in CATS:
            key='console' if cat=='consoles' else cat
            assert js[key]==slugs[cat],(page,'JS slugmap',cat)
        for old in migrations:
            assert '/'+old not in source,('Legacy product URL in homepage',page,old)
    for file in ('sitemap.html','ru/sitemap.html','jocuri-video-chisinau-moldova.html','ru/videoigry-kishinev-moldova.html'):
        source=(root/file).read_text(encoding='utf-8')
        for old in migrations:
            assert '/'+old not in source,('Old link in HTML guide/sitemap',file,old)
    print(f'V49 VALID: {total} products; {2*total} canonical RO/RU pages; {len(urls)} sitemap URLs;'
          ' short slugs, correct Product JSON-LD, hreflang, local delivery, SEO navigation, no redirects')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.')
    args=p.parse_args();validate(Path(args.root))
