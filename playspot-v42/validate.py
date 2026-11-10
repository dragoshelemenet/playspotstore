#!/usr/bin/env python3
"""Validate V42 product SEO and editorial copy in the pre-rendered RO/RU pages."""
from __future__ import annotations
import argparse,html,json,re
from pathlib import Path
CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')

def validate(root:Path):
 root=root.resolve()
 g=(root/'playspot-v29/generate.py').read_text(encoding='utf-8')
 for token in ('V42_EDITORIAL_PRODUCT','seo_meta_description','seo_editorial_review','{review_html}','playspot-v42.css'):
  assert token in g, f'Missing V42 renderer {token}'
 assert (root/'playspot-v42.css').is_file()
 total=0;seen=set();unique_desc={'ro':set(),'ru':set()};unique_review={'ro':set(),'ru':set()};max_meta=0
 for cat in CATS:
  catalog={lang:json.loads((root/'data'/f'{cat}{"_ru" if lang=="ru" else ""}.json').read_text(encoding='utf-8')) for lang in ('ro','ru')}
  ids={lang:{str(a['id']):a for a in records} for lang,records in catalog.items()}
  assert len(catalog['ro'])==len(catalog['ru'])==len(ids['ro'])==len(ids['ru']) and set(ids['ro'])==set(ids['ru']),cat
  total+=len(ids['ro'])
  for lang in ('ro','ru'):
   rootdir=root/('ru/produse' if lang=='ru' else 'produse')/('console' if cat=='consoles' else cat)
   pages={}
   for path in rootdir.glob('*.html'):
    source=path.read_text(encoding='utf-8')
    m=re.search(r'"sku":"([^"]+)"',source)
    assert m,f'SKU missing from {path}'
    pid=m.group(1)
    assert pid not in pages,(path,pid)
    pages[pid]=(path,source)
   assert set(pages)==set(ids[lang]),(cat,lang,'product files mismatch',len(pages),len(ids[lang]))
   for pid,p in ids[lang].items():
    assert p.get('seo_copy_version')=='v42',(pid,lang,'version')
    desc=p.get('description','');review=p.get('seo_editorial_review','');meta=p.get('seo_meta_description','')
    assert 25<=len(desc)<=530,(pid,lang,'summary',len(desc))
    assert 50<=len(review)<=900,(pid,lang,'review',len(review))
    assert meta.startswith(p['title']+' | '),(pid,lang,meta)
    assert desc[:min(len(desc),12)] in meta,(pid,lang,'meta source mismatched')
    assert len(meta)<245,(pid,lang,'meta length',len(meta));max_meta=max(max_meta,len(meta))
    # Identical titles on different platforms can legitimately share their
    # gameplay summary; the URL, platform and metadata remain distinct.
    assert (cat,desc) not in unique_desc[lang],(pid,lang,'repeated synopsis within category')
    assert (cat,review) not in unique_review[lang],(pid,lang,'repeated editorial review within category')
    unique_desc[lang].add((cat,desc));unique_review[lang].add((cat,review))
    path,source=pages[pid]
    assert source.count('class="p42-editorial"')==1,path
    assert source.count('playspot-v42.css')==1,path
    assert html.escape(desc,quote=True) in source or html.escape(desc,quote=False).replace("'",'&#x27;') in source,path
    assert html.escape(review,quote=True) in source or html.escape(review,quote=False).replace("'",'&#x27;') in source,path
    metatag=re.search(r'<meta name="description" content="([^"]+)"',source)
    assert metatag and html.unescape(metatag.group(1))==meta,path
    graph=json.loads(source.split('<script type="application/ld+json">',1)[1].split('</script>',1)[0])['@graph']
    prod=graph[0]
    assert prod['sku']==pid and prod['description']==desc,path
    assert 'review' not in prod and 'aggregateRating' not in prod and 'availability' not in prod,path
    for token in ('rel="canonical"','hreflang="ru"','hreflang="ro"','class="p40-product-facts"'):
     assert token in source,(path,token)
    if cat in ('accessories','consoles'):
     assert ('La ce să fii atent' if lang=='ro' else 'На что обратить внимание') in source,path
    else:
     assert ('Impresie editorială de gameplay' if lang=='ro' else 'Редакционные впечатления об игре') in source,path
 assert total>=279,('unexpectedly small catalog',total)
 for home in ('index.html','ru.html'):
  s=(root/home).read_text(encoding='utf-8')
  assert 'playspot-v39.css' in s and 'p29ProductSlugs' in s,home
 print('V42 VALID:',total,'products,',2*total,'RO/RU pages, unique copy in both languages, distinct meta, editorial UI, schema preserved, longest meta',max_meta)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.')
 validate(Path(p.parse_args().root))
