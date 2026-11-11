#!/usr/bin/env python3
"""Check deterministic V46 phrasing without introducing URL/indexing changes."""
from __future__ import annotations
import argparse,html,json,re,sys
from pathlib import Path
from mix import CATS, COMMENT, START, END, GUIDE, assemble, aside, category_aside, page_map

SITE='https://playspotstore.online'

def check(root:Path):
    root=root.resolve();map_paths=page_map(root)
    gen=(root/'playspot-v29/generate.py').read_text(encoding='utf-8')
    assert gen.count('P46_NATURAL_MIX_HOOK')==1,'V46 regeneration hook absent or duplicated'
    assert gen.index('P45_GEO_URL_HOOK')<gen.index('P46_NATURAL_MIX_HOOK'),'V46 must run after V45'
    variations={'ro':set(),'ru':set()};anchors={'ro':set(),'ru':set()};matched=0;cat_count=0
    for category in CATS:
        for lang in ('ro','ru'):
            records=json.loads((root/'data'/f'{category}{"_ru" if lang=="ru" else ""}.json').read_text(encoding='utf-8'))
            prefix='ru/' if lang=='ru' else ''
            for item in records:
                pid=str(item['id']);expected=assemble(pid,item['title'],category,lang,item['description'])
                # The SKU is the stable mapping between actual catalog and canonical page.
                old_routes=[(o,n) for o,n in map_paths.items() if o.startswith(prefix+'produse/'+('console' if category=='consoles' else category)+'/')]
                matches=[]
                for old,new in old_routes:
                    s=(root/new).read_text(encoding='utf-8')
                    if f'"sku":"{pid}"' in s:matches.append((old,new,s))
                assert len(matches)==1,(pid,lang,'canonical SKU mapping',len(matches))
                old,new,s=matches[0]
                assert COMMENT in s and s.count(COMMENT)==1,(pid,'V45 copy marker')
                ms=re.findall(r'<p class="seo-detail-description">(.*?)</p>',s,re.S)
                assert len(ms)==1,(pid,'description count')
                visible=html.unescape(ms[0]); assert visible==expected,(pid,lang,'unexpected visible copy')
                assert item['title'] in visible and item['description'] in visible,(pid,lang,'catalog facts missing')
                assert ('Chișinău' in visible if lang=='ro' else 'Кишинёв' in visible),(pid,'fulfilment locale')
                assert ('curier' in visible if lang=='ro' else 'курьер' in visible),(pid,'courier')
                assert s.count(START)==s.count(END)==1,(pid,'V44 block')
                section=s.split(START,1)[1].split(END,1)[0]
                assert aside(pid,lang) in section,(pid,'order advice mismatch')
                guide=GUIDE[lang]
                am=re.search(r'<a href="'+re.escape(guide)+r'">([^<]+)</a>',section)
                assert am,(pid,'guide link')
                anchors[lang].add(html.unescape(am.group(1)))
                assert s.count('rel="canonical"')==1,(pid,'canonical count')
                assert f'href="{SITE}/{new}"' in s,(pid,'canonical path change')
                assert 'hreflang="ro"' in s and 'hreflang="ru"' in s,(pid,'hreflang absent')
                assert s.count('class="p42-editorial"')==1,(pid,'editorial content removed')
                assert '"availability"' not in s,(pid,'unverified stock status')
                assert '<meta name="robots" content="noindex"' not in s,(pid,'unexpected noindex')
                assert (root/old).is_file(),(pid,'legacy URL removed')
                variations[lang].add(visible)
                matched+=1
            old_cat=prefix+'categorii/'+category+'.html';new_cat=map_paths[old_cat]
            page=(root/new_cat).read_text(encoding='utf-8')
            expected_section=category_aside(category,lang)
            assert expected_section in page,(old_cat,'category link variation')
            assert page.count('p37-integrated')>=1,(old_cat,'category search missing')
            cat_count+=1
    assert matched>=558 and cat_count==14,(matched,cat_count)
    assert len(variations['ro'])>=270 and len(variations['ru'])>=270,('copy variety', {k:len(v) for k,v in variations.items()})
    assert len(anchors['ro'])>=8 and len(anchors['ru'])>=8,('anchor variety',{k:len(v) for k,v in anchors.items()})
    print('V46 VALID:',matched,'RO/RU products,',cat_count,'categories; natural stable copy, varied link labels, unchanged URL mapping and technical SEO.')
    print('V46 diversity: distinct visible copy',len(variations['ro']),len(variations['ru']),'distinct delivery link labels',len(anchors['ro']),len(anchors['ru']))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.')
    try:check(Path(p.parse_args().root))
    except (AssertionError,ValueError,KeyError,OSError) as e:
        print('V46 validation failed:',e,file=sys.stderr);sys.exit(1)
