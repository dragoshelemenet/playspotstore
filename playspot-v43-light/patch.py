#!/usr/bin/env python3
"""V43 Light: natural mixed-condition storefront wording, ONLY on the two homepages.
No category/product pages or Product itemCondition values are changed.
Repeat-safe; validates the expected existing homepage structure before writing.
"""
from __future__ import annotations
import argparse
import html
import re
from pathlib import Path

COPY = {
    'index.html': {
        'title': 'Jocuri video noi si second-hand in Moldova | PlaySpotStore',
        'description': ('Jocuri PS2, PS4, PS5, Nintendo si Xbox, noi si second-hand (b/u), in Moldova. '
                        'Exploreaza catalogul PlaySpotStore si confirma starea produsului.'),
        'catalog': ('Alege platforma și descoperă jocuri noi sau second-hand (b/u), în funcție de titlu. '
                    'Starea, prețul și disponibilitatea se confirmă înainte de comandă.'),
        'language': 'ro',
    },
    'ru.html': {
        'title': 'Новые и б/у видеоигры в Молдове | PlaySpotStore',
        'description': ('Новые и б/у игры для PS2, PS4, PS5, Nintendo и Xbox в PlaySpotStore Молдова. '
                        'Изучайте каталог и уточняйте состояние и наличие.'),
        'catalog': ('Выберите платформу: в каталоге есть как новые игры, так и игры б/у, '
                    'в зависимости от товара. Состояние, цена и наличие уточняются перед заказом.'),
        'language': 'ru',
    },
}

CATALOG_RE = re.compile(
    r'(<div class="p29-seo-wrap"><h2 id="p29-catalog-title">[^<]+</h2><p>)'
    r'(.*?)'
    r'(</p>\s*<div class="p29-seo-links">)',
    re.DOTALL,
)


def update_page(source: str, filename: str) -> str:
    data = COPY[filename]
    head, marker, body = source.partition('</head>')
    if not marker or body.count('</body>') != 1:
        raise ValueError(f'{filename}: unexpected document structure')
    if f'<html lang="{data["language"]}">' not in head:
        raise ValueError(f'{filename}: unexpected page language')
    if source.count('id="catalog-seo"') != 1 or source.count('class="category-deck"') != 1:
        raise ValueError(f'{filename}: expected one existing catalog section and homepage category deck')
    if source.count('class="p29-seo-links"') != 1:
        raise ValueError(f'{filename}: missing or duplicated crawlable category links')

    title_re = re.compile(r'<title>[^<]*</title>')
    if len(title_re.findall(head)) != 1:
        raise ValueError(f'{filename}: expected exactly one HTML title')
    head = title_re.sub('<title>' + html.escape(data['title'], quote=True) + '</title>', head, count=1)

    meta_re = re.compile(r'<meta\s+name="description"\s+content="[^"]*"\s*/?>', re.I)
    if len(meta_re.findall(head)) != 1:
        raise ValueError(f'{filename}: expected exactly one meta description')
    head = meta_re.sub('<meta name="description" content="' + html.escape(data['description'], quote=True) + '">', head, count=1)

    # Only the existing catalog introduction changes, in-place. No extra blocks.
    whole = head + marker + body
    matches = list(CATALOG_RE.finditer(whole))
    if len(matches) != 1:
        raise ValueError(f'{filename}: expected exactly one catalog-introduction paragraph')
    match = matches[0]
    revised = match.group(1) + html.escape(data['catalog'], quote=True) + match.group(3)
    return whole[:match.start()] + revised + whole[match.end():]


def run(root: Path, check: bool) -> None:
    root = root.resolve()
    expected = ('index.html', 'ru.html')
    planned = {}
    for name in expected:
        path = root/name
        if not path.is_file():
            raise FileNotFoundError(path)
        original = path.read_text(encoding='utf-8')
        new = update_page(original, name)
        # Re-running must yield exactly the same bytes.
        if update_page(new, name) != new:
            raise AssertionError('Patch is not idempotent: ' + name)
        planned[path] = (original, new)
    changes = sum(a != b for a, b in planned.values())
    if check:
        print(f'V43 LIGHT CHECK: {changes} homepage(s) to update. Product/category files unaffected.')
        return
    for path, (old, new) in planned.items():
        if old != new:
            path.write_text(new, encoding='utf-8')
    print(f'V43 LIGHT: {changes} homepage(s) updated; 0 product/category pages modified.')


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',default='.')
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    run(Path(a.root),a.check)
