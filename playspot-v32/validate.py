#!/usr/bin/env python3
"""SEO bot-sitemap + HTML sitemap consistency tests."""
from __future__ import annotations
import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

SITE='https://playspotstore.online'
NS={'s':'http://www.sitemaps.org/schemas/sitemap/0.9', 'x':'http://www.w3.org/1999/xhtml'}

def check(root):
    root=root.resolve()
    xml=(root/'sitemap.xml').read_text(encoding='utf-8')
    assert 'xml-stylesheet' not in xml, 'XSLT stylesheet still present in XML'
    assert '<?xml' in xml and '<urlset' in xml
    assert not (root/'sitemap.xsl').exists(), 'Old root sitemap.xsl should be removed'
    doc=ET.fromstring(xml)
    assert doc.tag.endswith('}urlset'), 'XML root is not urlset'
    locs=[]
    for n in doc.findall('s:url',NS):
        loc=n.find('s:loc',NS)
        assert loc is not None and loc.text, 'Missing URL <loc>'
        assert loc.text.startswith(SITE+'/'), 'Sitemap uses wrong domain'
        assert not urlsplit(loc.text).query, 'Sitemap URL has query string'
        path=urlsplit(loc.text).path.lstrip('/')
        assert not path or (root/path).is_file(),f'Missing HTML file: {path}'
        alternates=n.findall('x:link',NS)
        assert len(alternates)==3,f'RO/RU/x-default links missing: {path}'
        locs.append(path)
    assert len(locs)==len(set(locs)),'Duplicate sitemap URLs'
    for lang,file in (('ro','sitemap.html'),('ru','ru/sitemap.html')):
        s=(root/file).read_text(encoding='utf-8')
        hrefs=set(re.findall(r'<a\b[^>]*\bhref="([^"]+)"',s))
        relevant=[v for v in locs if (v.startswith('ru/') or v=='ru.html') == (lang=='ru')]
        assert len(relevant)>0
        missing=[v for v in relevant if ('/'+v if v else '/') not in hrefs]
        assert not missing,f'{lang} HTML sitemap missing {len(missing)} URLs: {missing[:2]}'
        assert '<script' not in s,'Sitemap HTML must be crawlable without JS'
        assert f'<html lang="{lang}">' in s
        assert f'{SITE}/sitemap' in s or f'{SITE}/ru/sitemap' in s
    assert (root/'robots.txt').read_text(encoding='utf-8').splitlines().count('Sitemap: '+SITE+'/sitemap.xml')==1
    src=(root/'playspot-v29/generate.py').read_text(encoding='utf-8')
    assert 'xml-stylesheet' not in src,'Generator would restore browser XSLT'
    assert 'playspot-v32' in src and 'human_sitemap.py' in src
    for lang,file in (('ro','index.html'),('ru','ru.html')):
        s=(root/file).read_text(encoding='utf-8')
        want='/ru/sitemap.html' if lang=='ru' else '/sitemap.html'
        assert f'href="{want}"' in s,f'Homepage missing sitemap link: {file}'
    for file in ['categorii/ps4.html','ru/categorii/ps4.html','produse/ps4','ru/produse/ps4']:
        p=root/file
        if p.is_file():
            assert 'href="/sitemap.html"' in p.read_text(encoding='utf-8') or 'href="/ru/sitemap.html"' in p.read_text(encoding='utf-8')
    print(f'✅ V32: {len(locs)} XML URLs; sitemap.xml clean of XSLT; RO/RU plain-HTML sitemaps; no broken sitemap links')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='.')
    try:check(Path(parser.parse_args().root))
    except (AssertionError,ValueError,ET.ParseError,FileNotFoundError) as e:
        raise SystemExit(f'V32 validation failed: {e}')
