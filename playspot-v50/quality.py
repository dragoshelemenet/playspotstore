#!/usr/bin/env python3
"""PlaySpotStore V50: human-readable product meta descriptions + descriptive images.

No URLs, product conditions, pricing, JSON-LD, or indexability directives changed.
Deterministic and repeat-safe; generator integration restores fixes after rebuild.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

CATS = ('ps2', 'ps4', 'ps5', 'nintendo', 'xbox', 'consoles', 'accessories')
LABEL = {
    'ro': {'ps2': 'Jocuri PS2', 'ps4': 'Jocuri PS4', 'ps5': 'Jocuri PS5', 'nintendo': 'Jocuri Nintendo', 'xbox': 'Jocuri Xbox', 'consoles': 'Console PlayStation', 'accessories': 'Accesorii gaming'},
    'ru': {'ps2': 'Игры PS2', 'ps4': 'Игры PS4', 'ps5': 'Игры PS5', 'nintendo': 'Игры Nintendo', 'xbox': 'Игры Xbox', 'consoles': 'Игровые консоли', 'accessories': 'Игровые аксессуары'},
}
PLATFORM = {'ps2': 'PS2', 'ps4': 'PS4', 'ps5': 'PS5', 'nintendo': 'Nintendo', 'xbox': 'Xbox', 'consoles': 'PlayStation'}
STOP = {
    'ro': {'de','din','în','in','cu','la','pe','și','si','sau','un','o','pentru','care','ale','al','ai','a','prin','de-a','spre','către','contra','după','până','dintre','ce','iar'},
    'ru': {'и','в','во','на','с','со','для','но','а','или','к','по','до','от','из','за','у','при','над','под','что','как','об','о','это','так'},
}
META_LIMIT = 160  # Editorial target, not a Google-imposed length limit.
HOOK = '''    # P50_SEO_QUALITY_HOOK: retain human-readable metadata and image alt after catalog regeneration.
    addon50 = root / 'playspot-v50' / 'quality.py'
    if addon50.is_file(): subprocess.run([sys.executable, '-B', str(addon50), '--root', str(root)], check=True)
'''
ANCHOR = "    print(f'✅ Generated {total*2} product pages"
HEAD_TAGS = (
    ('name', 'description'),
    ('property', 'og:description'),
    ('name', 'twitter:description'),
)


def compact(text: str) -> str:
    return ' '.join(str(text or '').split())


def take_clause(s: str, budget: int, lang: str) -> str:
    """Extract a useful synopsis, not a mid-word or dangling conjunction cut."""
    original = compact(s)
    if not original or budget < 17:
        raise ValueError('Insufficient space for a meaningful meta description')
    if len(original) <= budget:
        return original if original.endswith(('.', '!', '?', '…')) else original + ('.' if len(original) + 1 <= budget else '')
    # A whole first sentence is preferable to keyword fragments.
    for i, c in enumerate(original):
        if c in '.!?' and i >= 26 and i + 1 <= budget and (i+1 == len(original) or original[i+1].isspace()):
            return original[:i+1]
    # Otherwise break at a natural comma/semicolon; use ellipsis because more follows.
    cut = [i for i,c in enumerate(original[:budget-1]) if c in ',;:' and i >= 28]
    if cut:
        natural = original[:cut[-1]].strip(' ,;:.')
        if len(natural) >= 24:
            return natural + '…'
    shortened = original[:budget-1]
    if len(original) > budget - 1:
        shortened = shortened.rsplit(' ', 1)[0] if ' ' in shortened else shortened
    shortened = shortened.rstrip(' ,;:.-')
    while shortened and shortened.split()[-1].lower().strip('“”"\'()') in STOP[lang]:
        shortened = shortened.rsplit(' ',1)[0] if ' ' in shortened else ''
    if len(shortened) < min(18, budget-1):
        raise ValueError('Meta fragment too short; cannot guarantee readable snippet')
    return shortened + '…'


def make_meta(product: dict, cat: str, lang: str) -> str:
    name = compact(product['title'])
    description = compact(product['description'])
    prefix = f'{name} | {LABEL[lang][cat]}: '
    # Both regions remain mentioned for compatibility with V44 local-SEO validations.
    long_tail = (' Predare în Chișinău, curier în Moldova.' if lang == 'ro'
                 else ' Встреча в Кишинёве, курьер по Молдове.')
    short_tail = (' Chișinău și Moldova.' if lang == 'ro'
                  else ' В Кишинёве и Молдове.')
    # Prefer informative fulfilment language, but retain a readable game synopsis.
    tail = long_tail if META_LIMIT-len(prefix)-len(long_tail) >= 47 else short_tail
    room = META_LIMIT-len(prefix)-len(tail)
    if room < 18:
        raise ValueError(f'Product title is too long for safe snippet: {name}')
    synopsis = take_clause(description, room, lang)
    out = prefix + synopsis + tail
    if len(out) > META_LIMIT or description[:12] not in out:
        raise AssertionError(f'Meta invalid: {name} ({len(out)} chars)')
    if not all(x in out for x in (('Chișinău','Moldova') if lang=='ro' else ('Кишинёве','Молдове'))):
        raise AssertionError('Missing real location context: '+name)
    return out


def image_alt(item: dict, cat: str, lang: str) -> str:
    name = compact(item['title'])
    if cat in PLATFORM and cat not in ('consoles',):
        return (f'Imagine joc {name} pentru {PLATFORM[cat]}' if lang=='ro' else f'Изображение игры {name} для {PLATFORM[cat]}')
    return (f'Imagine produs {name}' if lang=='ro' else f'Изображение товара {name}')


def replace_head(s: str, value: str, where: str) -> str:
    head, sep, body = s.partition('</head>')
    if not sep: raise ValueError(f'{where}: missing </head>')
    escaped = html.escape(value, quote=True)
    for key, attr in HEAD_TAGS:
        pattern = re.compile(r'(<meta\s+'+key+r'="'+re.escape(attr)+r'"\s+content=")([^"]*)(")', re.I)
        head, n = pattern.subn(lambda m:m.group(1)+escaped+m.group(3), head, count=1)
        if n!=1 and attr=='description':raise ValueError(f'{where}: meta description missing')
        if len(value)>META_LIMIT:raise ValueError('description over budget')
    return head+sep+body


def replace_hero_alt(s: str, alt: str, where: str) -> str:
    pattern = re.compile(r'(<div class="seo-detail-image"><img\b[^>]*?\balt=")([^"]*)(")')
    s,n = pattern.subn(lambda m:m.group(1)+html.escape(alt,quote=True)+m.group(3),s,count=1)
    if n!=1:raise ValueError(f'{where}: product image alt anchor missing')
    return s


def replace_card_alts(s: str, items: list, cat: str, lang: str, where:str) -> str:
    """Fix only category thumbnails, leaving logos and decorative images alone."""
    for item in items:
        current='alt="'+html.escape(compact(item['title']),quote=True)+'"'
        new='alt="'+html.escape(image_alt(item,cat,lang),quote=True)+'"'
        # Each catalog item occurs exactly once as a card in its category.
        if current==new:continue
        count=s.count(current)
        if count == 1: s=s.replace(current,new,1)
        elif count == 0 and s.count(new)==1: pass  # Already optimized.
        else:raise ValueError(f'{where}: thumbnail alt ambiguous for {item["title"]}: {count}')
    return s


def patch_generator(source:str) -> str:
    if 'P50_SEO_QUALITY_HOOK' in source:
        if source.count('P50_SEO_QUALITY_HOOK')!=1:raise ValueError('V50 hook repeated')
        return source
    if 'P49_CLEAN_PRODUCT_URL' not in source or 'P48_STATIC_SEO_MENU_ONLY' not in source:
        raise ValueError('Need V49 URL and V48 menu baseline')
    if source.count(ANCHOR)!=1:raise ValueError('Generator anchor has changed')
    return source.replace(ANCHOR,HOOK+ANCHOR,1)


def plan(root: Path) -> tuple[dict[Path,str], dict]:
    root=root.resolve()
    changes:dict[Path,str] = {}
    index_file=root/'playspot-v49/slug-index.json'
    slugs=json.loads(index_file.read_text(encoding='utf-8'))
    if set(slugs)!=set(CATS):raise ValueError('Unexpected slug index categories')
    total=0
    for cat in CATS:
        folder='console' if cat=='consoles' else cat
        for lang in ('ro','ru'):
            suffix='_ru' if lang=='ru' else ''
            fp=root/'data'/f'{cat}{suffix}.json'
            items=json.loads(fp.read_text(encoding='utf-8'))
            ids={str(item['id']):item for item in items}
            if len(ids)!=len(items) or set(ids)!=set(slugs[cat]):
                raise ValueError(f'{cat}/{lang}: product IDs do not match V49 slug map')
            updated_items=[]
            for item in items:
                item=dict(item)
                item['seo_meta_description']=make_meta(item,cat,lang)
                updated_items.append(item)
                slug=slugs[cat][str(item['id'])]
                page=root/('ru/produse' if lang=='ru' else 'produse')/folder/slug
                old=page.read_text(encoding='utf-8')
                if f'"sku":"{item["id"]}"' not in old:raise ValueError('Wrong SKU for '+str(page))
                new=replace_hero_alt(replace_head(old,item['seo_meta_description'],str(page)),image_alt(item,cat,lang),str(page))
                if new!=old:changes[page]=new
            newdata=json.dumps(updated_items,ensure_ascii=False,indent=2)+'\n'
            if newdata!=fp.read_text(encoding='utf-8'):changes[fp]=newdata
            category=root/('ru/categorii' if lang=='ru' else 'categorii')/f'{cat}.html'
            orig=category.read_text(encoding='utf-8')
            modified=replace_card_alts(orig,items,cat,lang,str(category))
            if modified!=orig:changes[category]=modified
            if lang=='ro':total+=len(items)
    generator=root/'playspot-v29/generate.py'
    old=generator.read_text(encoding='utf-8')
    modified=patch_generator(old)
    if old!=modified:changes[generator]=modified
    if total<279:raise ValueError(f'Catalog unexpectedly smaller than 279: {total}')
    return changes,{'products':total,'pages':total*2,'categories':len(CATS)*2,'changed_files':len(changes)}


def main(root:Path,check:bool)->None:
    changes,counts=plan(root)
    print(('V50 PREVIEW' if check else 'V50 SEO QUALITY')+': '+str(counts))
    if check:return
    for path,source in changes.items():path.write_text(source,encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='.');parser.add_argument('--check',action='store_true')
    opts=parser.parse_args();main(Path(opts.root),opts.check)
