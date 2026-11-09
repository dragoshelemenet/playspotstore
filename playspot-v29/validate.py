#!/usr/bin/env python3
"""Validate the generated sitemap, canonical URLs, hreflang, and structured data before publishing."""
import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SITE='https://playspotstore.online/'
NS={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','x':'http://www.w3.org/1999/xhtml'}
CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')

def run(root):
    count=sum(len(json.loads((root/'data'/f'{cat}.json').read_text(encoding='utf-8'))) for cat in CATS)
    expected=count*2+len(CATS)*2+2
    urls=ET.parse(root/'sitemap.xml').findall('.//s:url',NS)
    assert len(urls)==expected,f'Expected {expected} URLs, found {len(urls)}'
    got=set()
    for node in urls:
        loc=node.find('s:loc',NS)
        assert loc is not None and loc.text.startswith(SITE),'Unexpected sitemap domain'
        path=loc.text[len(SITE):]
        assert path not in got,'Duplicate URL in sitemap'
        got.add(path)
        if path: assert (root/path).is_file(),f'Missing URL target: {path}'
        assert len(node.findall('x:link',NS))==3,f'Missing hreflang: {path}'
        if path.endswith('.html') and ('categorii/' in path or 'produse/' in path):
            s=(root/path).read_text(encoding='utf-8')
            assert s.count('rel="canonical"')==1, f'Multiple canonical tags: {path}'
            assert f'href="{loc.text}"' in s,f'Wrong canonical: {path}'
            assert '<h1>' in s and '<script type="application/ld+json">' in s, f'Missing content: {path}'
            raw=s.split('<script type="application/ld+json">',1)[1].split('</script>',1)[0]
            graph=json.loads(raw)['@graph']
            if 'produse/' in path:
                p=graph[0]
                assert p['@type']=='Product',f'Wrong schema: {path}'
                assert 'availability' not in p,f'Fabricated inventory status: {path}'
                if 'offers' in p:
                    offer=p['offers']
                    assert offer['priceCurrency']=='MDL' and isinstance(offer['price'],(int,float)) and offer['price']>0
            else:assert graph[0]['@type']=='CollectionPage'
    for path in ('index.html','ru.html'):
        s=(root/path).read_text(encoding='utf-8')
        assert s.count('rel="canonical"')==1,f'Multiple canonical tags: {path}'
        assert 'playstationspot.store' not in s,f'Old domain in homepage: {path}'
        assert 'id="catalog-seo"' in s and 'window.p29ProductSlugs=' in s,f'No crawlable catalog: {path}'
    robots=(root/'robots.txt').read_text(encoding='utf-8')
    assert SITE+'sitemap.xml' in robots and 'Allow: /' in robots
    assert (root/'seo/site.css').exists()
    print(f'✅ Verified {count} catalog products, {len(urls)} sitemap URLs, canonical/hreflang/JSON-LD, robots.txt')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='.')
    args=parser.parse_args()
    try:run(Path(args.root).resolve())
    except (AssertionError,ValueError,ET.ParseError,KeyError,FileNotFoundError,TypeError) as exc:
        print('SEO validation failed:',exc,file=sys.stderr)
        sys.exit(1)
