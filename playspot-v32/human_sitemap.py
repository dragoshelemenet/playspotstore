#!/usr/bin/env python3
"""Generate separate plain-HTML RO/RU sitemap pages from the canonical XML sitemap.

Every product/category link is a standard server-served anchor; no JavaScript.
Never invent products or URLs. Rerunnable whenever the JSON catalogs change.
"""
from __future__ import annotations
import argparse
import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit, unquote

SITE = 'https://playspotstore.online'
SITEMAP_NS = {'sm':'http://www.sitemaps.org/schemas/sitemap/0.9'}
CATS = ['ps2','ps4','ps5','nintendo','xbox','consoles','accessories']
NAMES = {
    'ro': {'ps2':'Jocuri PS2','ps4':'Jocuri PS4','ps5':'Jocuri PS5',
           'nintendo':'Jocuri Nintendo','xbox':'Jocuri Xbox','consoles':'Console PlayStation','accessories':'Accesorii gaming'},
    'ru': {'ps2':'Игры PS2','ps4':'Игры PS4','ps5':'Игры PS5',
           'nintendo':'Игры Nintendo','xbox':'Игры Xbox','consoles':'Игровые консоли','accessories':'Аксессуары'}
}

def esc(s): return html.escape(str(s), quote=True)

def title_from_html(root, rel):
    if not rel: return 'PlaySpotStore'
    page=root/rel
    if not page.is_file():
        raise ValueError(f'XML sitemap references a missing page: {rel}')
    text=page.read_text(encoding='utf-8')
    m=re.search(r'<h1\b[^>]*>(.*?)</h1>',text,flags=re.S|re.I)
    if not m: m=re.search(r'<title\b[^>]*>(.*?)</title>',text,flags=re.S|re.I)
    if not m:
        raise ValueError(f'No page title: {rel}')
    return html.unescape(re.sub(r'<[^>]*>', '', m.group(1))).strip()

def load_sitemap(root):
    doc=ET.parse(root/'sitemap.xml')
    links=[]
    for node in doc.findall('sm:url', SITEMAP_NS):
        element=node.find('sm:loc',SITEMAP_NS)
        if element is None or not element.text or not element.text.startswith(SITE+'/'):
            raise ValueError('A sitemap URL is not on the official domain')
        url=element.text
        path=urlsplit(url).path.lstrip('/')
        if urlsplit(url).query or urlsplit(url).fragment:
            raise ValueError('Sitemap URLs should not have query strings or fragments')
        if path and not (root/path).is_file():
            raise ValueError('Sitemap URL points to nonexistent HTML: '+path)
        links.append(path)
    if len(links)!=len(set(links)):
        raise ValueError('Duplicate sitemap URL')
    return links

def build_page(root,urls,lang):
    ru=lang=='ru'
    pref='ru/' if ru else ''
    home='ru.html' if ru else ''
    main_links=[x for x in urls if x==home]
    if len(main_links)!=1:
        raise ValueError('Could not find language homepage in XML')
    records={cat:[] for cat in CATS}
    categories={cat:None for cat in CATS}
    # P44_GUIDE_SITEMAP: allow one useful service page per language.
    guide = ('ru/videoigry-kishinev-moldova.html' if ru else 'jocuri-video-chisinau-moldova.html')
    guide_link = None
    count=1
    for path in urls:
        is_russian = (path == 'ru.html' or path.startswith('ru/'))
        if is_russian != ru:
            continue
        if path==home: continue
        if path==guide:
            guide_link=path;count+=1;continue
        if path.startswith(pref+'categorii/'):
            cat=path.removeprefix(pref+'categorii/').removesuffix('.html')
            if cat not in categories: raise ValueError('Unknown category: '+cat)
            categories[cat]=path
            count+=1
        elif path.startswith(pref+'produse/'):
            chunks=path.removeprefix(pref+'produse/').split('/')
            product_cat='consoles' if len(chunks)==2 and chunks[0]=='console' else chunks[0]
            if len(chunks)!=2 or product_cat not in records: raise ValueError('Unexpected product path '+path)
            records[product_cat].append((path,title_from_html(root,path)))
            count+=1
        else:
            raise ValueError('Unexpected URL path: '+path)
    if any(not p for p in categories.values()):raise ValueError('A catalog category is missing from the XML sitemap')

    total_prod=sum(len(v) for v in records.values())
    total_urls=len(urls)
    sitemap_url='/ru/sitemap.html' if ru else '/sitemap.html'
    alternate='/sitemap.html' if ru else '/ru/sitemap.html'
    home_url='/ru.html' if ru else '/'
    heading='Карта сайта' if ru else 'Harta site-ului'
    subtitle=('Полный список страниц магазина PlaySpotStore. Все ссылки ведут прямо на страницы товаров и категорий.'
         if ru else 'Lista completă a paginilor PlaySpotStore. Fiecare link duce direct la pagina produsului sau a categoriei.')
    label_xml='XML для поисковых систем' if ru else 'XML pentru motoarele de căutare'
    label_categories='Категории' if ru else 'Categorii'
    label_product='Товаров' if ru else 'Produse'
    label_home='Главная' if ru else 'Acasă'
    label_other='Română' if ru else 'Русский'
    labels_count=('URL-uri în sitemap-ul XML' if not ru else 'URL в XML-карте')
    other_lang='ro' if ru else 'ru'

    toc=''.join(f'<a href="#cat-{esc(cat)}">{esc(NAMES[lang][cat])}<span>{len(records[cat])}</span></a>' for cat in CATS)
    sections=[]
    for cat in CATS:
        items='\n'.join(f'<li><a href="/{esc(rel)}">{esc(title)}</a></li>' for rel,title in records[cat])
        sections.append(f'''<section class="site-group" id="cat-{esc(cat)}" aria-labelledby="cat-title-{esc(cat)}">
<header><h2 id="cat-title-{esc(cat)}"><a href="/{esc(categories[cat])}">{esc(NAMES[lang][cat])}</a></h2><span>{len(records[cat])} {label_product}</span></header>
<ul class="link-grid">{items}</ul></section>''')

    guide_heading=('Как купить игры в Молдове' if ru else 'Cum cumperi jocuri în Moldova')
    guide_html=(f'<section class="site-group"><header><h2><a href="/{guide_link}">{esc(guide_heading)}</a></h2></header></section>' if guide_link else '')
    page=f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(heading)} | PlaySpotStore</title>
<meta name="description" content="{esc(subtitle)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{SITE}{sitemap_url}">
<link rel="alternate" hreflang="ro" href="{SITE}/sitemap.html">
<link rel="alternate" hreflang="ru" href="{SITE}/ru/sitemap.html">
<link rel="alternate" hreflang="x-default" href="{SITE}/sitemap.html">
<link rel="stylesheet" href="/playspot-v32/sitemap.css">
</head><body>
<header class="site-head"><div><a href="{home_url}" class="brand"><img width="45" height="45" src="/media/play-spot-logo-v4.webp" alt=""><strong>PlaySpotStore</strong></a>
<nav><a href="{home_url}">{label_home}</a><a href="{alternate}" lang="{other_lang}">{label_other}</a></nav></div></header>
<main class="site-wrap"><p class="eyebrow">PLAYSPOTSTORE · SEO</p><h1>{esc(heading)}</h1><p class="intro">{esc(subtitle)}</p>
<div class="site-meta"><span><strong>{total_urls}</strong> {esc(labels_count)}</span><span><strong>{total_prod}</strong> {label_product}</span><a href="/sitemap.xml">{label_xml}</a></div>
<h2>{label_categories}</h2><nav class="toc" aria-label="{label_categories}">{toc}</nav>
<section class="site-group" id="site-home"><header><h2><a href="{home_url}">{label_home} · PlaySpotStore</a></h2></header></section>
{guide_html}
{''.join(sections)}
</main><footer class="site-foot"><a href="{home_url}">PlaySpotStore</a><a href="/sitemap.xml">sitemap.xml</a></footer>
</body></html>'''
    dest=root/sitemap_url.lstrip('/')
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(page,encoding='utf-8')
    print(f'V32: generated {sitemap_url} with {count} crawlable HTML-page links ({total_prod} products)')
    return count

def build(root):
    root=root.resolve()
    links=load_sitemap(root)
    ro=build_page(root,links,'ro')
    ru=build_page(root,links,'ru')
    if ro+ru!=len(links):
        raise ValueError(f'HTML sitemaps cover {ro+ru}/{len(links)} XML URLs')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.')
    args=ap.parse_args()
    build(Path(args.root))
