#!/usr/bin/env python3
"""V37: place V36 category search within the existing hero border and collapse extras.
Idempotent, standard library only. V29 generator hook ensures regeneration survives.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path

CATEGORIES = ('ps2', 'ps4', 'ps5', 'nintendo', 'xbox', 'consoles', 'accessories')
START = '<!-- P36 CATEGORY FILTER START -->'
END = '<!-- P36 CATEGORY FILTER END -->'
CSS_LINK = '<link rel="stylesheet" href="/playspot-v37.css?v=20261109-v37">'
JS_LINK = '<script defer src="/playspot-v37.js?v=20261109-v37"></script>'
HOOK_COMMENT = '    # P37: restore single-border category filters after V36 generator hook\n'
HOOK = (HOOK_COMMENT +
        '    addon37 = root / "playspot-v37" / "patch.py"\n'
        '    if addon37.is_file(): subprocess.run([sys.executable, str(addon37), "--root", str(root)], check=True)\n')


def transform(source: str, lang: str, name: str) -> str:
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError(f'{name}: V36 filter panel not found exactly once; install V36 first')
    if 'p37-hero' in source:
        # Installation is repeat-safe. Verify the UI is not partially modified.
        for token in ('p37-integrated', 'data-p37-toggle', 'data-p37-extras hidden', CSS_LINK, JS_LINK):
            if token not in source:
                raise ValueError(f'{name}: incomplete V37 markup: {token}')
        return source

    block_match = re.search(re.escape(START) + r'.*?' + re.escape(END), source, flags=re.S)
    assert block_match
    block = block_match.group(0)
    if block.count('class="p36-filter-panel"') != 1:
        raise ValueError(f'{name}: unsupported V36 panel structure')
    block = block.replace('class="p36-filter-panel"', 'class="p36-filter-panel p37-integrated"', 1)
    label = 'Фильтры' if lang == 'ru' else 'Filtre'
    arrow = '<span class="p37-arrow" aria-hidden="true"></span>'
    toggle = (f'    <button type="button" class="p37-filter-toggle" data-p37-toggle '
              f'aria-expanded="false" aria-controls="p37-advanced-filters">'
              f'<span class="p37-filter-icon" aria-hidden="true">☷</span>{label}{arrow}</button>')
    old = '  </div>\n  <div class="p36-extras">'
    new = f'{toggle}\n  </div>\n  <div class="p36-extras" id="p37-advanced-filters" data-p37-extras hidden>'
    if block.count(old) != 1:
        raise ValueError(f'{name}: unsupported V36 field/extras layout')
    block = block.replace(old, new, 1)

    # No duplicate visual box: the complete filter panel lives INSIDE category hero.
    without = source[:block_match.start()] + source[block_match.end():]
    hero_match = re.search(r'<section class="seo-category-hero">(?P<body>.*?)</section>', without, re.S)
    if not hero_match:
        raise ValueError(f'{name}: category hero section missing')
    hero = hero_match.group(0)
    if hero.count('</h1>') != 1:
        raise ValueError(f'{name}: unexpected heading structure')
    hero = hero.replace('class="seo-category-hero"','class="seo-category-hero p37-hero"',1)
    hero = hero.replace('</h1>', '</h1>\n'+block, 1)
    without = without[:hero_match.start()] + hero + without[hero_match.end():]

    # Cache-busted CSS/JS, loaded after V36 so existing filtering remains unchanged.
    without = re.sub(r'\s*<link rel="stylesheet" href="/playspot-v37\.css[^\"]*">', '', without)
    without = re.sub(r'\s*<script defer src="/playspot-v37\.js[^\"]*"></script>', '', without)
    if '</head>' not in without or '</body>' not in without:
        raise ValueError(f'{name}: head or body missing')
    without = without.replace('</head>',CSS_LINK+'\n</head>',1)
    without = without.replace('</body>',JS_LINK+'\n</body>',1)
    return without


def install_generator_hook(root: Path) -> bool:
    generator = root / 'playspot-v29' / 'generate.py'
    if not generator.exists():
        raise FileNotFoundError(generator)
    source = generator.read_text(encoding='utf-8')
    if HOOK_COMMENT in source:
        return False
    anchor = '    if addon.is_file(): subprocess.run([sys.executable, str(addon), "--root", str(root)], check=True)\n'
    if source.count(anchor) != 1 or '# P36: keep search filters after each catalog regeneration' not in source:
        raise RuntimeError('V36 generator hook not found, install V36 before V37')
    source = source.replace(anchor, anchor+HOOK,1)
    generator.write_text(source, encoding='utf-8')
    return True


def apply(root: Path, patch_generator: bool = False) -> int:
    root = root.resolve()
    if not (root / 'index.html').is_file() or not (root / 'ru.html').is_file():
        raise RuntimeError('Run from the PlaySpotStore repository root')
    changed = {}
    for lang, folder in [('ro', 'categorii'), ('ru', 'ru/categorii')]:
        for cat in CATEGORIES:
            path = root / folder / (cat+'.html')
            if not path.is_file():
                raise FileNotFoundError(path)
            old = path.read_text(encoding='utf-8')
            new = transform(old, lang, str(path.relative_to(root)))
            if new != old:
                changed[path] = new
    # Validate all pages before writing any of them.
    if patch_generator:
        install_generator_hook(root)
    for path, text in changed.items():
        path.write_text(text, encoding='utf-8')
    print(f'V37 OK: {len(CATEGORIES)*2} RO/RU categories checked; {len(changed)} pages updated; one border per category.')
    return len(changed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--patch-generator', action='store_true')
    args = parser.parse_args()
    apply(Path(args.root), args.patch_generator)
