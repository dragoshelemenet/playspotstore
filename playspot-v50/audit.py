#!/usr/bin/env python3
"""V50 offline SEO audit of the deployed-to-GitHub static site.

This does not check Google's index or remote HTTP status; those require GSC/live crawls.
No fabricated scores, rankings, traffic, or publication dates.
"""
from __future__ import annotations
import argparse
import collections
import html
import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

from quality import CATS, META_LIMIT, image_alt

SITE='https://playspotstore.online/'
NS={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','x':'http://www.w3.org/1999/xhtml'}
TITLE=re.compile(r'<title>(.*?)</title>',re.I|re.S)
META=re.compile(r'<meta\s+name="description"\s+content="([^"]*)"',re.I)
CANONICAL=re.compile(r'<link\s+rel="canonical"\s+href="([^"]*)"',re.I)
JSONLD=re.compile(r'<script type="application/ld\+json">(.*?)</script>',re.S)
HERO=re.compile(r'<div class="seo-detail-image"><img\b[^>]*\balt="([^"]*)"')
IMAGE=re.compile(r'<div class="seo-detail-image"><img\b[^>]*\bsrc="([^"]*)"')


def get_html(s:str,pat:re.Pattern)->str|None:
    m=pat.search(s)
    return html.unescape(m.group(1)) if m else None


def audit(root:Path)->dict:
    root=root.resolve()
    doc=ET.parse(root/'sitemap.xml')
    pages=doc.findall('.//s:url',NS)
    canonical_paths=set()
    errors=[];warnings=[]
    url_count=0;product_count=0;categories=0;image_hosts=collections.Counter()
    image_missing=[];missing_targets=[]
    meta_seen={'ro':set(),'ru':set()}
    for node in pages:
        loc=node.find('s:loc',NS)
        if loc is None or not loc.text or not loc.text.startswith(SITE):
            errors.append('Unexpected sitemap loc');continue
        rel=loc.text[len(SITE):]
        url_count+=1
        if rel in canonical_paths:errors.append('Duplicate sitemap URL '+rel)
        canonical_paths.add(rel)
        file=root/(rel or 'index.html')
        if not file.is_file():errors.append('Sitemap URL missing file '+rel);continue
        body=file.read_text(encoding='utf-8')
        canonical=get_html(body,CANONICAL)
        if canonical!=loc.text:errors.append('Canonical mismatch '+rel)
        if len(node.findall('x:link',NS))!=3:errors.append('Sitemap hreflang count '+rel)
        if re.search(r'<meta\s+name="robots"[^>]*noindex',body,re.I):errors.append('Unexpected noindex '+rel)
        title=get_html(body,TITLE);meta=get_html(body,META)
        if not title:errors.append('Missing title '+rel)
        if not meta:errors.append('Missing meta description '+rel)
        if meta and len(meta)>META_LIMIT+5:warnings.append('Long meta description '+rel)
        if '<h1>' not in body:errors.append('Missing H1 '+rel)
        if rel.startswith('produse/') or rel.startswith('ru/produse/'):
            product_count+=1
            lang='ru' if rel.startswith('ru/') else 'ro'
            if meta:
                if meta in meta_seen[lang]:errors.append('Duplicate product meta '+rel)
                meta_seen[lang].add(meta)
            try:
                match=JSONLD.search(body)
                if not match:raise ValueError('No JSON-LD')
                data=json.loads(match.group(1))
                products=[x for x in data.get('@graph',[]) if x.get('@type')=='Product']
                if len(products)!=1:raise ValueError('Product not unique in @graph')
                prod=products[0]
                if prod.get('url')!=loc.text:errors.append('Product schema URL mismatch '+rel)
                if not prod.get('sku') or not prod.get('name'):errors.append('Product SKU/name missing '+rel)
                if 'aggregateRating' in prod or 'review' in prod:errors.append('Unverified rating or review '+rel)
                if 'offers' in prod and not isinstance(prod['offers'].get('price'),(int,float)):
                    errors.append('Non-numeric offer price '+rel)
            except (ValueError,KeyError,TypeError) as exc:errors.append('Product JSON-LD error '+rel+': '+str(exc))
            img=get_html(body,IMAGE)
            if not img:errors.append('Missing hero image '+rel)
            else:
                parts=urllib.parse.urlparse(img)
                host=parts.netloc.casefold() or 'relative'
                image_hosts[host]+=1
                if host in ('playspotstore.online','www.playspotstore.online','relative'):
                    local_img=root/urllib.parse.unquote(parts.path).lstrip('/')
                    if not local_img.is_file():image_missing.append(f'{rel}: {parts.path}')
            if not get_html(body,HERO):errors.append('Missing hero image alt '+rel)
        elif rel.startswith('categorii/') or rel.startswith('ru/categorii/'):
            categories+=1
        # Only check actual crawlable .html anchors and skip action hashes + external URLs.
        if rel.startswith(('produse/','ru/produse/','categorii/','ru/categorii/')):
            for href in re.findall(r'<a\s[^>]*href="([^"]+)"',body,re.I):
                target=html.unescape(href).split('#',1)[0].split('?',1)[0]
                if target.startswith('/') and target.endswith('.html') and not (root/target.lstrip('/')).is_file():
                    missing_targets.append(f'{rel} → {target}')
    if url_count != 576:errors.append(f'Expected 576 canonical URLs, found {url_count}')
    if product_count != 558:errors.append(f'Expected 558 product URLs, found {product_count}')
    if categories!=14:errors.append(f'Expected 14 category URLs, found {categories}')
    if image_missing:warnings.append(f'{len(image_missing)} missing LOCAL images (verify paths before deployment)')
    if missing_targets:errors.extend('Broken link '+link for link in missing_targets[:50])
    robots=(root/'robots.txt').read_text(encoding='utf-8')
    if 'Allow: /' not in robots or SITE+'sitemap.xml' not in robots:
        errors.append('robots.txt must allow crawling and link to sitemap')
    return {
      'site': SITE.rstrip('/'),
      'method': 'Offline audit of repository HTML, not a live Google Search Console index check',
      'sitemap_urls':url_count,
      'product_pages':product_count,
      'category_pages':categories,
      'other_pages':url_count-product_count-categories,
      'hero_image_hosts':dict(sorted(image_hosts.items(),key=lambda x:(-x[1],x[0]))),
      'missing_local_images':image_missing[:50],
      'broken_internal_links':missing_targets[:50],
      'errors':errors,
      'warnings':warnings,
    }


def markdown(report:dict)->str:
    lines=[
      '# PlaySpotStore V50 — audit SEO tehnic',
      '',
      '**Acesta este un audit al fișierelor statice.** Nu verifică pozițiile Google, starea indexării în Search Console sau dacă imaginile externe răspund HTTP 200.',
      '',
      f'- URL-uri canonice în sitemap: **{report["sitemap_urls"]}**',
      f'- Pagini produse: **{report["product_pages"]}**',
      f'- Pagini categorii: **{report["category_pages"]}**',
      f'- Alte pagini: **{report["other_pages"]}**',
      f'- Probleme blocante detectate în fișiere: **{len(report["errors"])}**',
      f'- Atenționări: **{len(report["warnings"])}**',
      '',
      '## Surse de imagini ale produselor',
    ]
    for host,count in report['hero_image_hosts'].items():lines.append(f'- `{host}`: {count} pagini')
    lines.extend(['','## Verificări suplimentare utile','',
      '1. Verifică în Google Search Console → Indexare → Pagini diferența dintre pagini descoperite și indexate; sitemap acceptat ≠ indexate.',
      '2. Inspectează câteva URL-uri reprezentative din fiecare categorie cu URL Inspection / Rich Results Test.',
      '3. Verifică manual încărcarea imaginilor externe; auditul offline nu poate testa domeniile terțe.',
      '4. Pentru jocuri noi/b-u, preț și disponibilitate: adaugă valori structurate doar după confirmarea exemplarelor. Nu inventa ratinguri.',
      '5. Evită o altă migrare a URL-urilor sau keyword stuffing cât Google procesează primele 576 de pagini.',''])
    if report['warnings']:
        lines.extend(['## Atenționări','']+['- '+w for w in report['warnings']]+[''])
    if report['errors']:
        lines.extend(['## Probleme','']+['- '+w for w in report['errors']]+[''])
    return '\n'.join(lines)+'\n'


def main(root:Path,write:bool=True)->None:
    report=audit(root)
    if write:
        folder=root/'playspot-v50'
        folder.mkdir(parents=True,exist_ok=True)
        (folder/'AUDIT.md').write_text(markdown(report),encoding='utf-8')
        (folder/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('V50 AUDIT: '+str({k:report[k] for k in ('sitemap_urls','product_pages','category_pages')}))
    print('V50 AUDIT: '+str(len(report['errors']))+' errors, '+str(len(report['warnings']))+' warnings')
    if report['errors']:
        raise SystemExit('V50 SEO audit failed: '+repr(report['errors'][:7]))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--check',action='store_true')
    a=p.parse_args();main(Path(a.root).resolve(),write=not a.check)
