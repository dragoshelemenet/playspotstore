#!/usr/bin/env python3
"""V47: restore existing stable SEO catalog URLs from V45, with NO redirects.

V45 geographic canonical pages are moved back onto the original game/platform/
SKU URL. Geographic filename variants are deleted, not redirected. V42/V44 and
(optional) V46 product copy is retained. Future V29 rebuilds use the original
URLs and the retained localized product copy from the bilingual data files.
Pure Python standard library, safe and repeatable.
"""
from __future__ import annotations
import argparse
import html
import json
import re
from pathlib import Path

SITE='https://playspotstore.online'
CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')
MARKER='<!-- P45 LEGACY REDIRECT -->'
GEN_45="""    # P45_GEO_URL_HOOK: migrate existing RO/RU URLs and preserve legacy redirects.
    addon45 = root / 'playspot-v45' / 'migrate.py'
    if addon45.is_file(): subprocess.run([sys.executable, str(addon45), '--root', str(root)], check=True)
"""
GEN_46="""    # P46_NATURAL_MIX_HOOK: preserve stable editorial variants after V45 migration.
    mix46 = root / 'playspot-v46' / 'mix.py'
    if mix46.is_file(): subprocess.run([sys.executable, str(mix46), '--root', str(root)], check=True)
"""
DESCRIPTION_ANCHOR='<p class="seo-detail-description">{esc(desc)}</p>'
DESCRIPTION_REPLACE='<p class="seo-detail-description">{esc(compact(product.get("seo_local_description")) or desc)}</p>'
HEAD_FILES=('index.html','ru.html','jocuri-video-chisinau-moldova.html','ru/videoigry-kishinev-moldova.html','sitemap.xml','sitemap.html','ru/sitemap.html')


def readmap(root:Path)->dict[str,str]:
    f=root/'playspot-v45/url-map.json'
    if not f.is_file():raise FileNotFoundError('V45 url-map.json missing: install V45 before V47')
    obj=json.loads(f.read_text(encoding='utf-8'))
    if not isinstance(obj,dict) or len(obj)<570 or len(set(obj.values()))!=len(obj):
        raise ValueError('Unexpected/colliding V45 mapping')
    if set(obj).intersection(obj.values()):raise ValueError('Overlapping original and geographic paths')
    for old,new in obj.items():
        if not isinstance(old,str) or not isinstance(new,str) or old.startswith('/') or new.startswith('/') or '..' in old or '..' in new or not old.endswith('.html') or not new.endswith('.html'):
            raise ValueError('Unsafe URL mapping')
        if not old.startswith(('produse/','ru/produse/','categorii/','ru/categorii/')):raise ValueError('Unexpected old path '+old)
        if not new.endswith(('-chisinau-moldova.html','-kishinev-moldova.html')):raise ValueError('Unexpected new path '+new)
    return obj


def repl_urls(s:str,inverted:dict[str,str])->str:
    # Use only whole known geo paths; no global renaming of geographic words.
    for new,old in sorted(inverted.items(),key=lambda x:-len(x[0])):
        s=s.replace('/'+new,'/'+old)
    return s


def home_slugs(s:str,lang:str,mapping:dict[str,str])->str:
    pattern=re.compile(r'(window\.p29ProductSlugs=)(\{.*?\})(;)',re.S)
    ms=list(pattern.finditer(s))
    if len(ms)!=1:raise ValueError(f'Expected one homepage JS slug lookup in {lang}')
    m=ms[0];slugs=json.loads(m.group(2));expected=0;fixed=0
    for old,new in mapping.items():
        if (old.startswith('ru/'))!=(lang=='ru') or '/produse/' not in '/'+old:continue
        expected+=1
        cat=old.split('/')[-2]
        old_basename=old.rsplit('/',1)[-1]
        new_basename=new.rsplit('/',1)[-1]
        vals=slugs.get(cat)
        if not isinstance(vals,dict):raise ValueError(f'Missing JS category slugmap {cat}')
        for sku,value in vals.items():
            if value==new_basename:
                vals[sku]=old_basename;fixed+=1
    present=sum(1 for old in mapping if (old.startswith('ru/'))==(lang=='ru') and '/produse/' in '/'+old and old.rsplit('/',1)[-1] in slugs.get(old.split('/')[-2],{}).values())
    if present!=expected:raise ValueError(f'{lang} homepage slugmap incomplete: {present}/{expected} ({fixed} fixed)')
    return s[:m.start(2)]+json.dumps(slugs,ensure_ascii=False,separators=(',',':'))+s[m.end(2):]


def patch_generator(src:str)->str:
    if 'P45_GEO_URL_HOOK' in src:
        if GEN_45 not in src:raise ValueError('V45 regeneration hook differs: will not edit blindly')
        src=src.replace(GEN_45,'',1)
    if 'P46_NATURAL_MIX_HOOK' in src:
        if GEN_46 not in src:raise ValueError('V46 regeneration hook differs: will not edit blindly')
        src=src.replace(GEN_46,'',1)
    if DESCRIPTION_REPLACE not in src:
        if src.count(DESCRIPTION_ANCHOR)!=1:raise ValueError('Expected product description generator anchor once')
        src=src.replace(DESCRIPTION_ANCHOR,DESCRIPTION_REPLACE,1)
    if 'P44_MOLDOVA_SEO_HOOK' not in src:raise ValueError('V44 SEO regeneration hook missing')
    return src


def get_description(src:str,sku:str)->str:
    m=re.search(r'<p class="seo-detail-description">([^<]*)</p>',src,re.S)
    if not m:raise ValueError('Missing safe plain visible description for '+sku)
    value=html.unescape(m.group(1)).strip()
    if len(value)<25 or len(value)>1500 or '<' in value or '>' in value:
        raise ValueError('Unexpected visible description for '+sku)
    return value



def restore_compat(root:Path)->dict[Path,str]:
    """Remove the compatibility guards that only made sense with V45 redirects."""
    out={}
    changes=(
        ('playspot-v44/patch.py',(
            ("   for path in directory.glob('*.html'):\n    # P45_SKIP_MIGRATED_PRODUCTS: V29 regenerates old routes, V45 redirects them.\n    if path.name.endswith(('-chisinau-moldova.html','-kishinev-moldova.html')):continue\n    source=path.read_text(encoding='utf-8')",
             "   for path in directory.glob('*.html'):\n    source=path.read_text(encoding='utf-8')"),
            ("   for page in folder.glob('*.html'):\n    # P45_SKIP_MIGRATED_GUIDE: the existing new geo URL is the same SKU.\n    if page.name.endswith(('-chisinau-moldova.html','-kishinev-moldova.html')):continue\n    if f'\"sku\":\"{pid}\"' in page.read_text(encoding='utf-8'):",
             "   for page in folder.glob('*.html'):\n    if f'\"sku\":\"{pid}\"' in page.read_text(encoding='utf-8'):"),
        )),
        ('playspot-v44/validate.py',(
            ("   cp=base/'categorii'/f'{cat}.html'\n   # P45_GEO_VALIDATOR: prefer relocated canonical pages when V45 is installed.\n   if (root/'playspot-v45/url-map.json').is_file():\n    import json as _json\n    _map=_json.loads((root/'playspot-v45/url-map.json').read_text(encoding='utf-8'))\n    cp=root/_map.get(cp.relative_to(root).as_posix(),cp.relative_to(root).as_posix())\n   s=cp.read_text(encoding='utf-8')",
             "   cp=base/'categorii'/f'{cat}.html';s=cp.read_text(encoding='utf-8')"),
            ("   pages=list(directory.glob('*.html'))\n   if (root/'playspot-v45/url-map.json').is_file():\n    _suffix='-kishinev-moldova.html' if lang=='ru' else '-chisinau-moldova.html'\n    pages=[page for page in pages if page.name.endswith(_suffix)]",
             "   pages=list(directory.glob('*.html'))"),
        )),
        ('playspot-v42/validate.py',(
            ("    source=path.read_text(encoding='utf-8')\n    if '<!-- P45 LEGACY REDIRECT -->' in source:continue  # P45_ALIAS_SKIP\n    m=re.search",
             "    source=path.read_text(encoding='utf-8')\n    m=re.search"),
        )),
    )
    for relative,edits in changes:
        path=root/relative
        s=path.read_text(encoding='utf-8')
        modified=s
        for before,after in edits:
            if before in modified: modified=modified.replace(before,after,1)
        if 'P45_' in modified and relative=='playspot-v44/validate.py':
            raise ValueError('Unexpected V45 compatibility marker in validator')
        if modified!=s:out[path]=modified
    return out

def plan(root:Path):
    root=root.resolve();mapping=readmap(root);inverse={v:k for k,v in mapping.items()}
    writes:dict[Path,str]={};deletes:list[Path]=[]
    ro_count=0;restored=0;products=0;cats=0;source_items={}
    for cat in CATS:
        for lang in ('ro','ru'):
            path=root/'data'/f'{cat}{"_ru" if lang=="ru" else ""}.json'
            source_items[cat,lang]=json.loads(path.read_text(encoding='utf-8'))
    product_index={}
    for (cat,lang),rows in source_items.items():
        for item in rows:
            key=(cat,lang,str(item['id']))
            if key in product_index:raise ValueError('Duplicate inventory SKU '+str(key))
            product_index[key]=item
    for old,new in mapping.items():
        p_old,p_new=root/old,root/new
        old_source=p_old.read_text(encoding='utf-8') if p_old.is_file() else None
        if p_new.is_file():
            source=p_new.read_text(encoding='utf-8')
            if MARKER in source:raise ValueError('Geographic canonical contains redirect: '+new)
            if old_source is not None and MARKER not in old_source:
                raise ValueError('Refusing to overwrite a non-redirect original URL: '+old)
            deletes.append(p_new)
            restored+=1
        elif old_source and MARKER not in old_source:
            source=old_source  # already restored; rerun-safe
        else:raise ValueError('Missing canonical source for '+old)
        if '<meta http-equiv="refresh"' in source:raise ValueError('Unexpected redirect in canonical content '+new)
        source=repl_urls(source,inverse)
        if '/produse/' in '/'+old:
            products+=1
            sku_match=re.search(r'"sku"\s*:\s*"([^"]+)"',source)
            if not sku_match:raise ValueError('Missing product SKU '+old)
            cat=old.split('/')[-2];cat='consoles' if cat=='console' else cat
            lang='ru' if old.startswith('ru/') else 'ro'
            key=(cat,lang,sku_match.group(1))
            item=product_index.get(key)
            if item is None:raise ValueError('Unexpected product/ID '+str(key))
            # Retain game-specific local prose as source data so any future
            # static regeneration reproduces it at the old URL.
            local_desc=get_description(source,sku_match.group(1))
            if item.get('seo_local_description')!=local_desc:
                item['seo_local_description']=local_desc
            if lang=='ro':ro_count+=1
        else:cats+=1
        if old_source!=source:writes[p_old]=source
    for (cat,lang),items in source_items.items():
        p=root/'data'/f'{cat}{"_ru" if lang=="ru" else ""}.json'
        content=json.dumps(items,ensure_ascii=False,indent=2)+'\n'
        if p.read_text(encoding='utf-8')!=content:writes[p]=content
    for name in HEAD_FILES:
        p=root/name
        if not p.is_file():raise ValueError('Missing required site page '+name)
        before=p.read_text(encoding='utf-8')
        after=repl_urls(before,inverse)
        if name in ('index.html','ru.html'):
            after=home_slugs(after,'ro' if name=='index.html' else 'ru',mapping)
        if after!=before:writes[p]=after
    writes.update(restore_compat(root))
    gen=root/'playspot-v29/generate.py'
    original=gen.read_text(encoding='utf-8');updated=patch_generator(original)
    if updated!=original:writes[gen]=updated
    if products<558 or cats!=14 or ro_count<279:
        raise ValueError('Unexpected counts: '+str((products,cats,ro_count)))
    return writes,deletes,{'product_pages':products,'category_pages':cats,'geo_pages_removed':len(deletes),'content_updates':len(writes),'original_urls_restored':restored}


def main(root:Path,check:bool):
    writes,deletes,stats=plan(root)
    print(('V47 PREVIEW ' if check else 'V47 RESTORED ')+str(stats))
    if check:return
    for p,text in writes.items():
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(text,encoding='utf-8')
    for p in deletes:
        p.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='.');parser.add_argument('--check',action='store_true')
    args=parser.parse_args();main(Path(args.root),args.check)
