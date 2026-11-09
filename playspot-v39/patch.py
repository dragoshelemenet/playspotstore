#!/usr/bin/env python3
"""PlaySpotStore V39: layer the click feedback and 10% float boost on V38.
Idempotent. All category anchors, SEO, product data and existing scripts are retained.
"""
import argparse
import re
from pathlib import Path

CATEGORIES = ('ps4', 'ps5', 'nintendo', 'xbox', 'console', 'accessories')
STYLE = '<link rel="stylesheet" href="playspot-v39.css?v=20261109-v39">'
SCRIPT = '<script defer src="playspot-v39.js?v=20261109-v39"></script>'
HOOK = ('    # P39: keep V39 hero float boost and category click feedback on regeneration\n'
        '    addon39 = root / "playspot-v39" / "patch.py"\n'
        '    if addon39.is_file(): subprocess.run([sys.executable, str(addon39), "--root", str(root)], check=True)\n')

def patch_page(p):
    source = p.read_text(encoding='utf-8')
    head, sep, tail = source.partition('</head>')
    if not sep or tail.count('</body>') != 1:
        raise ValueError(f'{p}: invalid HTML structure')
    if head.count('playspot-v38.css') != 1 or head.count('playspot-v35.css') != 1:
        raise ValueError(f'{p}: V35 and V38 must already be installed')
    if source.count('class="category-deck"') != 1:
        raise ValueError(f'{p}: category deck not found exactly once')
    for cat in CATEGORIES:
        pattern = rf'<a\s+class="category-tile {cat}"[^>]*href="[^"]+"[^>]*><img\s+[^>]*>'
        if len(re.findall(pattern, source)) != 1:
            raise ValueError(f'{p}: expected one link/image for {cat}')

    head = re.sub(r'\s*<link\s+rel="stylesheet"\s+href="playspot-v39\.css[^\"]*"\s*/?>', '', head)
    anchor = re.search(r'<link\s+rel="stylesheet"\s+href="playspot-v38\.css[^\"]*"\s*/?>', head)
    if anchor is None:
        raise ValueError(f'{p}: V38 stylesheet missing')
    head = head[:anchor.end()] + '\n  ' + STYLE + head[anchor.end():]
    tail = re.sub(r'\s*<script\s+defer\s+src="playspot-v39\.js[^\"]*"\s*></script>', '', tail)
    tail = tail.replace('</body>', '  ' + SCRIPT + '\n</body>', 1)
    output = head + sep + tail
    if output != source:
        p.write_text(output, encoding='utf-8')
        return True
    return False

def patch_generator(root):
    p = root / 'playspot-v29' / 'generate.py'
    if not p.is_file():
        raise FileNotFoundError(p)
    s = p.read_text(encoding='utf-8')
    if 'addon39 = root / "playspot-v39"' in s:
        return False
    mark = "    print(f'✅ Generated {total*2} product pages"
    if s.count(mark) != 1:
        raise ValueError(f'{p}: generator insertion point not found')
    p.write_text(s.replace(mark, HOOK + mark, 1), encoding='utf-8')
    return True

def run(root, generator=False):
    root = root.resolve()
    paths = [root/'index.html', root/'ru.html']
    # Verify all pages before modifying any files.
    for p in paths:
        if not p.is_file():
            raise FileNotFoundError(p)
        s = p.read_text(encoding='utf-8')
        if 'playspot-v38.css' not in s or 'class="category-deck"' not in s:
            raise ValueError(f'{p}: V38 category homepage required')
    n = sum(patch_page(p) for p in paths)
    hook = patch_generator(root) if generator else False
    print(f'V39 OK: RO/RU homepages updated={n}, generator hook added={hook}')

if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--root', default='.')
    a.add_argument('--patch-generator', action='store_true')
    args = a.parse_args()
    run(Path(args.root), args.patch_generator)
