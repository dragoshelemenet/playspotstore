#!/usr/bin/env python3
"""Ensure old JS category popup navigation is absent, while real SEO links remain."""
from pathlib import Path
import argparse
from cleanup import validate_homepage, cleanup_html, generator_hook, MARKER


def validate(root: Path):
    root = root.resolve()
    for name in ('index.html','ru.html'):
        s = (root/name).read_text(encoding='utf-8')
        validate_homepage(s, name)
        assert cleanup_html(s, name) == s, name + ': cleanup is not repeat-safe'
        for modal in ('modal-ps4','modal-ps5','modal-console','modal-accessories'):
            assert f'id="{modal}"' not in s, (name,modal)
        assert 'addMenuEvents' not in s and 'fetch("data/categories' not in s,name
        assert 'function fetchProducts(' not in s and 'function openCategoryModal(' not in s,name
        assert 'function showModal(' not in s and 'function trapFocus(' not in s,name
    gen = (root/'playspot-v29/generate.py').read_text(encoding='utf-8')
    assert MARKER in gen and generator_hook(gen) == gen
    print('V48 VALID: RO/RU menus are static SEO links, no duplicated JS categories or old category modals; product search and popups retained.')


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.')
    validate(Path(p.parse_args().root))
