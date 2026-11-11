#!/usr/bin/env python3
"""PlaySpotStore V44: specific Moldova SEO + truthful in-person/courier options.

Only updates initial, crawlable HTML: existing home, category and product pages.
Does not change prices, item conditions, inventory, reviews, URLs, Product schema,
canonical links, hreflang or sitemap. Idempotent, standard library only.
"""
from __future__ import annotations
import argparse
import html
import json
import re
import sys
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

CATS = ('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')
CATEGORY = {
 'ro': {'ps2':'Jocuri PS2','ps4':'Jocuri PS4','ps5':'Jocuri PS5','nintendo':'Jocuri Nintendo','xbox':'Jocuri Xbox','consoles':'Console PlayStation','accessories':'Accesorii gaming'},
 'ru': {'ps2':'Игры PS2','ps4':'Игры PS4','ps5':'Игры PS5','nintendo':'Игры Nintendo','xbox':'Игры Xbox','consoles':'Игровые консоли','accessories':'Игровые аксессуары'},
}
PLATFORM = {'ps2':'PS2','ps4':'PS4','ps5':'PS5','nintendo':'Nintendo','xbox':'Xbox','consoles':'PlayStation','accessories':'gaming'}
CSS = '<link rel="stylesheet" href="/playspot-v44.css?v=20261111-v44">'
START = '<!-- P44 MOLDOVA FULFILMENT START -->'
END = '<!-- P44 MOLDOVA FULFILMENT END -->'
SITE = 'https://playspotstore.online'
LANDING = {'ro':'jocuri-video-chisinau-moldova.html', 'ru':'ru/videoigry-kishinev-moldova.html'}
NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
XNS = 'http://www.w3.org/1999/xhtml'
HOME_META = {
 'ro': ('Jocuri noi și second-hand în Moldova | PlaySpotStore',
        'Jocuri PS4, PS5, Xbox și Nintendo noi sau second-hand în Moldova. Predare personală în Chișinău și livrare prin curier în alte orașe.'),
 'ru': ('Новые и б/у игры в Молдове | PlaySpotStore',
        'Игры для PS4, PS5, Xbox и Nintendo: новые и б/у в Молдове. Личная встреча в Кишинёве и доставка курьером в другие города.'),
}
HOME_BLOCK = {
 'ro': '''<section class="p44-fulfilment p44-home" id="livrare-moldova" aria-labelledby="p44-delivery-title">
<h2 id="p44-delivery-title">Predare în Chișinău și livrare în Moldova</h2>
<p>În Chișinău putem stabili o predare personală de comun acord. Pentru comenzi în restul Republicii Moldova, discutăm expedierea prin curier, inclusiv către Bălți, Orhei, Ungheni, Cahul, Soroca și Comrat.</p>
<p>Catalogul poate include jocuri noi sau second-hand (b/u), în funcție de exemplar. Înainte de comandă confirmăm starea, prețul, disponibilitatea, metoda și costul livrării. Nu există un punct fix de ridicare indicat pe site.</p>
<a href="/jocuri-video-chisinau-moldova.html">Mai multe despre cumpărare și livrare</a></section>''',
 'ru': '''<section class="p44-fulfilment p44-home" id="livrare-moldova" aria-labelledby="p44-delivery-title">
<h2 id="p44-delivery-title">Встреча в Кишинёве и доставка по Молдове</h2>
<p>В Кишинёве можно договориться о личной встрече для передачи заказа. Для других городов Республики Молдова обсуждаем доставку курьером, в том числе в Бельцы, Оргеев, Унгены, Кагул, Сороки и Комрат.</p>
<p>В каталоге бывают как новые игры, так и игры б/у — состояние зависит от конкретного экземпляра. Перед заказом уточняем состояние, цену, наличие, способ и стоимость доставки. Фиксированный пункт самовывоза на сайте не указан.</p>
<a href="/ru/videoigry-kishinev-moldova.html">Как купить игру и получить заказ</a></section>'''
}
CATEGORY_BLOCK = {
 'ro': '''<aside class="p44-fulfilment p44-category" aria-label="Predare și livrare">
<p><strong>Din Chișinău sau din alt oraș?</strong> Putem stabili o predare personală în Chișinău sau expedierea prin curier în Moldova. Confirmăm starea, prețul și condițiile înainte de comandă. <a href="/jocuri-video-chisinau-moldova.html">Cum funcționează livrarea</a></p></aside>''',
 'ru': '''<aside class="p44-fulfilment p44-category" aria-label="Получение и доставка">
<p><strong>В Кишинёве или другом городе?</strong> Возможна встреча в Кишинёве либо отправка курьером по Молдове. Состояние, цену и условия согласовываем до заказа. <a href="/ru/videoigry-kishinev-moldova.html">Как получить заказ</a></p></aside>''',
}
PRODUCT_BLOCK = {
 'ro': '''<aside class="p44-fulfilment p44-product" aria-label="Cum primești produsul">
<p><strong>Predare sau curier:</strong> putem stabili o predare personală în Chișinău sau livrare prin curier în Moldova. Confirmăm starea exemplarului (nou sau b/u, după caz), prețul și costul livrării înainte de comandă. <a href="/jocuri-video-chisinau-moldova.html">Detalii despre livrare</a></p></aside>''',
 'ru': '''<aside class="p44-fulfilment p44-product" aria-label="Получение товара">
<p><strong>Встреча или курьер:</strong> можно договориться о встрече в Кишинёве или доставке по Молдове. Перед заказом уточняем состояние экземпляра (новый или б/у), цену и стоимость доставки. <a href="/ru/videoigry-kishinev-moldova.html">Подробнее о доставке</a></p></aside>''',
}

def clean(s:str)->str:
 return ' '.join(str(s or '').split())

def truncate(s:str,n:int)->str:
 s=clean(s)
 if len(s)<=n:return s.rstrip(' .;,:')
 v=s[:n+1].rsplit(' ',1)[0].rstrip(' .;,:')
 return v if len(v)>=min(18,n) else s[:n].rstrip(' .;,:')

def product_title(title:str,cat:str,lang:str)->str:
 platform=PLATFORM[cat]
 name=clean(title)
 # Avoid repeating the platform if the product title already contains it.
 needs_platform=(cat!='accessories') and not re.search(r'(?<!\w)'+re.escape(platform)+r'(?!\w)',name,flags=re.I)
 suffix=(' '+platform) if needs_platform else ''
 if lang=='ro':
  normal=f'{name}{suffix} în Chișinău | PlaySpotStore'
  fallback=f'{name}{suffix} | PlaySpotStore Moldova'
 else:
  normal=f'{name}{suffix} в Кишинёве | PlaySpotStore'
  fallback=f'{name}{suffix} | PlaySpotStore Молдова'
 return normal if len(normal)<=82 else fallback

def product_meta(title:str,cat:str,desc:str,lang:str)->str:
 # Keep the V40/V42 invariant: 'title | localized category: real synopsis'.
 # V42 SEO descriptions are stored per item in the RO/RU catalog JSON, so an
 # existing SEO validator and any future generation can stay consistent.
 label=CATEGORY[lang][cat]
 prefix=f'{clean(title)} | {label}: '
 tail=('; Chișinău, curier Moldova.' if lang=='ro' else '; встреча в Кишинёве, курьер по Молдове.')
 budget=160-len(prefix)-len(tail)
 if budget<14:raise ValueError(f'Product title/category too long for honest unique metadata: {title!r}')
 snippet=truncate(desc,budget)
 if desc[:min(12,len(desc))] not in snippet:
  raise ValueError('Product synopsis vanished from meta: '+title)
 return prefix+snippet+tail

def category_title(cat:str,lang:str)->str:
 label=CATEGORY[lang][cat]
 if lang=='ro':return f'{label} în Chișinău | PlaySpotStore'
 return f'{label} в Кишинёве | PlaySpotStore'

def category_meta(cat:str,lang:str)->str:
 label=CATEGORY[lang][cat]
 if lang=='ro':
  return f'{label} la PlaySpotStore: descoperă catalogul în Chișinău și comandă cu livrare prin curier în Moldova. Verifică starea și disponibilitatea.'
 return f'{label} в PlaySpotStore: каталог для Кишинёва, доставка курьером по Молдове. Уточняйте состояние, цену и наличие перед заказом.'

def replace_html_metadata(source:str,title:str,description:str,where:str)->str:
 before,delim,after=source.partition('</head>')
 if not delim:raise ValueError(where+': no </head>')
 new_title=html.escape(title,quote=False)
 esc_desc=html.escape(description,quote=True)
 changes=(
  (r'(<title>)(.*?)(</title>)',new_title,True),
  (r'(<meta\s+name="description"\s+content=")(.*?)("\s*/?>)',esc_desc,True),
  (r'(<meta\s+property="og:title"\s+content=")(.*?)("\s*/?>)',html.escape(title,quote=True),False),
  (r'(<meta\s+property="og:description"\s+content=")(.*?)("\s*/?>)',esc_desc,False),
  (r'(<meta\s+name="twitter:title"\s+content=")(.*?)("\s*/?>)',html.escape(title,quote=True),False),
  (r'(<meta\s+name="twitter:description"\s+content=")(.*?)("\s*/?>)',esc_desc,False),
 )
 for regex,repl,required in changes:
  pat=re.compile(regex,re.S|re.I)
  matches=list(pat.finditer(before))
  if len(matches)!=1:
   if required or len(matches)>1:raise ValueError(f'{where}: expected 1 tag {regex}, found {len(matches)}')
   continue
  before=pat.sub(lambda m:m.group(1)+repl+m.group(3),before,count=1)
 if CSS not in before:before+='\n'+CSS+'\n'
 return before+delim+after

def update_block(s:str,markup:str,where:str,anchor:str,after:bool=False)->str:
 replacement=START+'\n'+markup+'\n'+END
 if START in s or END in s:
  if s.count(START)!=1 or s.count(END)!=1:raise ValueError(where+': corrupted V44 markers')
  return re.sub(re.escape(START)+r'.*?'+re.escape(END),lambda m:replacement,s,count=1,flags=re.S)
 if after:
  if s.count(anchor)!=1:raise ValueError(where+': missing or ambiguous insertion anchor')
  return s.replace(anchor,anchor+'\n'+replacement,1)
 if s.count(anchor)!=1:raise ValueError(where+': missing or ambiguous insertion anchor')
 return s.replace(anchor,replacement+'\n'+anchor,1)

def apply_home(s:str,lang:str)->str:
 title,desc=HOME_META[lang]
 s=replace_html_metadata(s,title,desc,'home '+lang)
 if s.count('id="catalog-seo"')!=1 or s.count('id="p29-catalog-title"')!=1:raise ValueError('home missing catalog discovery '+lang)
 # Find original SEO catalog section (not the video/animation hero).
 m=re.search(r'<section class="p29-seo-discovery"[^>]*>.*?</section>',s,re.S)
 if not m:raise ValueError('home missing p29 seo section '+lang)
 # The new section is added immediately after the existing crawlable catalog links.
 return update_block(s,HOME_BLOCK[lang],'home '+lang,m.group(0),after=True)

def apply_category(s:str,cat:str,lang:str)->str:
 where=f'category {cat} {lang}'
 s=replace_html_metadata(s,category_title(cat,lang),category_meta(cat,lang),where)
 if 'p37-integrated' not in s or 'seo-category-hero' not in s:raise ValueError(where+': V37 category filters missing')
 if f'<h1>{html.escape(CATEGORY[lang][cat])}</h1>' not in s:raise ValueError(where+': wrong category h1')
 return update_block(s,CATEGORY_BLOCK[lang],where,'<section class="seo-list"')

def apply_product(s:str,p:dict,cat:str,lang:str)->str:
 where=f'product {cat} {lang} {p["id"]}'
 title,desc=clean(p['title']),clean(p.get('description',''))
 if not title or not desc:raise ValueError(where+': empty title or description')
 s=replace_html_metadata(s,product_title(title,cat,lang),product_meta(title,cat,desc,lang),where)
 if s.count('class="p42-editorial"')!=1:raise ValueError(where+': V42 editorial section missing')
 if f'"sku":"{p["id"]}"' not in s:raise ValueError(where+': expected SKU missing')
 return update_block(s,PRODUCT_BLOCK[lang],where,'<div class="seo-pricebox">')

def patch_generator(s:str)->str:
 if 'P44_MOLDOVA_SEO_HOOK' in s:return s
 anchor='    print(f\'✅ Generated {total*2} product pages'
 if s.count(anchor)!=1:raise ValueError('Generator hook insertion anchor missing')
 hook='''    # P44_MOLDOVA_SEO_HOOK: restore local titles and delivery info after catalog rebuild.
    addon44 = root / 'playspot-v44' / 'patch.py'
    if addon44.is_file(): subprocess.run([sys.executable, str(addon44), '--root', str(root)], check=True)
'''
 return s.replace(anchor,hook+anchor,1)

def landing_html(root:Path,lang:str)->str:
 # A single useful service landing page, not a city-doorway URL variation.
 ru=lang=='ru';rel=LANDING[lang];other=LANDING['ro' if ru else 'ru']
 t={
  'title': ('Новые и б/у видеоигры в Кишинёве | PlaySpotStore' if ru else 'Jocuri noi și second-hand în Chișinău | PlaySpotStore'),
  'meta': ('Игры для PS4, PS5, PS2, Xbox и Nintendo в Молдове. Договоритесь о личной встрече в Кишинёве или обсудите доставку курьером.' if ru else 'Jocuri PS4, PS5, PS2, Nintendo și Xbox în Moldova. Predare personală în Chișinău prin înțelegere sau livrare prin curier în alte orașe.'),
  'h1': ('Купить видеоигры в Кишинёве с доставкой по Молдове' if ru else 'Jocuri video în Chișinău, cu livrare în Moldova'),
  'intro': ('В PlaySpotStore можно выбрать игры для PlayStation, Nintendo и Xbox. В каталоге встречаются как новые игры, так и игры б/у; состояние конкретного экземпляра уточняется до покупки. На этой странице собраны варианты получения заказа и ссылки на реальные товары.' if ru else 'La PlaySpotStore poți explora jocuri pentru PlayStation, Nintendo și Xbox. Unele exemplare pot fi noi, altele second-hand (b/u), iar starea fiecăruia se confirmă înainte de cumpărare. Aici găsești opțiunile de predare, livrare și linkuri către produsele din catalog.'),
  's1': ('Личная встреча в Кишинёве' if ru else 'Predare personală în Chișinău'),
  'p1': ('Для покупателей в Кишинёве можем согласовать личную встречу. Время и место оговариваются заранее; не предполагается, что у магазина есть открытая торговая точка для самовывоза.' if ru else 'Pentru cumpărătorii din Chișinău putem stabili o întâlnire pentru predare, de comun acord. Ora și locul se confirmă în conversație; această opțiune nu înseamnă că avem un magazin fizic deschis publicului.'),
  's2': ('Доставка курьером по Молдове' if ru else 'Livrare prin curier în Moldova'),
  'p2': ('Если вы в Бельцах, Оргееве, Унгенах, Кагуле, Сороках, Комрате или другом населённом пункте Молдовы, уточните возможность отправки курьером. Тариф, сроки и детали получения подтверждаем индивидуально до заказа.' if ru else 'Dacă ești în Bălți, Orhei, Ungheni, Cahul, Soroca, Comrat sau în altă localitate din Republica Moldova, poți întreba despre expedierea prin curier. Costul, timpul estimat și condițiile de livrare se confirmă individual, înainte de comandă.'),
  's3': ('Новые игры или б/у — зависит от товара' if ru else 'Jocuri noi sau second-hand, în funcție de exemplar'),
  'p3': ('Не все игры в каталоге имеют одинаковое состояние. Перед оплатой уточните, новый ли конкретный экземпляр или б/у, в каком он состоянии, что входит в комплект и актуальна ли цена.' if ru else 'Nu toate jocurile au aceeași stare. Înainte de plată, confirmă dacă exemplarul este nou sau folosit (b/u), starea discului ori a produsului, conținutul pachetului, prețul și disponibilitatea.'),
  's4': ('Каталог по платформам' if ru else 'Alege platforma'),
  's5': ('Примеры товаров из каталога' if ru else 'Exemple de produse din catalog'),
  's6': ('Как оформить заказ?' if ru else 'Cum comanzi?'),
  'p6': ('Откройте страницу интересующей игры, уточните наличие и состояние через WhatsApp или Instagram и согласуйте встречу либо отправку. Цены и стоимость доставки могут потребовать подтверждения.' if ru else 'Deschide pagina jocului dorit, contactează-ne prin WhatsApp sau Instagram pentru disponibilitate și stare, apoi stabilim împreună predarea sau livrarea. Prețurile și costul curierului se confirmă înainte de comandă.'),
  'home': ('Главная' if ru else 'Acasă'),
  'view': ('Смотреть игру' if ru else 'Vezi jocul'),
 }
 def esc2(x):return html.escape(str(x),quote=True)
 # Refer to existing, independently indexable pages, not synthetic product/city urls.
 prefix='/ru/' if ru else '/'
 links=''.join(f'<li><a href="{prefix}categorii/{cat}.html">{esc2(CATEGORY[lang][cat])}</a></li>' for cat in CATS)
 choices=[]
 for cat in ('ps4','ps5','nintendo','xbox'):
  items=json.loads((root/'data'/f'{cat}{"_ru" if ru else ""}.json').read_text(encoding='utf-8'))
  folder=root/('ru/produse' if ru else 'produse')/cat
  for item in items[:2]:
   pid=str(item['id'])
   matched=[]
   for page in folder.glob('*.html'):
    if f'"sku":"{pid}"' in page.read_text(encoding='utf-8'):
     matched.append(page)
   if len(matched)!=1:raise ValueError('Cannot locate a unique page for '+pid)
   choices.append((item['title'],CATEGORY[lang][cat],'/'+matched[0].relative_to(root).as_posix()))
 products=''.join(f'<li><a href="{esc2(link)}">{esc2(name)} — {esc2(catname)}</a></li>' for name,catname,link in choices)
 absolute=SITE+'/'+rel;other_absolute=SITE+'/'+other
 ro_href=SITE+'/'+LANDING['ro'];ru_href=SITE+'/'+LANDING['ru']
 schema=json.dumps({'@context':'https://schema.org','@graph':[{'@type':'WebPage','name':t['title'],'url':absolute,'inLanguage':lang,'description':t['meta']}]},ensure_ascii=False,separators=(',',':'))
 return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc2(t['title'])}</title><meta name="description" content="{esc2(t['meta'])}"><meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{esc2(absolute)}"><link rel="alternate" hreflang="ro" href="{esc2(ro_href)}"><link rel="alternate" hreflang="ru" href="{esc2(ru_href)}"><link rel="alternate" hreflang="x-default" href="{esc2(ro_href)}">
<meta property="og:title" content="{esc2(t['title'])}"><meta property="og:description" content="{esc2(t['meta'])}"><meta property="og:url" content="{esc2(absolute)}"><meta property="og:type" content="website">
<link rel="stylesheet" href="/seo/site.css"><link rel="stylesheet" href="/playspot-v44.css?v=20261111-v44">
<script type="application/ld+json">{schema}</script></head>
<body><main class="p44-guide"><nav class="p44-guide-nav" aria-label="Navigation"><a href="{'/ru.html' if ru else '/'}">{esc2(t['home'])}</a> · <a href="/{esc2(other)}" hreflang="{'ro' if ru else 'ru'}">{'Română' if ru else 'Русский'}</a></nav>
<article><h1>{esc2(t['h1'])}</h1><p class="p44-lead">{esc2(t['intro'])}</p>
<section><h2>{esc2(t['s1'])}</h2><p>{esc2(t['p1'])}</p></section>
<section><h2>{esc2(t['s2'])}</h2><p>{esc2(t['p2'])}</p></section>
<section><h2>{esc2(t['s3'])}</h2><p>{esc2(t['p3'])}</p></section>
<section><h2>{esc2(t['s4'])}</h2><ul class="p44-links">{links}</ul></section>
<section><h2>{esc2(t['s5'])}</h2><ul class="p44-links">{products}</ul></section>
<section><h2>{esc2(t['s6'])}</h2><p>{esc2(t['p6'])}</p><p><a href="https://wa.me/37378890580">WhatsApp</a> · <a href="https://www.instagram.com/PlaySpotStore/">Instagram</a></p></section>
</article></main></body></html>'''

def patch_sitemap(s:str)->str:
 ET.register_namespace('',NS);ET.register_namespace('xhtml',XNS)
 rootxml=ET.fromstring(s)
 current={n.findtext('{'+NS+'}loc') for n in rootxml.findall('{'+NS+'}url')}
 for lang,rel in LANDING.items():
  url=SITE+'/'+rel
  if url in current:continue
  node=ET.SubElement(rootxml,'{'+NS+'}url')
  ET.SubElement(node,'{'+NS+'}loc').text=url
  for code,href in [('ro',SITE+'/'+LANDING['ro']),('ru',SITE+'/'+LANDING['ru']),('x-default',SITE+'/'+LANDING['ro'])]:
   ET.SubElement(node,'{'+XNS+'}link',{'rel':'alternate','hreflang':code,'href':href})
 ET.indent(rootxml,space='  ')
 return '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n'+ET.tostring(rootxml,encoding='unicode')+'\n'

def patch_v29_validator(s:str)->str:
 old='    expected=count*2+len(CATS)*2+2'
 new='    expected=count*2+len(CATS)*2+4  # P44: two original local-service guide URLs'
 if new in s:return s
 if s.count(old)!=1:raise ValueError('V29 sitemap validation count anchor missing')
 return s.replace(old,new,1)

def patch_v32_human_sitemap(s:str)->str:
 if 'P44_GUIDE_SITEMAP' in s:return s
 old='    count=1\n    for path in urls:'
 new='''    # P44_GUIDE_SITEMAP: allow one useful service page per language.
    guide = ('ru/videoigry-kishinev-moldova.html' if ru else 'jocuri-video-chisinau-moldova.html')
    guide_link = None
    count=1
    for path in urls:'''
 if s.count(old)!=1:raise ValueError('V32 sitemap loop anchor missing')
 s=s.replace(old,new,1)
 old2='        if path==home: continue\n'
 new2='        if path==home: continue\n        if path==guide:\n            guide_link=path;count+=1;continue\n'
 if s.count(old2)!=1:raise ValueError('V32 home loop anchor missing')
 s=s.replace(old2,new2,1)
 old3="    page=f'''<!doctype html>"
 new3='    guide_heading=(\'Как купить игры в Молдове\' if ru else \'Cum cumperi jocuri în Moldova\')\n    guide_html=(f\'<section class="site-group"><header><h2><a href="/{guide_link}">{esc(guide_heading)}</a></h2></header></section>\' if guide_link else \'\')\n    page=f\'\'\'<!doctype html>'
 if s.count(old3)!=1:raise ValueError('V32 page anchor missing')
 s=s.replace(old3,new3,1)
 old4="{''.join(sections)}\n</main>"
 new4="{guide_html}\n{''.join(sections)}\n</main>"
 if s.count(old4)!=1:raise ValueError('V32 sections anchor missing')
 s=s.replace(old4,new4,1)
 return s

def plan(root:Path)->tuple[dict[Path,str],dict]:
 root=root.resolve();changes={};total=0
 def record(relative,updated):
  path=root/relative
  old=path.read_text(encoding='utf-8')
  if old!=updated:changes[path]=updated
 for filename,lang in [('index.html','ro'),('ru.html','ru')]:
  path=root/filename
  record(filename,apply_home(path.read_text(encoding='utf-8'),lang))
 for cat in CATS:
  for lang in ('ro','ru'):
   base=Path('ru') if lang=='ru' else Path('.')
   catpath=base/'categorii'/f'{cat}.html'
   record(catpath,apply_category((root/catpath).read_text(encoding='utf-8'),cat,lang))
   data_file=Path('data')/f'{cat}{"_ru" if lang=="ru" else ""}.json'
   data=json.loads((root/data_file).read_text(encoding='utf-8'))
   for item in data:
    item['seo_meta_description']=product_meta(item['title'],cat,item['description'],lang)
   record(data_file,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
   if len(data)==0:raise ValueError(f'No products in {cat} {lang}')
   directory=root/base/'produse'/('console' if cat=='consoles' else cat)
   pages={}
   for path in directory.glob('*.html'):
    source=path.read_text(encoding='utf-8')
    m=re.search(r'"sku"\s*:\s*"([^"]+)"',source)
    if not m:raise ValueError(f'No SKU found in {path}')
    if m.group(1) in pages:raise ValueError(f'Duplicate SKU {m.group(1)}')
    pages[m.group(1)]=path
   products={str(p['id']):p for p in data}
   if set(products)!=set(pages):raise ValueError(f'{cat} {lang}: catalog/page IDs mismatch ({len(products)}, {len(pages)})')
   for pid,p in products.items():
    path=pages[pid]
    record(path.relative_to(root),apply_product(path.read_text(encoding='utf-8'),p,cat,lang))
   if lang=='ro':total+=len(products)
 gp=Path('playspot-v29/generate.py')
 record(gp,patch_generator((root/gp).read_text(encoding='utf-8')))
 # Add one original, useful shopping/delivery page for each language.
 for lang,rel in LANDING.items():
  record(Path(rel),landing_html(root,lang)) if (root/rel).is_file() else changes.__setitem__(root/rel,landing_html(root,lang))
 # Ensure both canonical pages are discoverable from the XML and human sitemaps.
 sitemap=Path('sitemap.xml')
 record(sitemap,patch_sitemap((root/sitemap).read_text(encoding='utf-8')))
 p29=Path('playspot-v29/validate.py')
 record(p29,patch_v29_validator((root/p29).read_text(encoding='utf-8')))
 p32=Path('playspot-v32/human_sitemap.py')
 record(p32,patch_v32_human_sitemap((root/p32).read_text(encoding='utf-8')))
 if total<200:raise ValueError('Unexpectedly small product catalog')
 return changes,{'products':total,'product_pages':total*2,'category_pages':14,'homepages':2,'changed_files':len(changes)}

def main(root:Path,check:bool):
 changes,stats=plan(root)
 print(('V44 PREVIEW' if check else 'V44 SEO')+': '+str(stats))
 if check:return
 for path,s in changes.items():
  path.parent.mkdir(parents=True,exist_ok=True)
  path.write_text(s,encoding='utf-8')
 subprocess.run([sys.executable,'-B',str(root/'playspot-v32/human_sitemap.py'),'--root',str(root)],check=True)


if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--check',action='store_true')
 args=p.parse_args();main(Path(args.root),args.check)
