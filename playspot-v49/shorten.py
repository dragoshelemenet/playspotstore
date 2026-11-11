#!/usr/bin/env python3
"""V49: shorten existing game/product URLs without duplicating title+internal SKU.

One canonical URL per product/language. No geo suffixes, doorway pages, fake item
condition, or redirect stubs. Retains product copy, local delivery information,
prices, images, rich data and existing category URLs. Standard library only.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')
SITE='https://playspotstore.online'
INDEX='playspot-v49/slug-index.json'
URLMAP='playspot-v49/old-to-new.json'
HOMES=('index.html','ru.html')
GUIDES=('jocuri-video-chisinau-moldova.html','ru/videoigry-kishinev-moldova.html')
SITEMAPS=('sitemap.xml','sitemap.html','ru/sitemap.html')
MANIFEST='seo/generated-paths.json'
PRODUCT_RE=re.compile(r'"sku"\s*:\s*"([^"]+)"')
JS_RE=re.compile(r'(window\.p29ProductSlugs=)(\{.*?\})(;)',re.S)
GEN_MARK='P49_CLEAN_PRODUCT_URL'


def slug(value:str)->str:
    txt=unicodedata.normalize('NFKD',str(value)).encode('ascii','ignore').decode('ascii').lower()
    return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',txt)).strip('-') or 'produs'


def catalog(root:Path)->dict[str,dict[str,dict]]:
    products={}
    for cat in CATS:
        ro=json.loads((root/'data'/f'{cat}.json').read_text(encoding='utf-8'))
        ru=json.loads((root/'data'/f'{cat}_ru.json').read_text(encoding='utf-8'))
        if not isinstance(ro,list) or not ro or len(ro)!=len(ru):raise ValueError('Invalid RO/RU catalog '+cat)
        a={str(p['id']):p for p in ro};b={str(p['id']):p for p in ru}
        if len(a)!=len(ro) or len(b)!=len(ru) or set(a)!=set(b):raise ValueError('Mismatched product IDs '+cat)
        for p in ro:
            if not p.get('title') or not p.get('description'):raise ValueError('Incomplete product '+str(p))
        products[cat]=a
    return products


def create_slugs(root:Path, products:dict)->dict:
    location=root/INDEX
    stored=json.loads(location.read_text(encoding='utf-8')) if location.is_file() else {}
    if stored and (not isinstance(stored,dict) or set(stored)!=set(CATS)):
        raise ValueError('Existing V49 slug map invalid')
    out={};collision_groups=0
    for cat,items in products.items():
        prior=stored.get(cat,{})
        if not isinstance(prior,dict):raise ValueError('Invalid slug map category '+cat)
        names={pid:slug(prod['title']) for pid,prod in items.items()}
        counts=Counter(names.values())
        collision_groups+=sum(count>1 for count in counts.values())
        result={};used=set()
        # Preserve slugs for products already assigned by this version.
        for pid in items:
            if pid in prior:
                name=prior[pid]
                if not isinstance(name,str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,170}\.html',name):raise ValueError('Unsafe saved slug '+str(name))
                if name in used:raise ValueError('Duplicated saved slug '+name)
                result[pid]=name;used.add(name)
        for pid,name in names.items():
            if pid in result:continue
            basename=name+'.html'
            if counts[name]>1 or basename in used:
                digest=hashlib.sha1(pid.encode('utf-8')).hexdigest()
                basename=f'{name}-{digest[:7]}.html'
            if basename in used:raise ValueError('Unexpected slug hash collision '+basename)
            result[pid]=basename;used.add(basename)
        out[cat]=result
    return out


def patch_generator(source:str)->str:
    if GEN_MARK in source:
        for needle in ('def p49_slug(', 'productslug=p49_slug(cat,item)', ':p49_slug(cat,item) for item in ro'):
            if needle not in source:raise ValueError('Incomplete V49 generator patch: '+needle)
        return source
    old_page="    productslug=f\"{slugify(item['title'])}-{safe_id(item['id'])}.html\""
    if source.count(old_page)!=1:raise ValueError('Unexpected V29 page_path; will not modify blindly')
    old_map='f"{slugify(item[\'title\'])}-{safe_id(item[\'id\'])}.html" for item in ro'
    if source.count(old_map)!=1:raise ValueError('Unexpected V29 homepage slugmap; will not modify blindly')
    anchor='def page_path(cat, item, lang):'
    if source.count(anchor)!=1:raise ValueError('Missing V29 page_path function')
    helper='''# P49_CLEAN_PRODUCT_URL: one stable human-readable slug per product ID.
# The mapping survives future catalog regenerations and product title changes.
from functools import lru_cache as _p49_lru_cache
@_p49_lru_cache(maxsize=1)
def _p49_saved_slugs():
    root=Path(__file__).resolve().parent.parent
    path=root/'playspot-v49'/'slug-index.json'
    if not path.is_file():raise FileNotFoundError('Missing V49 slug index: '+str(path))
    return json.loads(path.read_text(encoding='utf-8'))

def p49_slug(cat,item):
    mapping=_p49_saved_slugs()[cat]
    pid=str(item['id'])
    if pid in mapping:return mapping[pid]
    # Safe fallback for future NEW inventory. Do not rename existing pages.
    import hashlib as _hashlib
    base=slugify(item['title'])
    candidate=base+'.html'
    if candidate in mapping.values():
        candidate=base+'-'+_hashlib.sha1(pid.encode('utf-8')).hexdigest()[:7]+'.html'
    return candidate

'''
    source=source.replace(anchor,helper+anchor,1)
    source=source.replace(old_page,'    productslug=p49_slug(cat,item)',1)
    source=source.replace(old_map,'p49_slug(cat,item) for item in ro',1)
    return source


def patch_legacy_validator(source:str)->str:
    marker='# P49_VALIDATOR_COMPAT'
    if marker in source:return source
    anchor='def validate(root:Path):\n'
    if source.count(anchor)!=1:raise ValueError('V47 validator changed; will not patch')
    guard=('    '+marker+': use the current canonical slug validator after V49.\n'
           "    if (root/'playspot-v49/slug-index.json').is_file():\n"
           '        import runpy\n'
           "        runpy.run_path(str(root/'playspot-v49/validate.py'))['validate'](root)\n"
           '        return\n')
    return source.replace(anchor,anchor+guard,1)


def page_index(root:Path,cat:str,lang:str)->dict[str,Path]:
    folder='console' if cat=='consoles' else cat
    directory=root/('ru/produse' if lang=='ru' else 'produse')/folder
    found={}
    for path in sorted(directory.glob('*.html')):
        source=path.read_text(encoding='utf-8')
        if 'P45 LEGACY REDIRECT' in source or '<meta http-equiv="refresh"' in source:
            raise ValueError('Old redirect page still present: '+str(path))
        m=PRODUCT_RE.search(source)
        if not m:raise ValueError('Missing Product schema SKU in '+str(path))
        pid=m.group(1)
        if pid in found:raise ValueError('Duplicate product file for '+pid+' '+lang)
        found[pid]=path
    return found


def update_home_slugs(s:str,slug_index:dict,lang:str)->str:
    matches=list(JS_RE.finditer(s))
    if len(matches)!=1:raise ValueError('Missing/duplicated homepage JS product link lookup: '+lang)
    m=matches[0];current=json.loads(m.group(2))
    for cat,names in slug_index.items():
        key='console' if cat=='consoles' else cat
        if key not in current or set(current[key])!=set(names):
            raise ValueError('Homepage product IDs differ from catalog for '+key+'/'+lang)
        for pid,filename in names.items():current[key][pid]=filename
    result=json.dumps(current,ensure_ascii=False,separators=(',',':'))
    return s[:m.start(2)]+result+s[m.end(2):]


def replace_all_paths(s:str,remap:dict[str,str])->str:
    # Explicit absolute paths, so an image name or SEO prose is never renamed.
    for old,new in sorted(remap.items(),key=lambda p:-len(p[0])):
        s=s.replace('/'+old,'/'+new)
    return s


def plan(root:Path):
    root=root.resolve()
    if not (root/'playspot-v48/cleanup.py').is_file() or not (root/'playspot-v47/restore.py').is_file():
        raise ValueError('Install V47 + V48 before V49')
    products=catalog(root)
    slugs=create_slugs(root,products)
    total=sum(len(v) for v in products.values())
    if total<279:raise ValueError('Unexpectedly small catalog; no files modified')
    locations={};mapping={};all_dest=set()
    for cat,items in products.items():
        for lang in ('ro','ru'):
            found=page_index(root,cat,lang)
            if set(found)!=set(items):
                raise ValueError(f'{cat}/{lang} pages mismatch: {len(found)} vs {len(items)}')
            folder='console' if cat=='consoles' else cat
            for pid in items:
                old_path=found[pid]
                new_rel=(Path('ru/produse') if lang=='ru' else Path('produse'))/folder/slugs[cat][pid]
                dest=root/new_rel
                if dest in all_dest:raise ValueError('Duplicate generated path '+str(dest))
                all_dest.add(dest)
                locations[old_path]=dest
                if old_path!=dest:
                    mapping[old_path.relative_to(root).as_posix()]=new_rel.as_posix()
    if set(mapping).intersection(mapping.values()):
        raise ValueError('New filename is currently used by another product; unsafe rename')
    oldmap=root/URLMAP
    if oldmap.is_file():
        persisted=json.loads(oldmap.read_text(encoding='utf-8'))
        if not isinstance(persisted,dict):raise ValueError('Bad existing old/new URL map')
        if mapping and persisted!=mapping:
            raise ValueError('Conflicting V49 URL map; partial or altered install, refusing overwrite')
        mapping=persisted
    else:
        if len(mapping)<total*2:
            raise ValueError(f'Expected {total*2} product URLs to shorten, got {len(mapping)}; potential partial installation')
    for old,new in mapping.items():
        if old==new or not (old.startswith(('produse/','ru/produse/')) and new.startswith(('produse/','ru/produse/'))):
            raise ValueError('Unsafe or unexpected URL mapping')
    writes={};deletes=set()
    def record(path:Path,content:str):
        old=path.read_text(encoding='utf-8') if path.is_file() else None
        if old!=content:writes[path]=content
    # Move real product HTML with ALL existing Product JSON-LD and visible text.
    for old_path,new_path in locations.items():
        original=old_path.read_text(encoding='utf-8')
        converted=replace_all_paths(original,mapping)
        if old_path!=new_path:
            if new_path.is_file() and new_path not in locations:
                raise ValueError('Refusing overwrite of unexpected existing path '+str(new_path))
            record(new_path,converted)
            deletes.add(old_path)
        else:record(new_path,converted)
    for cat in CATS:
        for lang in ('ro','ru'):
            prefix='ru/' if lang=='ru' else ''
            path=root/f'{prefix}categorii/{cat}.html'
            record(path,replace_all_paths(path.read_text(encoding='utf-8'),mapping))
    for filename,lang in [('index.html','ro'),('ru.html','ru')]:
        p=root/filename
        s=replace_all_paths(p.read_text(encoding='utf-8'),mapping)
        record(p,update_home_slugs(s,slugs,lang))
    for filename in (*GUIDES,*SITEMAPS):
        p=root/filename
        if not p.is_file():raise FileNotFoundError('Missing V44 file '+filename)
        record(p,replace_all_paths(p.read_text(encoding='utf-8'),mapping))
    manifest=root/MANIFEST
    if manifest.is_file():
        values=json.loads(manifest.read_text(encoding='utf-8'))
        if not isinstance(values,list):raise ValueError('Generated URL manifest is not a list')
        converted=[mapping.get(x,x) for x in values]
        if len(converted)!=len(set(converted)):raise ValueError('Duplicate generated URL manifest paths')
        record(manifest,json.dumps(converted,ensure_ascii=False,indent=2)+'\n')
    generator=root/'playspot-v29/generate.py'
    record(generator,patch_generator(generator.read_text(encoding='utf-8')))
    validator=root/'playspot-v47/validate.py'
    record(validator,patch_legacy_validator(validator.read_text(encoding='utf-8')))
    record(root/INDEX,json.dumps(slugs,ensure_ascii=False,indent=2)+'\n')
    record(root/URLMAP,json.dumps(mapping,ensure_ascii=False,indent=2)+'\n')
    stats={'products':total,'pages_ro_ru':total*2,'renamed_urls':len(mapping),
           'files_written':len(writes),'old_files_removed':len(deletes),
           'new_geo_product_urls':0}
    return writes,deletes,stats


def main(root:Path,check:bool):
    writes,deletes,stats=plan(root)
    print(('V49 PREVIEW' if check else 'V49 APPLY')+': '+json.dumps(stats,ensure_ascii=False))
    if check:return
    for path,content in writes.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(content,encoding='utf-8')
    for path in deletes:
        if path.is_file():path.unlink()
    print('V49: original long product URLs removed; no redirect pages generated.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--check',action='store_true')
    args=p.parse_args();main(Path(args.root),args.check)
