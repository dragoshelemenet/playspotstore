#!/usr/bin/env python3
"""Enable subtle image-only float on the existing PlaySpotStore home category tiles.
No dependencies, no homepage regeneration, and safe to run twice.
"""
from pathlib import Path
import argparse
import re

LINK = '<link rel="stylesheet" href="playspot-v38.css?v=20261109-v38">'
CATEGORIES = ('ps4', 'ps5', 'nintendo', 'xbox', 'console', 'accessories')


def patch_page(path: Path) -> bool:
    content = path.read_text(encoding='utf-8')
    head, sep, tail = content.partition('</head>')
    if not sep or '</head>' in tail:
        raise ValueError(f'{path}: unexpected HTML head')
    if 'playspot-v35.css' not in head:
        raise ValueError(f'{path}: V35 homepage is required')
    if 'class="category-deck"' not in content:
        raise ValueError(f'{path}: no category deck found')
    for category in CATEGORIES:
        pattern = rf'<a\s+class="category-tile {category}"[^>]*><img\s+[^>]*src="neon-assets/[^\"]+"'
        if len(re.findall(pattern, content)) != 1:
            raise ValueError(f'{path}: expected exactly one {category} image tile')

    # Keep CSS last after V35, preserving the hero scroll parallax rules.
    head = re.sub(r'\s*<link\s+rel="stylesheet"\s+href="playspot-v38\.css[^\"]*"\s*/?>', '', head)
    marker = re.search(r'<link\s+rel="stylesheet"\s+href="playspot-v35\.css[^\"]*"\s*/?>', head)
    if not marker:
        raise ValueError(f'{path}: expected V35 stylesheet link')
    at = marker.end()
    head = head[:at] + '\n  ' + LINK + head[at:]
    result = head + sep + tail
    if result != content:
        path.write_text(result, encoding='utf-8')
        return True
    return False


def run(root: Path) -> None:
    root = root.resolve()
    for filename in ('index.html', 'ru.html'):
        if not (root / filename).is_file():
            raise FileNotFoundError(root / filename)
    updated = sum(patch_page(root / filename) for filename in ('index.html', 'ru.html'))
    print(f'V38: checked 6 tiles x 2 languages; {updated} homepage(s) updated')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    run(Path(parser.parse_args().root))
