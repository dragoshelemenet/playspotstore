#!/usr/bin/env python3
"""Minimal check for homepage-only V43 Light SEO copy."""
from pathlib import Path
import argparse, html, re
from patch import COPY, CATALOG_RE, update_page


def check(root:Path)->None:
    root=root.resolve()
    for name, values in COPY.items():
        page=(root/name).read_text(encoding='utf-8')
        head=page.split('</head>',1)[0]
        assert '<title>'+html.escape(values['title'],quote=True)+'</title>' in head, name
        meta='<meta name="description" content="'+html.escape(values['description'],quote=True)+'">'
        assert head.count(meta)==1, name
        assert 45<=len(values['description'])<=160, (name,'meta too long')
        assert page.count('id="catalog-seo"')==1, name
        m=CATALOG_RE.search(page)
        assert m and html.unescape(m.group(2))==values['catalog'], name
        assert page.count('class="category-tile ')==6, (name,'category tiles changed')
        assert page.count('rel="canonical"')==1, (name,'canonical changed')
        assert page.count('hreflang="ro"')>=1 and page.count('hreflang="ru"')>=1, name
        assert 'p29ProductSlugs' in page, (name,'catalog links missing')
        assert update_page(page,name)==page, (name,'not stable')
    print('V43 LIGHT VALID: 2 homepages, natural RO/RU copy, canonicals and category links preserved.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.')
    check(Path(p.parse_args().root))
