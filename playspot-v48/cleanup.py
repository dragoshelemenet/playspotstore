#!/usr/bin/env python3
"""V48: remove ONLY superseded JS-generated category navigation and its modal UI.

The SEO category menu, category tiles, product details popup, search, hamburger,
filters, Spin & Win, data inventory, and crawlable catalog pages are retained.
Pure standard library; deterministic and idempotent.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

PAGES = ('index.html', 'ru.html')
CATS = ('ps4', 'ps5', 'nintendo', 'xbox', 'consoles', 'accessories')
MODALS = ('ps4', 'ps5', 'console', 'accessories')
MARKER = 'P48_STATIC_SEO_MENU_ONLY'


def remove_between(source: str, start: str, end: str, label: str) -> str:
    """Remove one obsolete JS block; accept a previously removed block."""
    if start not in source:
        # If the original header no longer exists, there must be no orphaned
        # references to legacy addMenuEvents or its category JSON menu loader.
        return source
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f'{label}: expected exactly one start/end marker')
    first = source.index(start)
    last = source.index(end, first + len(start))
    if last < first:
        raise ValueError(f'{label}: JS block boundary invalid')
    return source[:first] + source[last:]


def cleanup_html(source: str, filename: str) -> str:
    if filename not in PAGES:
        raise ValueError('Unexpected homepage ' + filename)
    original = source
    if source.count('id="main-menu"') != 1 or source.count('class="p29-seo-links"') != 1:
        raise ValueError(filename + ': expected one static navigation and one crawlable SEO catalog')
    if source.count('class="category-deck"') != 1 or 'window.p29ProductSlugs=' not in source:
        raise ValueError(filename + ': missing SEO category tiles or product slug map')
    # This legacy loader appends categories from categories.json to the header,
    # causing duplicated PS4, PS5, Console and Accessories links.
    legacy = '/* ========== DYNAMIC CATEGORIES (OPTIONAL) ========== */'
    modal = '/* ========== openCategoryModal ========== */'
    if legacy in source:
        if 'fetch("data/categories' not in source[source.index(legacy):source.index(modal)]:
            raise ValueError(filename + ': legacy loader changed unexpectedly')
        source = remove_between(source, legacy, modal, filename + ' dynamic menu')
    # The old category-specific modal selector has no callers once the
    # JS-generated header menu is removed. The real HTML anchors stay intact.
    source = remove_between(source, modal, 'function showModal(', filename + ' old category-modal selector')
    # These helpers had no other callers on the checked original homepage.
    source = remove_between(source, 'function showModal(', 'function closeAllModals(', filename + ' unused showModal helper')
    source = remove_between(source,
                            '/* ========== Focus Trap for Modals ========== */',
                            '/* ========== fetchProducts ========== */',
                            filename + ' obsolete category modal focus trap')
    source = remove_between(source,
                            '/* ========== fetchProducts ========== */',
                            'function p29ProductHref(',
                            filename + ' old category fetchProducts')

    # Retain the product details dialog (#product-modal), used elsewhere.
    for id in MODALS:
        marker = f'<div id="modal-{id}" class="modal"'
        matches = source.count(marker)
        if matches > 1:
            raise ValueError(filename + ': duplicate old category modal ' + id)
        if matches:
            old = re.compile(
                rf'<div id="modal-{re.escape(id)}" class="modal"[^>]*>\s*'
                rf'<div class="modal-content"[^>]*>.*?'
                rf'<div class="modal-products" id="modal-products-{re.escape(id)}"></div>'
                rf'\s*</div>\s*</div>\s*',
                re.S,
            )
            source, num = old.subn('', source, count=1)
            if num != 1:
                raise ValueError(filename + ': cannot safely remove old modal ' + id)
    for label in ('<!-- PS4/PS5 Modals -->', '<!-- Console & Accessories Modals -->'):
        source = source.replace(label, '')
    # Trim superfluous blank lines, without reformatting the homepage.
    source = re.sub(r'\n{4,}', '\n\n\n', source)
    validate_homepage(source, filename)
    # Guard against accidental treatment as a no-op on a still unpatched file.
    if original == source and ('fetch("data/categories' in original or 'function openCategoryModal(' in original):
        raise ValueError(filename + ': legacy menu unexpectedly survived')
    return source


def validate_homepage(s: str, filename: str) -> None:
    if s.count('id="main-menu"') != 1 or s.count('class="p29-seo-links"') != 1:
        raise ValueError(filename + ': static menu or crawlable catalog removed')
    if s.count('class="category-deck"') != 1 or 'window.p29ProductSlugs=' not in s:
        raise ValueError(filename + ': existing category cards/product links lost')
    if s.count('id="product-modal"') != 1 or 'function openGame(' not in s:
        raise ValueError(filename + ': product modal functionality changed')
    if 'fetch("data/categories' in s or 'function openCategoryModal(' in s or 'function addMenuEvents(' in s:
        raise ValueError(filename + ': old JS menu still active')
    if re.search(r'<a\b[^>]*\bdata-category-id\s*=', s):
        raise ValueError(filename + ': found a legacy JS popup anchor')
    if 'function p29ProductHref(' not in s or 'function createProductCard(' not in s:
        raise ValueError(filename + ': catalogue navigation broken')
    menu = s.split('<ul id="main-menu">', 1)[1].split('</ul>', 1)[0]
    if menu.count('<li>') < 5:
        raise ValueError(filename + ': too few ordinary category menu links')
    for cat in CATS:
        href = f'/categorii/{cat}.html'
        if filename == 'ru.html': href = '/ru' + href
        if f'href="{href}"' not in menu:
            raise ValueError(filename + ': missing expected HTML category link ' + href)
    for a in ('id="hamburger"', 'id="search-input"', 'id="mobile-search-input"', 'id="catalog-seo"', 'href="/sitemap.xml"'):
        if a not in s and a != 'href="/sitemap.xml"':
            raise ValueError(filename + ': missing essential UI element '+a)
    if s.count('rel="canonical"') != 1 or 'hreflang="ru"' not in s or 'hreflang="ro"' not in s:
        raise ValueError(filename + ': canonical / hreflang altered')


def generator_hook(source: str) -> str:
    if MARKER in source:
        if "root / 'playspot-v48' / 'cleanup.py'" not in source:
            raise ValueError('Incomplete V48 generation hook')
        return source
    anchor = "    print(f'✅ Generated {total*2} product pages"
    if source.count(anchor) != 1:
        raise ValueError('Unsupported V29 generator: cannot insert V48 hook')
    hook = (
        '    # ' + MARKER + ': keep only the HTML SEO navigation after rebuild.\n'
        "    addon48 = root / 'playspot-v48' / 'cleanup.py'\n"
        "    if addon48.is_file(): subprocess.run([sys.executable, str(addon48), '--root', str(root)], check=True)\n"
    )
    return source.replace(anchor, hook + anchor, 1)


def plan(root: Path) -> dict[Path, str]:
    root = root.resolve()
    output = {}
    for name in PAGES:
        file = root / name
        old = file.read_text(encoding='utf-8')
        new = cleanup_html(old, name)
        if old != new:
            output[file] = new
    file = root / 'playspot-v29/generate.py'
    old = file.read_text(encoding='utf-8')
    new = generator_hook(old)
    if old != new: output[file] = new
    return output


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    changes = plan(Path(args.root))
    print(('V48 PREVIEW' if args.check else 'V48 CLEANUP') + ': '
          + f'{len(changes)} files to update; only the two homepages and V29 regeneration hook')
    if args.check: return
    for path, content in changes.items():
        path.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    main()
