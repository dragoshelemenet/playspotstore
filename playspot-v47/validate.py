#!/usr/bin/env python3
"""V47 strict validation: stable original catalog URLs; no redirect pages."""
from __future__ import annotations
import argparse,html,json,re,xml.etree.ElementTree as ET
from pathlib import Path

SITE='https://playspotstore.online/'
NS={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','x':'http://www.w3.org/1999/xhtml'}
CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')

def validate(root:Path):
    import restore
    root=root.resolve();mapping=restore.readmap(root)
    gen=(root/'playspot-v29/generate.py').read_text(encoding='utf-8')
    assert 'P45_GEO_URL_HOOK' not in gen and 'P46_NATURAL_MIX_HOOK' not in gen
    assert restore.DESCRIPTION_REPLACE in gen
    assert 'P45_GEO_VALIDATOR' not in (root/'playspot-v44/validate.py').read_text(encoding='utf-8')
    sitemap=ET.parse(root/'sitemap.xml').getroot()
    nodes=sitemap.findall('s:url',NS)
    expected=2+2+len(mapping)
    assert len(nodes)==expected,(len(nodes),expected)
    xml_paths=set()
    for node in nodes:
        loc=node.find('s:loc',NS)
        assert loc is not None and loc.text.startswith(SITE)
        path=loc.text[len(SITE):]
        assert path not in xml_paths,path
        xml_paths.add(path)
        assert len(node.findall('x:link',NS))==3,path
        assert not path.endswith(('-chisinau-moldova.html','-kishinev-moldova.html')) or path in ('jocuri-video-chisinau-moldova.html','ru/videoigry-kishinev-moldova.html')
    assert set(mapping).issubset(xml_paths)
    assert set(mapping.values()).isdisjoint(xml_paths)
    assert '' in xml_paths and 'ru.html' in xml_paths
    for old,new in mapping.items():
        assert (root/old).is_file(),old
        assert not (root/new).exists(),'Geographic file still present: '+new
        s=(root/old).read_text(encoding='utf-8')
        assert '<meta http-equiv="refresh"' not in s and restore.MARKER not in s,old
        assert s.count('rel="canonical"')==1,old
        assert f'<link rel="canonical" href="{SITE}{old}">' in s,old
        assert f'"url":"{SITE}{old}"' in s or '"@type":"CollectionPage"' in s,old
        assert 'hreflang="ro"' in s and 'hreflang="ru"' in s,old
        assert f'/{new}' not in s,old
        if '/produse/' in '/'+old:
            cat=old.split('/')[-2];cat='consoles' if cat=='console' else cat
            lang='ru' if old.startswith('ru/') else 'ro'
            obj=json.loads(s.split('<script type="application/ld+json">',1)[1].split('</script>',1)[0])['@graph'][0]
            assert obj['@type']=='Product' and obj['sku'],old
            data=json.loads((root/'data'/f'{cat}{"_ru" if lang=="ru" else ""}.json').read_text(encoding='utf-8'))
            item=next((p for p in data if str(p['id'])==str(obj['sku'])),None)
            assert item is not None,old
            local=item['seo_local_description']
            assert len(local)>25 and html.escape(local,quote=True) in s,old
            assert 'p42-editorial' in s and 'p44-fulfilment' in s,old
    for page in ('index.html','ru.html','sitemap.html','ru/sitemap.html','jocuri-video-chisinau-moldova.html','ru/videoigry-kishinev-moldova.html'):
        source=(root/page).read_text(encoding='utf-8')
        for old,new in mapping.items():
            assert '/'+new not in source,(page,new)
    print(f'V47 VALID: {len(mapping)} original canonical catalog URLs; no redirects; {len(nodes)} sitemap URLs; source data and RO/RU links verified.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.')
    validate(Path(p.parse_args().root))
