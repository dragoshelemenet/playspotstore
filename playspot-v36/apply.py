#!/usr/bin/env python3
"""V36: integrate filters into 14 SEO category pages; preserve SEO and V35 homepage.

Idempotent, stdlib only. Optional --patch-generator ensures future V29 catalog
regenerations automatically apply this UI to freshly generated pages.
"""
from __future__ import annotations
import argparse
import html
import json
import re
from pathlib import Path

CATS = ('ps2', 'ps4', 'ps5', 'nintendo', 'xbox', 'consoles', 'accessories')
START = '<!-- P36 CATEGORY FILTER START -->'
END = '<!-- P36 CATEGORY FILTER END -->'
STYLE = '<link rel="stylesheet" href="/playspot-v36.css?v=20261109-v36">'
SCRIPT = '<script defer src="/playspot-v36.js?v=20261109-v36"></script>'
HOOK = '    # P36: keep search filters after each catalog regeneration\n    addon = root / "playspot-v36" / "apply.py"\n    if addon.is_file(): subprocess.run([sys.executable, str(addon), "--root", str(root)], check=True)\n'


def filter_markup(lang: str) -> str:
    ru = lang == 'ru'
    tr = {
        'heading': 'Поиск и фильтры' if ru else 'Cautare si filtre',
        'search': 'Поиск в этой категории' if ru else 'Cauta in aceasta categorie',
        'placeholder': 'Название игры или товара...' if ru else 'Nume joc sau produs...',
        'sort': 'Сортировка' if ru else 'Sorteaza dupa',
        'default': 'Порядок в каталоге' if ru else 'Ordinea din catalog',
        'price_asc': 'Цена: сначала дешёвые' if ru else 'Pret: crescator',
        'price_desc': 'Цена: сначала дорогие' if ru else 'Pret: descrescator',
        'az': 'Название: А–Я / A–Z' if ru else 'Nume: A–Z',
        'za': 'Название: Я–А / Z–A' if ru else 'Nume: Z–A',
        'newfirst': 'Сначала новые' if ru else 'Produse noi primele',
        'price': 'Цена (MDL)' if ru else 'Pret (MDL)',
        'min': 'Мин.' if ru else 'Min.',
        'max': 'Макс.' if ru else 'Max.',
        'under': 'До 300' if ru else 'Sub 300',
        'over': 'Свыше 800' if ru else 'Peste 800',
        'new': 'Только новинки' if ru else 'Doar produse noi',
        'priced': 'Только с ценой' if ru else 'Doar cu pret afisat',
        'loading': 'Загрузка результатов…' if ru else 'Se incarca rezultatele...',
        'reset': 'Сбросить фильтры' if ru else 'Reseteaza filtrele',
    }
    return f'''{START}
<section class="p36-filter-panel" aria-label="{tr['heading']}">
  <div class="p36-main">
    <label class="p36-field"><span class="p36-label">{tr['search']}</span>
      <span class="p36-search-shell"><span class="p36-search-icon" aria-hidden="true"><svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="10.9" cy="10.9" r="6.8"/><path d="m16 16 5 5"/></svg></span><input type="search" data-p36-search autocomplete="off" placeholder="{tr['placeholder']}" aria-label="{tr['search']}"></span>
    </label>
    <label class="p36-field"><span class="p36-label">{tr['sort']}</span><select data-p36-sort aria-label="{tr['sort']}">
      <option value="default">{tr['default']}</option><option value="price-asc">{tr['price_asc']}</option><option value="price-desc">{tr['price_desc']}</option><option value="name-asc">{tr['az']}</option><option value="name-desc">{tr['za']}</option><option value="new">{tr['newfirst']}</option>
    </select></label>
  </div>
  <div class="p36-extras">
    <div class="p36-field"><span class="p36-label">{tr['price']}</span>
      <div class="p36-price-controls"><input data-p36-min type="number" inputmode="numeric" min="0" step="1" placeholder="{tr['min']}" aria-label="{tr['price']} {tr['min']}"><span aria-hidden="true">—</span><input data-p36-max type="number" inputmode="numeric" min="0" step="1" placeholder="{tr['max']}" aria-label="{tr['price']} {tr['max']}"></div>
    </div>
    <div class="p36-price-presets" aria-label="{tr['price']}">
      <button type="button" class="p36-chip" data-p36-range="0:299" aria-pressed="false">{tr['under']}</button>
      <button type="button" class="p36-chip" data-p36-range="300:500" aria-pressed="false">300–500</button>
      <button type="button" class="p36-chip" data-p36-range="500:800" aria-pressed="false">500–800</button>
      <button type="button" class="p36-chip" data-p36-range="801:" aria-pressed="false">{tr['over']}</button>
    </div>
    <div class="p36-toggles"><label class="p36-toggle"><input type="checkbox" data-p36-new><span>{tr['new']}</span></label><label class="p36-toggle"><input type="checkbox" data-p36-priced><span>{tr['priced']}</span></label></div>
  </div>
  <div class="p36-bottom"><span data-p36-count class="p36-count" role="status" aria-live="polite">{tr['loading']}</span><button class="p36-reset" type="button" data-p36-reset>{tr['reset']}</button></div>
</section>
{END}'''


def new_description(title: str, lang: str) -> str:
    return (f'{title} la PlaySpotStore Moldova. Vezi titlurile din catalog si preturile afisate unde sunt disponibile.'
            if lang == 'ro' else
            f'{title} в PlaySpotStore Молдова. Каталог товаров с отдельными страницами и указанными ценами, где они доступны.')


def transform_category(source: str, lang: str, path: str) -> str:
    # Remove any previous V36 panel first, so repeated installation stays clean.
    source = re.sub(r'\s*' + re.escape(START) + r'.*?' + re.escape(END) + r'\s*', '', source, flags=re.S)
    source = re.sub(r'\s*<link rel="stylesheet" href="/playspot-v36\.css[^\"]*">', '', source)
    source = re.sub(r'\s*<script defer src="/playspot-v36\.js[^\"]*"></script>', '', source)
    hero = re.search(r'<section class="seo-category-hero">(?P<inside>.*?)</section>',source,re.S)
    if not hero: raise ValueError(f'{path}: no SEO category hero')
    h1 = re.search(r'<h1>(.*?)</h1>',hero.group('inside'),re.S)
    if not h1: raise ValueError(f'{path}: no category heading')
    title = html.unescape(re.sub(r'<[^>]+>', '', h1.group(1))).strip()
    inside = hero.group('inside')
    # Only remove boilerplate paragraph in the category hero – retain other text elsewhere.
    inside, removed = re.subn(r'(?s)(</h1>)\s*<p>.*?</p>',r'\1',inside,count=1)
    inside = re.sub(r'<div class="seo-result-count">.*?</div>', '', inside, count=1, flags=re.S)
    source = source[:hero.start('inside')] + inside + source[hero.end('inside'):]
    if 'class="seo-list"' not in source or 'class="seo-grid"' not in source:
        raise ValueError(f'{path}: missing crawlable product grid')
    source = re.sub(r'\s*</head>', '\n'+STYLE+'\n</head>', source, count=1)
    source, n = re.subn(r'\s*(<section class="seo-list")','\n'+filter_markup(lang)+'\n'+r'\1',source,count=1)
    if n != 1:raise ValueError(f'{path}: no place for filters')
    source = re.sub(r'\s*</body>', '\n'+SCRIPT+'\n</body>', source, count=1)
    # Refresh generic snippets without removing metadata used by Google.
    desc = html.escape(new_description(title, lang),quote=True)
    source = re.sub(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^\"]*(">)',lambda m:m.group(1)+desc+m.group(2),source)
    ld = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)',source,re.S)
    if ld:
        try:
            schema=json.loads(ld.group(2))
            if schema.get('@graph') and schema['@graph'][0].get('@type') == 'CollectionPage':
                schema['@graph'][0]['description']=new_description(title, lang)
                source=source[:ld.start(2)] + json.dumps(schema,ensure_ascii=False,separators=(',',':')).replace('</','<\\/') + source[ld.end(2):]
        except (ValueError,KeyError,TypeError) as e:
            raise ValueError(f'{path}: invalid schema JSON-LD: {e}') from e
    return source


def patch_generator(root:Path) -> bool:
    path=root/'playspot-v29'/'generate.py'
    if not path.is_file():raise FileNotFoundError(f'Missing generator: {path}')
    source=path.read_text(encoding='utf-8')
    if '# P36: keep search filters after each catalog regeneration' in source: return False
    anchor="    print(f'✅ Generated {total*2} product pages"
    idx=source.find(anchor)
    if idx < 0: raise RuntimeError('Unsupported V29 generator: cannot locate output hook safely')
    source=source[:idx]+HOOK+source[idx:]
    path.write_text(source,encoding='utf-8')
    return True


def apply(root:Path,with_generator:bool=False) -> int:
    root=root.resolve()
    if not (root/'index.html').is_file() or not (root/'ru.html').is_file():
        raise RuntimeError('Run in the PlaySpotStore repo root')
    changes={}
    for lang, prefix in [('ro','categorii'),('ru','ru/categorii')]:
        for cat in CATS:
            path=root/prefix/(cat+'.html')
            if not path.is_file():raise FileNotFoundError(f'Missing SEO category: {path}')
            old=path.read_text(encoding='utf-8')
            new=transform_category(old,lang,str(path.relative_to(root)))
            if new != old:changes[path]=new
    # Finish checks before writing any files.
    if with_generator: patch_generator(root)
    for path,new in changes.items():path.write_text(new,encoding='utf-8')
    print(f'V36 OK: {len(CATS)*2} RO/RU category pages checked, {len(changes)} updated; pages remain fully crawlable.')
    return len(changes)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',default='.')
    parser.add_argument('--patch-generator',action='store_true')
    args=parser.parse_args()
    apply(Path(args.root),args.patch_generator)
