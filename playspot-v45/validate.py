#!/usr/bin/env python3
"""Validate all canonical geographic URLs, redirects, bilingual schema and copy."""
from __future__ import annotations
import argparse
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import migrate


def validate(root:Path, light:bool=False):
    root=root.resolve()
    mapping=migrate.routes(root)
    total_products=sum('produse/' in old for old in mapping)
    total_categories=sum('categorii/' in old for old in mapping)
    assert len(mapping)==total_products+total_categories and total_categories==14 and total_products>=558,(total_products,total_categories)
    assert len(set(mapping.values()))==len(mapping)
    original=set(mapping);target=set(mapping.values())
    assert original.isdisjoint(target)
    pages={}
    seen_meta={'ro':set(),'ru':set()}
    visible=set()
    for old,new in mapping.items():
        old_file=root/old;new_file=root/new
        assert old_file.is_file() and new_file.is_file(),(old,new)
        o=old_file.read_text(encoding='utf-8');s=new_file.read_text(encoding='utf-8')
        lang=migrate.lang_of(old)
        assert migrate.MARKER in o,(old,'legacy redirect missing')
        assert f'http-equiv="refresh" content="0;url=/{new}"' in o,old
        assert f'<link rel="canonical" href="{migrate.SITE}/{new}">' in o,old
        assert migrate.MARKER not in s,new
        assert s.count('rel="canonical"')==1,new
        assert f'rel="canonical" href="{migrate.SITE}/{new}"' in s,new
        assert '<meta name="robots" content="noindex"' not in s,new
        assert 'hreflang="ro"' in s and 'hreflang="ru"' in s,new
        old_ro=old.removeprefix('ru/')
        old_ru='ru/'+old_ro
        paired_ro=mapping.get(old_ro)
        paired_ru=mapping.get(old_ru)
        assert paired_ro and paired_ru,(old,'RO/RU pair missing')
        assert f'hreflang="ro" href="{migrate.SITE}/{paired_ro}"' in s,(new,'RO alternate')
        assert f'hreflang="ru" href="{migrate.SITE}/{paired_ru}"' in s,(new,'RU alternate')
        assert new.endswith('-'+migrate.PREFIX[lang]+'.html'),new
        assert 'playspot-v44.css' in s,new
        assert 'p37-integrated' in s if '/categorii/' in '/'+new else True
        if '/produse/' in '/'+new:
            sku=re.search(r'"sku"\s*:\s*"([^"]+)"',s)
            assert sku,('missing sku',new)
            cat=old.split('/')[-2]
            if cat=='console':cat='consoles'
            key=(cat,lang,sku.group(1))
            assert key not in pages,('duplicate canonical SKU',key)
            pages[key]=new
            item=next((x for x in json.loads((root/'data'/f'{cat}{"_ru" if lang=="ru" else ""}.json').read_text(encoding='utf-8')) if str(x['id'])==sku.group(1)),None)
            assert item is not None,('missing catalog id',key)
            desc=re.search(r'<p class="seo-detail-description">(.*?)</p>',s,re.S)
            assert desc and migrate.COPY_MARK in s,(key,'missing enhanced description')
            copy=html.unescape(desc.group(1))
            assert item['title'] in copy,(key,'title missing in visible description')
            assert item['description'] in copy,(key,'original synopsis missing')
            assert ('Chișinău' in copy if lang=='ro' else 'Кишинёв' in copy),(key,'local information missing')
            assert ('curier' in copy if lang=='ro' else 'курьер' in copy),(key,'courier information missing')
            assert s.count('class="p42-editorial"')==1,(key,'editorial reviews missing')
            assert s.count('class="p40-product-facts"')==1,(key,'SKU details missing')
            raw=s.split('<script type="application/ld+json">',1)[1].split('</script>',1)[0]
            schema=json.loads(raw)['@graph'][0]
            assert schema['sku']==sku.group(1) and schema['url']==migrate.SITE+'/'+new,key
            assert schema['description']==item['description'],key
            assert 'review' not in schema and 'aggregateRating' not in schema and 'availability' not in schema,key
            if 'offers' in schema:assert schema['offers']['url']==migrate.SITE+'/'+new,key
            meta=re.search(r'<meta name="description" content="([^"]+)"',s)
            assert meta,new
            mt=html.unescape(meta.group(1))
            assert 30<=len(mt)<=165,(new,len(mt))
            assert mt not in seen_meta[lang],(new,'duplicate meta description')
            seen_meta[lang].add(mt)
            visible.add(copy)
        else:
            assert '<h1>' in s and 'CollectionPage' in s,new
            assert 'p37-integrated' in s,new
    assert len(pages)==total_products,(len(pages),total_products)
    assert len(visible)>=total_products-8,(len(visible),total_products)
    # Canonical URLs and RO/RU hreflang pairs must agree with the sitemap.
    nodes=ET.parse(root/'sitemap.xml').findall(f'{{{migrate.NS}}}url')
    loc={n.findtext(f'{{{migrate.NS}}}loc') for n in nodes}
    assert len(nodes)==len(loc)==total_products+total_categories+4,(len(nodes),len(loc))
    for old,new in mapping.items():
        assert migrate.SITE+'/'+new in loc,new
        assert migrate.SITE+'/'+old not in loc,old
    backward={new:old for old,new in mapping.items()}
    for node in nodes:
        links=node.findall(f'{{{migrate.XNS}}}link')
        assert len(links)==3,'sitemap missing RO/RU/x-default'
        node_url=node.findtext(f'{{{migrate.NS}}}loc')
        current=node_url.removeprefix(migrate.SITE+'/')
        old_url=backward.get(current)
        for a in links:
            href=a.attrib['href']
            assert not any(href==migrate.SITE+'/'+x for x in mapping),'old legacy link in sitemap'
            if old_url and a.attrib['hreflang'] in ('ro','ru'):
                pair=old_url.removeprefix('ru/')
                if a.attrib['hreflang']=='ru':pair='ru/'+pair
                assert href==migrate.SITE+'/'+mapping[pair],(node_url,a.attrib['hreflang'],href)

    for home,lang in [('index.html','ro'),('ru.html','ru')]:
        src=(root/home).read_text(encoding='utf-8')
        assert 'id="catalog-seo"' in src and 'p29ProductSlugs' in src
        for old,new in mapping.items():
            if 'categorii/' in old and migrate.lang_of(old)==lang:
                assert '/'+new in src,(home,new)
        pat=re.search(r'window\.p29ProductSlugs=(\{.*?\});',src,re.S)
        if pat:
            slugs=json.loads(pat.group(1))
            count=0
            for old,new in mapping.items():
                if migrate.lang_of(old)!=lang or '/produse/' not in '/'+old:continue
                cat=old.split('/')[-2]
                count+=new.rsplit('/',1)[-1] in slugs.get(cat,{}).values()
            assert count>=267,(home,'homepage search links are stale',count)
    # See V44 landing pages and sitemap helper pages for preserved indexable links.
    for guide in ('jocuri-video-chisinau-moldova.html','ru/videoigry-kishinev-moldova.html','sitemap.html','ru/sitemap.html'):
        s=(root/guide).read_text(encoding='utf-8')
        assert 'categorii/' in s or guide.endswith('sitemap.html'),guide
    gen=(root/'playspot-v29/generate.py').read_text(encoding='utf-8')
    assert gen.count('P45_GEO_URL_HOOK')==1
    print('V45 VALID:',total_products//2,'products,',total_products,'RO/RU canonical product URLs,',total_categories,'canonical categories,',len(nodes),'sitemap URLs, legacy redirects, unique descriptions, hreflang, reviews, structured data')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.')
    args=ap.parse_args();validate(Path(args.root))
