#!/usr/bin/env python3
"""Add V35 scroll parallax over existing V34 CSS floating animation. Idempotent."""
import argparse
import re
from pathlib import Path

STYLE = '<link rel="stylesheet" href="playspot-v35.css?v=20261109-v35">'
SCRIPT = '<script defer src="playspot-v35.js?v=20261109-v35"></script>'

def patch(root):
    for name in ('index.html','ru.html'):
        p=root/name
        html=p.read_text(encoding='utf-8')
        if 'class="hero-art p34-hero-art"' not in html or 'class="p34-layers"' not in html:
            raise RuntimeError(f'{name}: V34 hero layers not installed; install V34 first')
        if not re.search(r'<link\s+rel="stylesheet"\s+href="playspot-v34\.css[^\"]*"',html):
            raise RuntimeError(f'{name}: V34 stylesheet missing')
        html=re.sub(r'\s*<link\s+rel="stylesheet"\s+href="playspot-v35\.css[^\"]*"\s*/?>','',html)
        html=re.sub(r'\s*<script\s+defer\s+src="playspot-v35\.js[^\"]*"></script>','',html)
        # Keep our CSS after the V34 rules so independent translation has correct precedence.
        html,n=re.subn(r'(<link\s+rel="stylesheet"\s+href="playspot-v34\.css[^\"]*"\s*/?>)',r'\1\n  '+STYLE,html,count=1)
        if n!=1:raise RuntimeError(f'{name}: unable to place V35 CSS')
        html=html.replace('</body>','  '+SCRIPT+'\n</body>',1)
        p.write_text(html,encoding='utf-8')
        print(f'OK: {name}: V35 parallax enabled without changing V34 artwork')

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',default='.');args=a.parse_args()
    patch(Path(args.root))
