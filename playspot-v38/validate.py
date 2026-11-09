#!/usr/bin/env python3
"""Quick V38 correctness checks; no browser dependencies required."""
from pathlib import Path
import argparse
import re


def validate(root: Path) -> None:
    css = (root / 'playspot-v38.css').read_text(encoding='utf-8')
    assert '@keyframes p38-category-art-float' in css
    assert 'prefers-reduced-motion: reduce' in css
    assert '.category-deck > .category-tile > img' in css
    assert ':nth-child(6)' in css
    for filename in ('index.html', 'ru.html'):
        text = (root / filename).read_text(encoding='utf-8')
        head = text.split('</head>', 1)[0]
        assert head.count('playspot-v38.css') == 1, f'{filename}: missing/duplicate V38 CSS'
        assert head.index('playspot-v35.css') < head.index('playspot-v38.css'), f'{filename}: wrong CSS order'
        deck = re.search(r'<div class="category-deck">(.+?)</div>', text, re.S)
        assert deck, f'{filename}: category deck not found'
        assert len(re.findall(r'<a class="category-tile ', deck.group(1))) == 6, f'{filename}: category count changed'
        assert len(re.findall(r'<img\s', deck.group(1))) == 6, f'{filename}: image count changed'
    print('V38 PASS: homepage RO/RU, 6 original links/images per page, CSS order, reduced motion')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    validate(Path(parser.parse_args().root))
