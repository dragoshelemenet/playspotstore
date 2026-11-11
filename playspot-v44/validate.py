#!/usr/bin/env python3
"""Validate V44 crawlable local SEO without making unverifiable commerce claims."""
from __future__ import annotations
import argparse
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')
PLATFORM={'ps2':'PS2','ps4':'PS4','ps5':'PS5','nintendo':'Nintendo','xbox':'Xbox','consoles':'PlayStation','accessories':'gaming'}
START='<!-- P44 MOLDOVA FULFILMENT START -->'
END='<!-- P44 MOLDOVA FULFILMENT END -->'


def metadata(s:str,path:Path)->tuple[str,str]:
 head=s.split('</head>',1)[0]
 tm=re.findall(r'<title>(.*?)</title>',head,flags=re.S|re.I)
 mm=re.findall(r'<meta name="description" content="([^"]+)"',head,flags=re.I)
 assert len(tm)==len(mm)==1,(path,'missing or repeated title/description')
 title,desc=html.unescape(tm[0]),html.unescape(mm[0])
 assert 4<len(title)<165 and 30<len(desc)<=165,(path,len(title),len(desc))
 assert head.count('playspot-v44.css')==1,(path,'missing CSS')
 assert 'rel="canonical"' in head and 'hreflang="ro"' in head and 'hreflang="ru"' in head,(path,'broken canonical/hreflang')
 assert s.count(START)==s.count(END)==1,(path,'missing/duplicated V44 content')
 assert '<meta name="robots" content="noindex"' not in head,(path,'noindex')
 return title,desc


def verify(root:Path)->None:
 root=root.resolve()
 gen=(root/'playspot-v29/generate.py').read_text(encoding='utf-8')
 assert gen.count('P44_MOLDOVA_SEO_HOOK')==1,'V44 persistence hook missing'
 assert (root/'playspot-v44.css').is_file(),'V44 CSS not deployed'
 for path,lang in ((root/'index.html','ro'),(root/'ru.html','ru')):
  s=path.read_text(encoding='utf-8');title,desc=metadata(s,path)
  assert 'catalog-seo' in s and 'class="category-deck"' in s,path
  assert 'id="livrare-moldova"' in s,path
  assert ('Chișinău' in s if lang=='ro' else 'Кишинёве' in s),path
  assert ('second-hand' in s if lang=='ro' else 'б/у' in s),path
  assert ('Moldova' in desc if lang=='ro' else 'Молдове' in desc),path
 total=0;seen_meta={'ro':set(),'ru':set()};seen_titles={'ro':set(),'ru':set()}
 for cat in CATS:
  for lang in ('ro','ru'):
   base=root/('ru' if lang=='ru' else '')
   cp=base/'categorii'/f'{cat}.html';s=cp.read_text(encoding='utf-8')
   title,desc=metadata(s,cp)
   assert 'p37-integrated' in s and 'P36 CATEGORY FILTER START' in s,(cp,'V37 filter changed')
   assert ('Chișinău' in title if lang=='ro' else 'Кишинёве' in title),cp
   assert ('Moldova' in desc if lang=='ro' else 'Молдове' in desc),cp
   assert 'id="livrare-moldova"' not in s and ('href="/jocuri-video-chisinau-moldova.html"' if lang=='ro' else 'href="/ru/videoigry-kishinev-moldova.html"') in s,cp
   cat_data=json.loads((root/'data'/f'{cat}{"_ru" if lang=="ru" else ""}.json').read_text(encoding='utf-8'))
   products={str(p['id']):p for p in cat_data}
   directory=base/'produse'/('console' if cat=='consoles' else cat)
   pages=list(directory.glob('*.html'))
   assert len(pages)==len(products),(directory,len(pages),len(products))
   for path in pages:
    s=path.read_text(encoding='utf-8');title,desc=metadata(s,path)
    match=re.search(r'"sku"\s*:\s*"([^"]+)"',s)
    assert match and match.group(1) in products,path
    p=products.pop(match.group(1))
    assert p['title'] in title,(path,p['title'],title)
    if cat!='accessories':assert PLATFORM[cat].casefold() in title.casefold(),path
    assert ('Chișinău' in desc if lang=='ro' else 'Кишинёве' in desc),path
    assert ('Moldova' in desc if lang=='ro' else 'Молдове' in desc),path
    assert 'p42-editorial' in s and 'p40-product-facts' in s,path
    assert ('href="/jocuri-video-chisinau-moldova.html"' if lang=='ro' else 'href="/ru/videoigry-kishinev-moldova.html"') in s,path
    assert desc not in seen_meta[lang],(path,'nonunique description')
    seen_meta[lang].add(desc)
    # A same-named title can occur on another platform, but paths always unique.
    assert title not in seen_titles[lang],(path,'duplicate title')
    seen_titles[lang].add(title)
    schema_raw=s.split('<script type="application/ld+json">',1)[1].split('</script>',1)[0]
    data=json.loads(schema_raw)['@graph'][0]
    assert data['@type']=='Product' and data['sku']==match.group(1),path
    assert 'aggregateRating' not in data and 'review' not in data and 'availability' not in data,path
    total+=(lang=='ro')
   assert not products,(cat,lang,'missing pages for some IDs',len(products))
 assert total>=200,('catalog unexpectedly small',total)
 for rel in ('jocuri-video-chisinau-moldova.html','ru/videoigry-kishinev-moldova.html'):
  page=root/rel
  s=page.read_text(encoding='utf-8')
  assert f'<link rel="canonical" href="https://playspotstore.online/{rel}">' in s,rel
  assert '<h1>' in s and 'hreflang="ro"' in s and 'hreflang="ru"' in s,rel
  assert 'PlaySpotStore' in s and 'robots" content="index,follow' in s,rel
  assert s.count('produse/')>=6 and s.count('/categorii/')==7,rel
 xml=ET.parse(root/'sitemap.xml').getroot()
 ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
 links={n.findtext(ns+'loc') for n in xml.findall(ns+'url')}
 assert len(links)==total*2+14+4,(len(links),total)
 for rel in ('jocuri-video-chisinau-moldova.html','ru/videoigry-kishinev-moldova.html'):
  assert 'https://playspotstore.online/'+rel in links,rel
 for path in (root/'sitemap.html',root/'ru/sitemap.html'):
  s=path.read_text(encoding='utf-8')
  assert ('jocuri-video-chisinau-moldova.html' if path.name=='sitemap.html' and 'ru' not in path.parts else 'ru/videoigry-kishinev-moldova.html') in s,path
 print(f'V44 VALID: {total} products, {2*total} product pages, 14 category pages, 2 homepages, 2 original local-service pages, unique metadata, unchanged schema/filters and RO/RU crawlability.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.')
 verify(Path(p.parse_args().root))
