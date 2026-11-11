#!/usr/bin/env python3
"""V45: SEO-friendly Chișinău/Moldova URL migration with safe static legacy redirects.

One canonical RO/RU product per SKU. No fabricated product condition, ratings,
stock, prices or delivery charges. GitHub Pages cannot issue HTTP 301 natively,
so the old URLs use instant HTML meta refresh (documented fallback).
"""
from __future__ import annotations
import argparse
import copy
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SITE='https://playspotstore.online'
NS='http://www.sitemaps.org/schemas/sitemap/0.9'
XNS='http://www.w3.org/1999/xhtml'
CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')
PREFIX={'ro':'chisinau-moldova','ru':'kishinev-moldova'}
ROUTE_NAMES={
 'ro':{'ps2':'jocuri-ps2','ps4':'jocuri-ps4','ps5':'jocuri-ps5','nintendo':'jocuri-nintendo','xbox':'jocuri-xbox','consoles':'console-playstation','accessories':'accesorii-gaming'},
 'ru':{'ps2':'igry-ps2','ps4':'igry-ps4','ps5':'igry-ps5','nintendo':'igry-nintendo','xbox':'igry-xbox','consoles':'konsoli-playstation','accessories':'igrovye-aksessuary'},
}
PLATFORM={'ps2':'PS2','ps4':'PS4','ps5':'PS5','nintendo':'Nintendo','xbox':'Xbox','consoles':'PlayStation','accessories':'gaming'}
MARKER='<!-- P45 LEGACY REDIRECT -->'
COPY_MARK='<!-- P45 LOCALIZED PRODUCT DESCRIPTION -->'


def lang_of(path:str)->str:
    return 'ru' if path.startswith('ru/') else 'ro'


def remap(old:str)->str:
    lang=lang_of(old)
    prefix='ru/' if lang=='ru' else ''
    base=old.removeprefix(prefix)
    if base.startswith('categorii/') and base.endswith('.html'):
        cat=base[len('categorii/'):-5]
        if cat not in CATS:raise ValueError('Unexpected category route: '+old)
        return f'{prefix}categorii/{ROUTE_NAMES[lang][cat]}-{PREFIX[lang]}.html'
    if base.startswith('produse/') and base.endswith('.html'):
        bits=base.split('/')
        if len(bits)!=3 or bits[1] not in CATS+('console',):raise ValueError('Unexpected product route: '+old)
        stem=bits[2][:-5]
        if stem.endswith('-'+PREFIX[lang]):return old
        return f'{prefix}produse/{bits[1]}/{stem}-{PREFIX[lang]}.html'
    raise ValueError('Non-product/category URL in migration: '+old)


def routes(root:Path)->dict[str,str]:
    manifest=root/'seo/generated-paths.json'
    if manifest.is_file():
        old=[x for x in json.loads(manifest.read_text(encoding='utf-8')) if x.startswith(('produse/','ru/produse/','categorii/','ru/categorii/'))]
    else:
        old=[]
        for n in ET.parse(root/'sitemap.xml').findall(f'{{{NS}}}url'):
            loc=n.find(f'{{{NS}}}loc')
            if loc is None or not loc.text:continue
            p=loc.text.removeprefix(SITE+'/')
            if p.startswith(('produse/','ru/produse/','categorii/','ru/categorii/')) and not p.endswith(('-chisinau-moldova.html','-kishinev-moldova.html')):old.append(p)
    if not old:
        existing=root/'playspot-v45/url-map.json'
        if existing.is_file():return json.loads(existing.read_text(encoding='utf-8'))
    mapping={o:remap(o) for o in old}
    if len(mapping)<550 or len(set(mapping.values()))!=len(mapping):raise ValueError(f'Unexpected route mapping size/collision: {len(mapping)}')
    return mapping


def local_copy(pid:str,title:str,cat:str,lang:str,old_desc:str)->str:
    platform=PLATFORM[cat]
    t=html.escape(title,quote=True)
    p=html.escape(platform,quote=True)
    # Keep the already unique V40/V42 synopsis verbatim, with a contextual local
    # sentence in varied positions. No fake game facts and no per-city duplicate URLs.
    value=sum((i+1)*ord(c) for i,c in enumerate(pid))%5
    if lang=='ro':
        label='produsul' if cat in ('accessories','consoles') else 'jocul'
        openers=[f'{t} pentru {p}: ',f'Cauți {t} pentru {p} în Moldova? ',f'{t} pe {p} — ',f'Pentru {label} {t} ({p}), ',f'{t} ({p}) este în catalogul PlaySpotStore. ']
        notes=[
          'Predarea personală se poate stabili în Chișinău, iar pentru Bălți și Orhei putem discuta expedierea prin curier.',
          'Din Chișinău se poate conveni o predare personală; pentru Ungheni, Cahul și alte orașe din Moldova discutăm livrarea prin curier.',
          'În Chișinău putem stabili predarea de comun acord. Pentru Soroca, Comrat și restul Moldovei, confirmăm opțiunile de curier înainte de comandă.',
          'Poți solicita detalii despre predarea personală în Chișinău ori despre livrarea prin curier către Bălți, Orhei și alte localități.',
          'Comenzile se pot preda personal în Chișinău prin înțelegere; pentru Cahul, Ungheni și alte orașe din Moldova, livrarea prin curier se confirmă înainte de comandă.',
        ]
        if value in (0,3):return f'{openers[value]}{old_desc} {notes[value]}'
        if value==1:return f'{openers[value]}{notes[value]} {old_desc}'
        if value==2:return f'{old_desc} {openers[value]}{notes[value]}'
        return f'{openers[value]}{old_desc} {notes[value]}'
    else:
        kind='товар' if cat in ('accessories','consoles') else 'игра'
        openers=[f'{t} для {p}: ',f'Ищете {t} для {p} в Молдове? ',f'{t} на {p} — ',f'Для покупки {t} ({p}): ',f'{t} ({p}) представлен в каталоге PlaySpotStore. ']
        notes=[
          'В Кишинёве возможна передача при личной встрече, а доставку курьером в Бельцы и Оргеев можно согласовать перед заказом.',
          'В Кишинёве можно договориться о личной встрече; для Унген, Кагула и других городов Молдовы уточняем курьерскую доставку.',
          'Для Кишинёва доступна передача по договорённости. Для Сорок, Комрата и остальной Молдовы уточняйте вариант курьерской доставки.',
          'Можно уточнить личную встречу в Кишинёве или отправку курьером в Бельцы, Оргеев и другие населённые пункты Молдовы.',
          'Передачу в Кишинёве можно согласовать лично; доставку курьером в Кагул, Унгены и другие города Молдовы подтверждаем перед заказом.',
        ]
        if value in (0,3):return f'{openers[value]}{old_desc} {notes[value]}'
        if value==1:return f'{openers[value]}{notes[value]} {old_desc}'
        if value==2:return f'{old_desc} {openers[value]}{notes[value]}'
        return f'{openers[value]}{old_desc} {notes[value]}'


def updated_body(src:str,product:dict|None,cat:str|None,lang:str)->str:
    if product is None or COPY_MARK in src:return src
    match=re.search(r'(<p class="seo-detail-description">)(.*?)(</p>)',src,re.S)
    if not match:raise ValueError('Expected visible product description '+product['id'])
    existing=match.group(2)
    if '<' in existing and not re.search(r'&(?:#\d+|#x[0-9a-f]+|\w+);',existing,re.I):
        raise ValueError('Unexpected markup inside product description '+product['id'])
    new=local_copy(str(product['id']),str(product['title']),cat,lang,existing)
    return src[:match.start()]+COPY_MARK+'\n'+match.group(1)+new+match.group(3)+src[match.end():]


def replace_paths(content:str,mapping:dict[str,str])->str:
    # Exact escaped HTML and JSON route strings; cannot replace only path prefixes.
    for old,new in sorted(mapping.items(),key=lambda kv:-len(kv[0])):
        content=content.replace('/'+old,'/'+new)
    return content


def replace_home_slugmap(page:str,lang:str,mapping:dict[str,str])->str:
    # Existing JS cards/search use a serialized ID -> slug lookup. Preserve it.
    pat=re.compile(r'(window\.p29ProductSlugs=)(\{.*?\})(;)',re.S)
    matches=list(pat.finditer(page))
    if not matches:return page  # synthetic fixtures may not include homepage JS.
    if len(matches)!=1:raise ValueError('Ambiguous homepage slugmap')
    m=matches[0]
    obj=json.loads(m.group(2));n=0
    for old,new in mapping.items():
        if lang_of(old)!=lang or '/produse/' not in '/'+old:continue
        seg=old.split('/')
        cat=seg[-2]
        if cat=='console':cat='console'
        if cat not in obj:continue
        old_basename=seg[-1];new_basename=new.split('/')[-1]
        for pid,val in obj[cat].items():
            if val==old_basename:
                obj[cat][pid]=new_basename;n+=1
    expected=sum(1 for old in mapping if lang_of(old)==lang and '/produse/' in '/'+old)
    current=sum(1 for old,new in mapping.items() if lang_of(old)==lang and '/produse/' in '/'+old and new.rsplit('/',1)[-1] in obj.get(old.split('/')[-2],{}).values())
    if n+current<min(expected,250):raise ValueError('Homepage slugmap is missing mapped products: '+str(n+current))
    js=json.dumps(obj,ensure_ascii=False,separators=(',',':'))
    return page[:m.start(2)]+js+page[m.end(2):]


def redirect(old:str,new:str)->str:
    lang=lang_of(old)
    label='Pagina s-a mutat. Deschide noul URL al produsului.' if lang=='ro' else 'Страница переехала. Откройте новый адрес товара.'
    target='/'+new
    return (f'<!doctype html>\n<html lang="{lang}"><head><meta charset="utf-8">\n'
            f'<meta http-equiv="refresh" content="0;url={html.escape(target,quote=True)}">\n'
            f'<link rel="canonical" href="{SITE}/{html.escape(new,quote=True)}">\n'
            f'<title>PlaySpotStore – {"Redirecționare" if lang=="ro" else "Переадресация"}</title>\n'
            f'</head><body>\n{MARKER}\n<p>{label} '
            f'<a href="{html.escape(target,quote=True)}">{html.escape(target)}</a></p></body></html>\n')


def patch_generator(source:str)->str:
    if 'P45_GEO_URL_HOOK' in source:return source
    anchor="    print(f'✅ Generated {total*2} product pages"
    if source.count(anchor)!=1:raise ValueError('V29 generator insertion point changed')
    hook="""    # P45_GEO_URL_HOOK: migrate existing RO/RU URLs and preserve legacy redirects.
    addon45 = root / 'playspot-v45' / 'migrate.py'
    if addon45.is_file(): subprocess.run([sys.executable, str(addon45), '--root', str(root)], check=True)
"""
    return source.replace(anchor,hook+anchor,1)


def make_changes(root:Path):
    root=root.resolve();mapping=routes(root)
    changes={};removed=[]
    products={}
    for cat in CATS:
        for lang in ('ro','ru'):
            path=root/'data'/f'{cat}{"_ru" if lang=="ru" else ""}.json'
            for p in json.loads(path.read_text(encoding='utf-8')):
                key=(cat,lang,str(p['id']))
                if key in products:raise ValueError('Duplicate catalog SKU '+str(key))
                products[key]=p
    for old,new in mapping.items():
        old_path=root/old;new_path=root/new
        old_source=old_path.read_text(encoding='utf-8') if old_path.is_file() else None
        new_source=new_path.read_text(encoding='utf-8') if new_path.is_file() else None
        if old_source and MARKER not in old_source:
            source=old_source
        elif new_source:
            source=new_source
        else:raise ValueError('Missing original and migrated file for '+old)
        lang=lang_of(old)
        product=None;cat=None
        if '/produse/' in '/'+old:
            m=re.search(r'"sku"\s*:\s*"([^"]+)"',source)
            if not m:raise ValueError('Missing product SKU '+old)
            cat=old.split('/')[-2]
            if cat=='console':cat='consoles'
            product=products.get((cat,lang,m.group(1)))
            if product is None:raise ValueError('No localized product for '+old)
            source=updated_body(source,product,cat,lang)
        source=replace_paths(source,mapping)
        if new_source!=source:changes[new_path]=source
        redir=redirect(old,new)
        if old_source!=redir:changes[old_path]=redir
    for name,lang in [('index.html','ro'),('ru.html','ru')]:
        path=root/name;s=path.read_text(encoding='utf-8')
        result=replace_paths(s,mapping)
        result=replace_home_slugmap(result,lang,mapping)
        if s!=result:changes[path]=result
    for guide in ('jocuri-video-chisinau-moldova.html','ru/videoigry-kishinev-moldova.html'):
        path=root/guide
        if not path.is_file():raise ValueError('Missing V44 service guide '+guide)
        s=path.read_text(encoding='utf-8');result=replace_paths(s,mapping)
        if result!=s:changes[path]=result
    for path_name in ('sitemap.xml','sitemap.html','ru/sitemap.html'):
        path=root/path_name
        if not path.is_file():raise ValueError('Missing '+path_name)
        s=path.read_text(encoding='utf-8');result=replace_paths(s,mapping)
        if s!=result:changes[path]=result
    gp=root/'playspot-v29/generate.py'
    orig=gp.read_text(encoding='utf-8');new=patch_generator(orig)
    if orig!=new:changes[gp]=new
    mapfile=root/'playspot-v45/url-map.json'
    maptext=json.dumps(mapping,ensure_ascii=False,indent=2)+'\n'
    if not mapfile.exists() or mapfile.read_text(encoding='utf-8')!=maptext:changes[mapfile]=maptext
    return changes,{'aliases':len(mapping),'products':sum('/produse/' in '/'+p for p in mapping),'categories':sum('categorii/' in p for p in mapping),'files_changed':len(changes)}


def main(root:Path,check:bool):
    changes,stats=make_changes(root)
    print(('V45 PREVIEW: ' if check else 'V45 MIGRATED: ')+str(stats))
    if check:return
    for path,data in changes.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(data,encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--check',action='store_true')
    a=p.parse_args();main(Path(a.root),a.check)
