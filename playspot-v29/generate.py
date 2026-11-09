#!/usr/bin/env python3
"""PlaySpotStore V29 — build static RO/RU SEO catalog and connect existing homepages.
Runs in Codespaces against the actual current JSON inventory; pure Python stdlib.
No fabricated reviews, availability, prices, visits, or historical dates.
"""
from __future__ import annotations
import argparse
import html
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree as ET

SITE='https://playspotstore.online'
CATEGORIES=['ps2','ps4','ps5','nintendo','xbox','consoles','accessories']
CAT_RO={'ps2':'Jocuri PS2','ps4':'Jocuri PS4','ps5':'Jocuri PS5','nintendo':'Jocuri Nintendo','xbox':'Jocuri Xbox','consoles':'Console PlayStation','accessories':'Accesorii gaming'}
CAT_RU={'ps2':'Игры PS2','ps4':'Игры PS4','ps5':'Игры PS5','nintendo':'Игры Nintendo','xbox':'Игры Xbox','consoles':'Игровые консоли','accessories':'Игровые аксессуары'}
LABEL={
 'ro':{'home':'Acasă','catalog':'Catalog','all':'Toate categoriile','explore':'Descoperă catalogul PlaySpotStore',
       'catalog_info':'Alege platforma pentru a vedea produsele și detaliile lor, pe pagini dedicate.',
       'search':'Vezi produsele','total':'produse','one':'produs','filters':'Categorii','details':'Vezi detalii',
       'price':'Preț afișat','ask':'Preț la cerere','contact':'Comandă / Verifică disponibilitatea',
       'confirm':'Prețul, starea și disponibilitatea se confirmă înainte de comandă.',
       'desc_default':'Detalii despre produs disponibile la cerere.',
       'related':'Alte produse din această categorie','whatsapp':'Întreabă pe WhatsApp',
       'instagram':'Scrie pe Instagram','breadcrumb':'Navigare','return':'Înapoi la magazin',
       'catalog_title':'Jocuri, console și accesorii','products':'Produse în această categorie',
       'intro':'Descoperă produsele PlaySpotStore din categoria {category}. Poți verifica prețurile afișate și detaliile produselor, apoi ne poți contacta pentru confirmarea disponibilității și a comenzii în Moldova.',
       'single_desc':'{title} — {category} la PlaySpotStore. Vezi detaliile și contactează-ne pentru disponibilitate și comandă în Moldova.',
       'more':'Explorează alte categorii','lang':'Русский','call':'Contact',
       'legal':'Informațiile despre disponibilitate și preț se confirmă prin contact. Imaginile produselor pot fi orientative.',
       'count':'Produse disponibile în catalog: {count}', 'new':'Adăugat recent'},
 'ru':{'home':'Главная','catalog':'Каталог','all':'Все категории','explore':'Каталог PlaySpotStore',
       'catalog_info':'Выберите платформу, чтобы открыть отдельные страницы товаров с подробностями.',
       'search':'Смотреть товары','total':'товаров','one':'товар','filters':'Категории','details':'Подробнее',
       'price':'Цена в каталоге','ask':'Цена по запросу','contact':'Заказ / Уточнить наличие',
       'confirm':'Цена, состояние и наличие подтверждаются до оформления заказа.',
       'desc_default':'Подробности о товаре можно уточнить при обращении.',
       'related':'Другие товары этой категории','whatsapp':'Написать в WhatsApp',
       'instagram':'Написать в Instagram','breadcrumb':'Навигация','return':'Вернуться в магазин',
       'catalog_title':'Игры, консоли и аксессуары','products':'Товары этой категории',
       'intro':'Посмотрите товары PlaySpotStore в категории «{category}». Узнайте подробности и цены в каталоге, затем уточните наличие, состояние и условия заказа по Молдове.',
       'single_desc':'{title} — {category} в PlaySpotStore. Подробности, цена и заказ в Молдове с подтверждением наличия.',
       'more':'Другие категории','lang':'Română','call':'Контакты',
       'legal':'Актуальные цены и наличие уточняются при обращении. Изображения товаров могут быть иллюстративными.',
       'count':'Товаров в каталоге: {count}', 'new':'Недавно добавлено'}
}

def esc(v): return html.escape(str(v or ''),quote=True)
def compact(s): return ' '.join(str(s or '').split())
def slugify(value):
    raw=unicodedata.normalize('NFKD',str(value)).encode('ascii','ignore').decode('ascii').lower()
    return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',raw)).strip('-') or 'produs'
def safe_id(value): return re.sub(r'[^a-z0-9]+','-',str(value).lower()).strip('-') or 'item'
def page_path(cat, item, lang):
    # Use title from Romanian catalog for stable bilingual slugs.
    productslug=f"{slugify(item['title'])}-{safe_id(item['id'])}.html"
    prefix='ru/' if lang=='ru' else ''
    folder='console' if cat=='consoles' else cat
    return f"{prefix}produse/{folder}/{productslug}"
def category_path(cat,lang): return ('ru/' if lang=='ru' else '')+'categorii/'+cat+'.html'
def product_image(img):
    img=str(img or '').strip()
    if img.startswith('https://') or img.startswith('http://'): return img
    if img.startswith('/'):return SITE+img
    return SITE+'/'+img.lstrip('/') if img else SITE+'/media/play-spot-logo-v4.webp'
def price_value(price):
    s=compact(price)
    if not re.fullmatch(r'[\d,.]+\s+MDL',s,re.I): return None
    amt=s[:-3].strip().replace(',','')
    try:
        num=float(amt)
        if not 0<num<100000000:return None
        return round(num,2)
    except ValueError:return None

def jsdata(obj):return json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
def head(title,description,canonical,alternate,lang,img,extra_schema,ogtype='website'):
    other='ro' if lang=='ru' else 'ru'
    canonical_url=SITE+'/'+canonical
    other_url=SITE+'/'+alternate
    ro_url=canonical_url if lang=='ro' else other_url
    ru_url=canonical_url if lang=='ru' else other_url
    content_lang='ro_MD' if lang=='ro' else 'ru_MD'
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description[:165])}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{esc(canonical_url)}">
<link rel="alternate" hreflang="ro" href="{esc(ro_url)}">
<link rel="alternate" hreflang="ru" href="{esc(ru_url)}">
<link rel="alternate" hreflang="x-default" href="{esc(ro_url)}">
<link rel="icon" type="image/webp" href="/media/play-spot-logo-v4.webp">
<meta property="og:type" content="{esc(ogtype)}">
<meta property="og:locale" content="{content_lang}">
<meta property="og:site_name" content="PlaySpotStore">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description[:200])}">
<meta property="og:url" content="{esc(canonical_url)}">
<meta property="og:image" content="{esc(img)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description[:190])}">
<link rel="stylesheet" href="/seo/site.css?v=20261109-v30">
<link rel="stylesheet" href="/playspot-v27.css?v=seo29">
<script type="application/ld+json">{jsdata(extra_schema)}</script>
</head>'''

def nav(cat,lang):
    t=LABEL[lang]
    home='/ru.html' if lang=='ru' else '/'
    items=''.join(f'<a href="/{category_path(c,lang)}"'+(' aria-current="page"' if c==cat else '')+f'>{esc(CAT_RU[c] if lang=="ru" else CAT_RO[c])}</a>' for c in CATEGORIES)
    return f'''<header class="seo-header"><div class="seo-header-inner">
<a class="seo-brand" href="{home}" aria-label="PlaySpotStore"><img src="/media/play-spot-logo-v4.webp" alt="PlaySpotStore" width="54" height="54"><b>PlaySpotStore</b></a>
<nav class="seo-main-nav" aria-label="{esc(t['filters'])}">{items}</nav>
<a class="seo-header-contact" href="{home}#contact">{esc(t['call'])}</a>
</div></header>'''

def footer(lang):
    t=LABEL[lang];home='/ru.html' if lang=='ru' else '/'
    count_title='Посетители · 2026' if lang=='ru' else 'Vizitatori · 2026'
    return f'''<footer class="seo-footer"><div class="seo-footer-inner">
<a href="{home}">PlaySpotStore</a> <span>·</span> <a href="{home}#contact">{esc(t['call'])}</a>
<span>·</span> <span>{esc(t['legal'])}</span></div></footer>
<section class="p26-visitor-counter" aria-label="{esc(count_title)}"><div class="p26-inner"><span class="p26-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"/><path d="M3 21v-2a6 6 0 0 1 12 0v2M17 5a3 3 0 0 1 0 6M17 14a5 5 0 0 1 4 5v2"/></svg></span><div class="p26-copy"><strong>{esc(count_title)}</strong></div><strong class="p26-number" id="p26-total" aria-live="polite">—</strong></div></section>
<script defer src="/playspot-v27.js?v=seo29"></script>'''

def crumb(cat,lang,product=None):
    t=LABEL[lang];root='/ru.html' if lang=='ru' else '/';cp='/'+category_path(cat,lang)
    names=[(t['home'],root),(CAT_RU[cat] if lang=='ru' else CAT_RO[cat],cp)]
    if product: names.append((product,None))
    markup='<nav class="seo-breadcrumb" aria-label="'+esc(t['breadcrumb'])+'">'
    markup+=' <span class="sep">›</span> '.join(f'<a href="{esc(href)}">{esc(label)}</a>' if href else f'<span aria-current="page">{esc(label)}</span>' for label,href in names)
    return markup+'</nav>'

def breadcrumbs_schema(cat,lang,product=None,url=None):
    home=SITE+('/ru.html' if lang=='ru' else '/')
    parts=[('Главная' if lang=='ru' else 'Acasă',home),(CAT_RU[cat] if lang=='ru' else CAT_RO[cat],SITE+'/'+category_path(cat,lang))]
    if product:parts.append((product,SITE+'/'+url))
    return {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i,'name':n,'item':u} for i,(n,u) in enumerate(parts,1)]}

def product_card(it,cat,lang,ro_item):
    t=LABEL[lang];url='/'+page_path(cat,ro_item,lang)
    img=product_image(it.get('image'))
    pr=compact(it.get('price')) or t['ask']
    b='<span class="seo-new">'+esc(t['new'])+'</span>' if it.get('new_arrival')=='yes' else ''
    return f'''<article class="seo-product-card"><a href="{esc(url)}" aria-label="{esc(it['title'])}">
<div class="seo-product-art"><img loading="lazy" decoding="async" src="{esc(img)}" alt="{esc(it['title'])}" onerror="this.onerror=null;this.src='/media/play-spot-logo-v4.webp'">{b}</div>
<div class="seo-product-body"><h3>{esc(it['title'])}</h3><p class="seo-product-price">{esc(pr)}</p>
<span class="seo-product-details">{esc(t['details'])} <span aria-hidden="true">→</span></span></div></a></article>'''

def category_html(cat,lang,products,ro_products):
    t=LABEL[lang];catname=CAT_RU[cat] if lang=='ru' else CAT_RO[cat]
    url=category_path(cat,lang);alt=category_path(cat,'ro' if lang=='ru' else 'ru')
    desc=t['intro'].format(category=catname)
    title=f'{catname} în Moldova | PlaySpotStore' if lang=='ro' else f'{catname} в Молдове | PlaySpotStore'
    lst=[{'@type':'ListItem','position':i+1,'url':SITE+'/'+page_path(cat,ro,lang),'name':p['title']} for i,(p,ro) in enumerate(zip(products,ro_products))]
    schema={'@context':'https://schema.org','@graph':[
        {'@type':'CollectionPage','name':catname,'url':SITE+'/'+url,'description':desc,'inLanguage':lang,'mainEntity':{'@type':'ItemList','itemListElement':lst}},
        breadcrumbs_schema(cat,lang)]}
    page=head(title,desc,url,alt,lang,SITE+'/media/play-spot-logo-v4.webp',schema)
    cards=''.join(product_card(p,cat,lang,ro) for p,ro in zip(products,ro_products))
    other=''.join(f'<a href="/{category_path(c,lang)}">{esc(CAT_RU[c] if lang=="ru" else CAT_RO[c])}</a>' for c in CATEGORIES if c!=cat)
    return f'''{page}<body>{nav(cat,lang)}
<main class="seo-wrap">{crumb(cat,lang)}<section class="seo-category-hero"><p class="seo-eyebrow">PLAYSPOTSTORE · {esc(t['catalog'])}</p>
<h1>{esc(catname)}</h1><p>{esc(desc)}</p><div class="seo-result-count">{esc(t['count'].format(count=len(products)))}</div></section>
<section class="seo-list" aria-label="{esc(t['products'])}"><div class="seo-list-head"><h2>{esc(t['products'])}</h2><span>{len(products)} {esc(t['total'])}</span></div>
<div class="seo-grid">{cards}</div></section>
<section class="seo-more"><h2>{esc(t['more'])}</h2><div class="seo-chip-row">{other}</div></section></main>
{footer(lang)}</body></html>'''

def product_html(cat,lang,product,ro_item,related):
    t=LABEL[lang];catname=CAT_RU[cat] if lang=='ru' else CAT_RO[cat]
    path=page_path(cat,ro_item,lang);alt=page_path(cat,ro_item,'ru' if lang=='ro' else 'ro')
    title=f'{product["title"]} {catname} | PlaySpotStore'
    desc=compact(product.get('description'))
    if not desc:desc=t['single_desc'].format(title=product['title'],category=catname)
    # Keep catalog descriptions as-is; no generated/fake technical specifications.
    # Unique metadata even where source descriptions are generic placeholders.
    meta=t['single_desc'].format(title=product['title'],category=catname)+' '+desc
    img=product_image(product.get('image'))
    product_schema={'@type':'Product','name':product['title'],'url':SITE+'/'+path,'description':desc,
                    'image':[img],'category':catname}
    price=price_value(product.get('price'))
    if price is not None:
        product_schema['offers']={'@type':'Offer','url':SITE+'/'+path,'price':price,'priceCurrency':'MDL','seller':{'@type':'Organization','name':'PlaySpotStore'}}
        # Stock is unknown and must not be marked InStock.
    schema={'@context':'https://schema.org','@graph':[product_schema,breadcrumbs_schema(cat,lang,product['title'],path)]}
    more=''.join(product_card(p,cat,lang,r) for p,r in related[:4])
    price_text=compact(product.get('price')) or t['ask']
    wmsg=('Salut! Aș dori detalii și disponibilitate pentru: ' if lang=='ro' else 'Здравствуйте! Уточните, пожалуйста, наличие и цену: ')+product['title']+' ('+catname+'). '+SITE+'/'+path
    whatsapp='https://wa.me/37378890580?text='+quote(wmsg,safe='')
    instagram='https://www.instagram.com/PlaySpotStore/'
    from_catalog=t['new'] if product.get('new_arrival')=='yes' else 'PlaySpotStore'
    page=head(title,meta,path,alt,lang,img,schema,ogtype="product")
    return f'''{page}<body>{nav(cat,lang)}
<main class="seo-wrap">{crumb(cat,lang,product['title'])}
<article class="seo-detail"><div class="seo-detail-image"><img src="{esc(img)}" alt="{esc(product['title'])}" width="550" height="650" fetchpriority="high" decoding="async" onerror="this.onerror=null;this.src='/media/play-spot-logo-v4.webp'"></div>
<div class="seo-detail-info"><p class="seo-eyebrow">{esc(from_catalog)} · {esc(catname)}</p><h1>{esc(product['title'])}</h1>
<p class="seo-detail-description">{esc(desc)}</p>
<div class="seo-pricebox"><span>{esc(t['price'])}</span><strong>{esc(price_text)}</strong>
<p>{esc(t['confirm'])}</p></div>
<div class="seo-ctas"><a class="seo-cta-primary" href="{esc(whatsapp)}" target="_blank" rel="noopener noreferrer">{esc(t['whatsapp'])}</a>
<a class="seo-cta-secondary" href="{esc(instagram)}" target="_blank" rel="noopener noreferrer">{esc(t['instagram'])}</a></div>
<a class="seo-back" href="/{category_path(cat,lang)}">← {esc(catname)}</a></div></article>
<section class="seo-related"><h2>{esc(t['related'])}</h2><div class="seo-grid">{more}</div></section>
<section class="seo-more"><h2>{esc(t['more'])}</h2><div class="seo-chip-row">{''.join(f'<a href="/{category_path(c,lang)}">{esc(CAT_RU[c] if lang=="ru" else CAT_RO[c])}</a>' for c in CATEGORIES if c!=cat)}</div></section>
</main>{footer(lang)}</body></html>'''

def clean_home_header(s,lang):
    s=s.replace('https://www.playstationspot.store','https://playspotstore.online').replace('https://playstationspot.store','https://playspotstore.online')
    # Remove prior canonical/hreflang tags within <head> (including minified HTML).
    hd=s.index('</head>')
    headpart,tail=s[:hd],s[hd:]
    headpart=re.sub(r'[ \t]*<link\s+rel="canonical"[^>]*>\s*','',headpart,flags=re.I)
    headpart=re.sub(r'[ \t]*<link\s+rel="alternate"\s+hreflang="[^"]+"[^>]*>\s*','',headpart,flags=re.I)
    s=headpart+tail
    home=(SITE+'/' if lang=='ro' else SITE+'/ru.html')
    links=f'''  <link rel="canonical" href="{home}">
  <link rel="alternate" hreflang="ro" href="{SITE}/">
  <link rel="alternate" hreflang="ru" href="{SITE}/ru.html">
  <link rel="alternate" hreflang="x-default" href="{SITE}/">
'''
    homestyle='' if 'href="/seo/home.css"' in s else '  <link rel="stylesheet" href="/seo/home.css">\n'
    s=s.replace('</head>',homestyle+links+'</head>',1)
    return s

def home_update(s,lang,slugmap):
    t=LABEL[lang]
    s=clean_home_header(s,lang)
    # Existing header category links become crawlable routes instead of JS-only # popups.
    m=re.search(r'<ul id="main-menu">[\s\S]*?</ul>',s)
    if not m:raise ValueError('Cannot find home navigation in current HTML')
    header=m.group()
    for cat in CATEGORIES:
        navkey='console' if cat=='consoles' else cat
        cp='/'+category_path(cat,lang)
        header=re.sub(r'<a href="#" data-category-id="'+re.escape(navkey)+r'">',f'<a href="{cp}">',header)
        header=re.sub(r'<a href="#" onclick="event.preventDefault\(\);showPlatformNotice\(\''+re.escape(cat)+r'\'\)">',f'<a href="{cp}">',header)
    s=s[:m.start()]+header+s[m.end():]
    # Turn visual category tiles into normal HTML links. Original click-based helper remains in other sections.
    def tile(match):
        cat=match.group(1)
        url='/'+category_path('consoles' if cat=='console' else cat,lang)
        return '<a class="category-tile '+cat+'" href="'+url+'" aria-label="'+match.group(2)+'">'+match.group(3)+'</a>'
    s,num=re.subn(r'<button type="button" class="category-tile (ps4|ps5|nintendo|xbox|console|accessories)" onclick="[^"]+" aria-label="([^"]+)">([\s\S]*?)</button>',tile,s)
    if num!=6 and s.count('<a class="category-tile ')<6:raise ValueError('Expected six category tiles or existing SEO category anchors; found '+str(num))
    # Crawlable category discovery block; emitted in initial HTML so no JS rendering needed.
    intro=''.join(f'<a href="/{category_path(cat,lang)}"><strong>{esc(CAT_RU[cat] if lang=="ru" else CAT_RO[cat])}</strong><span aria-hidden="true">↗</span></a>' for cat in CATEGORIES)
    section=f'''\n<section class="p29-seo-discovery" id="catalog-seo" aria-labelledby="p29-catalog-title">
<div class="p29-seo-wrap"><h2 id="p29-catalog-title">{esc(t['explore'])}</h2><p>{esc(t['catalog_info'])}</p>
<div class="p29-seo-links">{intro}</div></div></section>\n'''
    if 'id="catalog-seo"' not in s:
        hero=s.index('<section class="hero"');end=s.index('</section>',hero)+len('</section>');s=s[:end]+section+s[end:]
    # Add a visible catalog link in the footer, backed by actual HTML pages.
    if 'href="#catalog-seo"' not in s:
        at=s.find('class="p8-links"')
        if at>=0:
            ed=s.find('</nav>',at)
            s=s[:ed]+f'<a href="#catalog-seo">{esc(t["catalog"])}</a>'+s[ed:]
    # Link existing JS-built product cards to permanent product pages. The modal functions remain fallback.
    function='''\nfunction p29ProductHref(game,cat) {
  const map=window.p29ProductSlugs || {};
  const slug=map[cat] && map[cat][String(game && game.id)];
  return slug ? ('/'''+('ru/' if lang=='ru' else '')+'''produse/' + cat + '/' + slug) : '#';
}
'''
    if 'function p29ProductHref' not in s:
        mark='/* ========== createProductCard ========== */'
        if mark not in s:raise ValueError('Cannot find product card builder')
        s=s.replace(mark,function+'\n'+mark,1)
    s=s.replace('link.href = "#";', 'link.href = p29ProductHref(game,cat);',1)
    s=s.replace('link2.href = "#";', 'link2.href = p29ProductHref(game,cat);',1)
    # Let regular anchors work; no JS-required clicks on product cards.
    block=re.compile(r'if \(link\) \{\s*e\.preventDefault\(\);\s*const id = link\.getAttribute\("data-id"\);\s*const cat = link\.getAttribute\("data-category"\);\s*openGame\(id, cat\);\s*\}')
    if block.search(s):
        s=block.sub('if (link && link.getAttribute("href") === "#") {\n    e.preventDefault();\n    openGame(link.getAttribute("data-id"),link.getAttribute("data-category"));\n  }',s,count=1)
    # Prevent the legacy data/categories.json loader from appending duplicate JS-only links
    # after we replace the existing menu links with static pages.
    old_check="if (mainMenu.querySelector('[data-category-id=\"' + cat.id + '\"]')) return;"
    new_check="if (mainMenu.querySelector('[data-category-id=\"' + cat.id + '\"], [href=\"/categorii/' + (cat.id === 'console' ? 'consoles' : cat.id) + '.html\"]')) return;"
    s=s.replace(old_check,new_check,1)
    # Convert legacy secondary category buttons into crawlable links too.
    def secondary_button(m):
        cat=m.group(1)
        target='consoles' if cat=='console' else cat
        return '<a href=\"/'+category_path(target,lang)+'\">'+m.group(2)+'</a>'
    if '<div class="p3-links">' in s:
        start=s.index('<div class="p3-links">');end=s.find('</div>',start)
        if end>=0:
            fragment=s[start:end]
            fragment=re.sub(r'<button type="button" onclick="(?:openCategoryModal|showPlatformNotice)\(\'(ps4|ps5|ps2|nintendo|xbox|console|accessories)\'\)">([\s\S]*?)</button>',secondary_button,fragment)
            s=s[:start]+fragment+s[end:]
    # Search suggestions currently open JS popup. If we can identify exact match, route to static page.
    if 'const seoDestination = p29ProductHref(r, cat);' not in s:
        s=s.replace('openGame(r.id, cat);','const seoDestination = p29ProductHref(r, cat);\n      if (seoDestination !== "#") window.location.assign(seoDestination);\n      else openGame(r.id, cat);',1)
    # Search dock (V24) is separate; will also be routed to pages by a small patch to that script.
    # Slugs are generated from the source-language titles; embed a lightweight id->slug map for RU compatibility.
    mapping=json.dumps(slugmap,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    script='<script>window.p29ProductSlugs='+mapping+';</script>\n'
    if 'window.p29ProductSlugs=' in s:
        s=re.sub(r'<script>window\.p29ProductSlugs=[^<]*;</script>\n',script,s,count=1)
    else:
        pos=s.index('<script>\n/* ========== HAMBURGER')
        s=s[:pos]+script+s[pos:]
    return s

def generate(root,check=False):
    root=root.resolve()
    if not (root/'index.html').exists() or not (root/'ru.html').exists():raise SystemExit('Error: Run from PlaySpotStore repo root (index.html and ru.html required)')
    collections={};slugmap={};total=0
    for cat in CATEGORIES:
        filename='consoles' if cat=='consoles' else cat
        ro=json.loads((root/'data'/f'{filename}.json').read_text(encoding='utf-8'))
        ru=json.loads((root/'data'/f'{filename}_ru.json').read_text(encoding='utf-8'))
        if not isinstance(ro,list) or not ro:raise ValueError(f'Missing products in {cat}')
        ruid={str(x['id']):x for x in ru}
        assert len(ruid)==len(ru),f'Duplicate RU IDs in {cat}'
        assert set(ruid)=={str(x['id']) for x in ro},f'RO/RU products differ in {cat}'
        assert len(set(str(x['id']) for x in ro))==len(ro),f'Duplicate IDs in {cat}'
        assert all(x.get('title') for x in ro),f'Missing titles in {cat}'
        itemsru=[ruid[str(p['id'])] for p in ro]
        slugmap['console' if cat=='consoles' else cat]={str(item['id']):f"{slugify(item['title'])}-{safe_id(item['id'])}.html" for item in ro}
        if len(set(slugmap['console' if cat=='consoles' else cat].values()))!=len(ro):raise ValueError(f'Colliding slugs in {cat}')
        collections[cat]=(ro,itemsru)
        total+=len(ro)
    if check:print(f'Catalog input verified: {total} products x 2 languages, {len(CATEGORIES)} categories x 2 languages');return
    manifest=root/'seo'/'generated-paths.json'
    old_paths=json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else []
    seo_dir=root/'seo';seo_dir.mkdir(exist_ok=True)
    shutil.copyfile(Path(__file__).with_name('seo.css'),seo_dir/'site.css')
    shutil.copyfile(Path(__file__).with_name('home.css'),seo_dir/'home.css')
    urls=['','ru.html']
    # Generate indexable category pages and all product pages, separate for both languages.
    for cat,(ro,ru) in collections.items():
        for lang,localized in [('ro',ro),('ru',ru)]:
            p=category_path(cat,lang);path=root/p;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(category_html(cat,lang,localized,ro),encoding='utf-8')
            urls.append(p)
        for idx,source in enumerate(ro):
            # Related products from same category, preferring adjacent items without duplicates.
            for lang,localized in [('ro',ro),('ru',ru)]:
                item=localized[idx]
                other=[(localized[j],ro[j]) for j in range(len(ro)) if j!=idx]
                path=page_path(cat,source,lang);target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(product_html(cat,lang,item,source,other[:4]),encoding='utf-8')
                urls.append(path)
    # Delete only pages previously generated by this tool that are no longer in the catalog.
    stale=set(old_paths)-set(x for x in urls if x)
    for rel in stale:
        if not isinstance(rel,str) or not (rel.startswith('produse/') or rel.startswith('ru/produse/') or rel.startswith('categorii/') or rel.startswith('ru/categorii/')) or not rel.endswith('.html'):continue
        f=root/rel
        if f.is_file():f.unlink()
    manifest.write_text(json.dumps([x for x in urls if x],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Resolve old on-site domain typo, link to real categories/products on both existing homepages.
    for lang,f in [('ro','index.html'),('ru','ru.html')]:
        path=root/f
        s=path.read_text(encoding='utf-8')
        s=home_update(s,lang,slugmap)
        path.write_text(s,encoding='utf-8')
    # If V24 floating search exists, direct result clicks to a real product page (popups kept as fallback).
    search_script=root/'playspot-v24.js'
    if search_script.exists():
        s=search_script.read_text(encoding='utf-8')
        orig="collapse();if(typeof window.openGame==='function')window.openGame(String(item.id),cat);"
        repl="collapse();const href=(window.p29ProductSlugs?.[cat]||{})[String(item.id)];if(href)window.location.assign('/'+(ru?'ru/':'')+'produse/'+cat+'/'+href);else if(typeof window.openGame==='function')window.openGame(String(item.id),cat);"
        if orig in s:search_script.write_text(s.replace(orig,repl,1),encoding='utf-8')
    (root/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+SITE+'/sitemap.xml\n',encoding='utf-8')
    # Do not fabricate lastmod timestamps; inventory records have no verified modified dates.
    ns='http://www.sitemaps.org/schemas/sitemap/0.9';xns='http://www.w3.org/1999/xhtml'
    ET.register_namespace('',ns);ET.register_namespace('xhtml',xns)
    rootxml=ET.Element(f'{{{ns}}}urlset')
    urlset=set(urls)
    for path in urls:
        node=ET.SubElement(rootxml,f'{{{ns}}}url');ET.SubElement(node,f'{{{ns}}}loc').text=SITE+'/'+path
        if path in ('','ru.html'):
            ro_url=SITE+'/';ru_url=SITE+'/ru.html'
        elif path.startswith('ru/'):
            ro_url=SITE+'/'+path[3:];ru_url=SITE+'/'+path
        else:
            ro_url=SITE+'/'+path;ru_url=SITE+'/ru/'+path
        for code,href in [('ro',ro_url),('ru',ru_url),('x-default',ro_url)]:
            ET.SubElement(node,f'{{{xns}}}link',{'rel':'alternate','hreflang':code,'href':href})
    tree=ET.ElementTree(rootxml)
    ET.indent(tree, space='  ', level=0)  # Human-readable XML; same URL entries for crawlers.
    tree.write(root/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    # V31 FIX: Retain the sitemap XSL viewer after regenerating the SEO pages.
    xml_file = root/'sitemap.xml'
    xml_text = xml_file.read_text(encoding='utf-8')
    xml_text = re.sub(r'<\?xml-stylesheet\b[^>]*\?>\s*', '', xml_text)
    xml_text = re.sub(r'^(<\?xml\b[^>]*\?>)',
                      r'\1\n<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>',
                      xml_text, count=1)
    xml_file.write_text(xml_text, encoding='utf-8')
    # Simple local checks; comprehensive tests in test-build script.
    for path in urls:
        if path and not (root/path).is_file():raise ValueError('Missing generated page '+path)
    print(f'✅ Generated {total*2} product pages, {len(CATEGORIES)*2} category pages, 2 homepages; sitemap URLs: {len(urls)}')
    print('✅ Fixed canonical domain, crawlable category links, RO/RU hreflang, Product JSON-LD, robots and sitemap')
    print('✅ All prices and product details are read from data/*.json; no fake review, stock or rating')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.',help='GitHub repository root');ap.add_argument('--check',action='store_true')
    args=ap.parse_args()
    generate(Path(args.root),args.check)
