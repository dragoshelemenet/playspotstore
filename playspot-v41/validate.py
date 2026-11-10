#!/usr/bin/env python3
"""V41: validate all 279 RO/RU long descriptions and generated SEO pages."""
from __future__ import annotations
import argparse, html, json, re, sys
from pathlib import Path
CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')

def run(root):
    root=root.resolve()
    total=0; unique_ro=set();unique_ru=set();minro=1000;minru=1000;maxro=0;maxru=0
    for cat in CATS:
        ro=json.loads((root/'data'/f'{cat}.json').read_text(encoding='utf8'))
        ru=json.loads((root/'data'/f'{cat}_ru.json').read_text(encoding='utf8'))
        ru_map={str(x['id']):x for x in ru}
        assert len(ro)==len(ru_map)==len(ru),cat
        assert set(ru_map)=={str(x['id']) for x in ro},cat
        total+=len(ro)
        for item in ro:
            ru_item=ru_map[str(item['id'])]
            for lang,prod in [('ro',item),('ru',ru_item)]:
                assert prod.get('seo_copy_version')=='v41',(cat,lang,item['id'])
                desc=prod['description'];wordcount=len(desc.split())
                assert 78<=wordcount<=155,(item['id'],lang,'words',wordcount)
                assert not desc.lower().startswith(('adăugat recent. confirm','новое поступление. уточ')),item['id']
                assert len(set(desc.split()))>20,(item['id'],lang,'content variety')
                # Distinct product SEO pages are pre-rendered in HTML and structured data.
                slug_dir=root/('ru/produse/' if lang=='ru' else 'produse/')/('console' if cat=='consoles' else cat)
                hits=[]
                for fp in slug_dir.glob('*.html'):
                    data=fp.read_text(encoding='utf8')
                    if '"sku":"'+str(item['id'])+'"' in data:hits.append((fp,data))
                assert len(hits)==1,(item['id'],lang,'product URL count',len(hits))
                fp,contents=hits[0]
                schema=json.loads(contents.split('<script type="application/ld+json">',1)[1].split('</script>',1)[0])['@graph'][0]
                assert schema['@type']=='Product' and schema['description']==desc,fp
                assert schema['sku']==str(item['id']),fp
                assert 'availability' not in schema and 'aggregateRating' not in schema,fp
                assert 'rel="canonical"' in contents and 'hreflang="ru"' in contents and 'hreflang="ro"' in contents,fp
                assert html.escape(desc,quote=True) in contents or html.escape(desc,quote=False).replace("'",'&#x27;') in contents,fp
                assert 'p40-product-facts' in contents,fp
                if lang=='ro':minro=min(minro,wordcount);maxro=max(maxro,wordcount);unique_ro.add(desc)
                else:minru=min(minru,wordcount);maxru=max(maxru,wordcount);unique_ru.add(desc)
    assert total>=279,('Unexpected inventory size',total)
    assert len(unique_ro)>=180 and len(unique_ru)>=180,('Insufficient variation',len(unique_ro),len(unique_ru))
    print(f'V41 VALID: {total} products, {total*2} SEO pages; RO words {minro}-{maxro}, RU words {minru}-{maxru}; unique RO/RU {len(unique_ro)}/{len(unique_ru)}')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.')
 try:run(Path(p.parse_args().root))
 except (AssertionError, ValueError, TypeError, KeyError, OSError) as e:
    print('V41 VALIDATION FAILED:',e,file=sys.stderr);sys.exit(1)
