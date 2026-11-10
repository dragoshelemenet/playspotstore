#!/usr/bin/env python3
"""PlaySpotStore V40: truthful per-title RO/RU copy and static SEO product pages.

Keeps existing editorial descriptions, canonicals, hreflang, product paths, prices,
images, category UI, homepage and stock-unknown policy. Standard library only.
"""
from __future__ import annotations
import argparse
import html
import json
import re
import types
import unicodedata
from pathlib import Path

CATS = ('ps2', 'ps4', 'ps5', 'nintendo', 'xbox', 'consoles', 'accessories')
GEN = Path('playspot-v29/generate.py')
STYLE = '<link rel="stylesheet" href="/playspot-v40.css?v=20261110-v40">'
META_OLD = "meta=t['single_desc'].format(title=product['title'],category=catname)+' '+desc"
META_NEW = "meta=f'{product[\"title\"]} | {catname}: {desc}'"
SCHEMA_OLD = "product_schema={'@type':'Product','name':product['title'],'url':"
SCHEMA_NEW = "product_schema={'@type':'Product','name':product['title'],'sku':str(ro_item['id']),'url':"
PAGE_OLD = 'page=head(title,meta,path,alt,lang,img,schema,ogtype="product")'
PAGE_NEW = PAGE_OLD + "\n    page=page.replace('</head>', '" + STYLE + "\\n</head>', 1)"
DESCRIPTION_OLD = '<p class="seo-detail-description">{esc(desc)}</p>'
DESCRIPTION_NEW = '''<p class="seo-detail-description">{esc(desc)}</p>
<dl class="p40-product-facts" aria-label="{\"Информация о товаре\" if lang == \"ru\" else \"Informatii despre produs\"}">
<div><dt>{\"Платформа / категория\" if lang == \"ru\" else \"Platforma / categoria\"}</dt><dd>{esc(catname)}</dd></div>
<div><dt>{\"Код в каталоге\" if lang == \"ru\" else \"Cod in catalog\"}</dt><dd>{esc(str(ro_item['id']))}</dd></div>
</dl>'''


def key(title: str) -> str:
    s = unicodedata.normalize('NFKC', title).casefold()
    s = re.sub(r'[^\w]+', ' ', s, flags=re.UNICODE).strip()
    return ' '.join(s.split())


def load_copy(path: Path) -> dict:
    pairs = {}
    for number, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not raw.strip() or raw.startswith('#'):
            continue
        fields = raw.split('\t')
        if len(fields) != 3:
            raise ValueError(f'{path}:{number} must contain title + RO + RU, separated by tabs')
        name, ro, ru = [x.strip() for x in fields]
        norm = key(name)
        if not name or len(ro) < 65 or len(ru) < 55:
            raise ValueError(f'{path}:{number}: incomplete copy for {name}')
        if norm in pairs:
            raise ValueError(f'{path}:{number}: duplicate title {name}')
        pairs[norm] = (ro, ru)
    return pairs


def placeholder(s: str) -> bool:
    s = ' '.join((s or '').strip().casefold().split())
    return s.startswith('adăugat recent. confirmă starea') or s.startswith('adaugat recent. confirma starea') or s.startswith('новое поступление. уточняйте состояние')


def patch_generator(source: str) -> str:
    edits = ((META_OLD,META_NEW), (SCHEMA_OLD,SCHEMA_NEW), (PAGE_OLD,PAGE_NEW), (DESCRIPTION_OLD,DESCRIPTION_NEW))
    for old,new in edits:
        if new in source:
            continue
        if source.count(old) != 1:
            raise ValueError('Unsupported V29 generator: expected one occurrence of '+old[:70])
        source = source.replace(old,new,1)
    # Catch half-patched installations instead of silently generating mismatched pages.
    for _,new in edits:
        if new not in source:
            raise ValueError('V40 generator patch incomplete: '+new[:45])
    return source


def generate_pages(root: Path, json_data: dict, generator_code: str) -> dict[Path,str]:
    module = types.ModuleType('p40_generator')
    module.__file__ = str(root / GEN)
    exec(compile(generator_code, module.__file__, 'exec'), module.__dict__)
    output = {}
    for cat in CATS:
        ro, ru = json_data[cat]
        for index, base in enumerate(ro):
            for lang, localized in (('ro',ro),('ru',ru)):
                other = [(localized[j],ro[j]) for j in range(len(ro)) if j!=index]
                relative = module.page_path(cat,base,lang)
                path = root / relative
                if not path.is_file():
                    raise FileNotFoundError(f'Product page missing; run V29 generator first: {relative}')
                body = module.product_html(cat,lang,localized[index],base,other[:4])
                if body.count('<dl class="p40-product-facts"') != 1 or body.count('rel="canonical"') != 1 or body.count(STYLE) != 1:
                    raise AssertionError('Incomplete product page SEO: '+relative)
                if body.count('application/ld+json') != 1 or '"sku"' not in body:
                    raise AssertionError('Product structured data error: '+relative)
                output[path] = body
    return output


def main(root: Path, check: bool = False) -> None:
    root = root.resolve()
    if not (root / '.git').is_dir() or not (root / 'ru.html').is_file():
        raise RuntimeError('Run from PlaySpotStore Codespaces repository root')
    source_path = root / GEN
    source = source_path.read_text(encoding='utf-8')
    modified_gen = patch_generator(source)
    curated = load_copy(Path(__file__).with_name('descriptions.tsv'))
    records = {}
    updates = {}
    changed_ids = []
    misses = []
    known_ro_ids = set()
    for cat in CATS:
        ro_path = root / 'data' / (cat+'.json')
        ru_path = root / 'data' / (cat+'_ru.json')
        ro = json.loads(ro_path.read_text(encoding='utf-8'))
        ru = json.loads(ru_path.read_text(encoding='utf-8'))
        ru_map = {str(p['id']):p for p in ru}
        if len(ro)!=len(ru) or len(ru_map)!=len(ru) or {str(p['id']) for p in ro}!=set(ru_map):
            raise ValueError(cat+': RO/RU product IDs differ')
        if any(not isinstance(p.get('title'),str) for p in ro):
            raise ValueError(cat+': product title missing')
        localized_ru=[]
        for item in ro:
            product_id = str(item['id'])
            if product_id in known_ro_ids:
                raise ValueError('Duplicate internal product ID: '+product_id)
            known_ro_ids.add(product_id)
            loc = ru_map[product_id]
            ro_generic = placeholder(item.get('description',''))
            ru_generic = placeholder(loc.get('description',''))
            if ro_generic or ru_generic:
                entry = curated.get(key(item['title']))
                if entry is None:
                    misses.append((cat,item['title'],product_id))
                else:
                    if ro_generic:item['description'] = entry[0]
                    if ru_generic:loc['description'] = entry[1]
                    changed_ids.append(product_id)
            localized_ru.append(loc)
        updates[ro_path] = json.dumps(ro,ensure_ascii=False,indent=2)+'\n'
        updates[ru_path] = json.dumps(localized_ru,ensure_ascii=False,indent=2)+'\n'
        records[cat] = (ro,localized_ru)
    if misses:
        message='\n'.join(f'  {c}: {name} [{pid}]' for c,name,pid in misses)
        raise ValueError('The V40 editorial file has no safe fact-based copy for these products:\n'+message)
    if len(known_ro_ids) < 200:
        raise AssertionError('Unexpectedly small catalog; refusing to continue')
    pages = generate_pages(root,records,modified_gen)
    # Avoid rewriting unrelated files; this keeps manual edits and git diffs manageable.
    write_map = {source_path:modified_gen}
    for p,s in updates.items():
        if p.read_text(encoding='utf-8') != s:write_map[p]=s
    for p,s in pages.items():
        if p.read_text(encoding='utf-8') != s:write_map[p]=s
    if modified_gen != source:write_map[source_path]=modified_gen
    else:write_map.pop(source_path,None)
    if check:
        print(f'V40 CHECK: {len(known_ro_ids)} products, {len(pages)} localized product pages, {len(changed_ids)} placeholder products fixed, {len(write_map)} files would change')
        return
    for p,s in write_map.items():
        p.write_text(s,encoding='utf-8')
    print(f'V40 OK: {len(known_ro_ids)} products x 2 languages = {len(pages)} SEO pages; {len(changed_ids)} generic titles upgraded; {len(write_map)} files updated')
    print('Unchanged: categories, homepages, canonical URLs, hreflang, sitemap, prices, availability and custom product descriptions')


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',default='.')
    ap.add_argument('--check',action='store_true')
    a=ap.parse_args()
    main(Path(a.root),a.check)
