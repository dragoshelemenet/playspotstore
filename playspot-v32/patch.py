#!/usr/bin/env python3
"""PlaySpotStore V32: remove browser XSLT from bot sitemap and persist HTML sitemap.

Idempotent, no data/catalog changes; existing V29/V30 SEO remains intact.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path


def patch(root: Path):
    root = root.resolve()
    generator = root / 'playspot-v29' / 'generate.py'
    if not generator.is_file():
        raise RuntimeError('V29 generator missing; run from repository root')
    src = generator.read_text(encoding='utf-8')

    # The XSLT injection introduced in V31 is obsolete (and browser-deprecated).
    start = src.find('    # V31 FIX: Retain the sitemap XSL viewer after regenerating the SEO pages.')
    if start >= 0:
        end = src.find('    # Simple local checks;', start)
        if end < 0:
            raise RuntimeError('Could not find the end of the V31 XSL injection: not editing generator')
        src = src[:start] + src[end:]
    if 'xml-stylesheet' in src:
        raise RuntimeError('An unknown sitemap stylesheet injection exists; refusing unsafe edit')

    # The separate HTML sitemap must be regenerated alongside new catalog products.
    hook = "    subprocess.run([sys.executable, str(root/'playspot-v32'/'human_sitemap.py'), '--root', str(root)], check=True)"
    if hook not in src:
        signature = "    tree.write(root/'sitemap.xml',encoding='utf-8',xml_declaration=True)"
        if src.count(signature) != 1:
            raise RuntimeError('Unexpected sitemap output statement; refusing generator modification')
        src = src.replace(signature, signature + '\n    # V32: separate crawlable HTML sitemap for people; XML stays plain for search bots.\n' + hook, 1)
    if 'import subprocess\n' not in src:
        src = src.replace('import shutil\n', 'import shutil\nimport subprocess\n', 1)

    # Link the human-readable sitemap from every generated SEO product/category footer.
    if 'sitemap_link=' not in src:
        marker = "    count_title='Посетители · 2026' if lang=='ru' else 'Vizitatori · 2026'"
        if src.count(marker) != 1:
            raise RuntimeError('Could not locate SEO page footer to add sitemap link')
        src = src.replace(marker,
            "    sitemap_link='<a href=\"/ru/sitemap.html\">Карта сайта</a>' if lang=='ru' else '<a href=\"/sitemap.html\">Harta site-ului</a>'\n" + marker, 1)
    footer_old = "<span>·</span> <span>{esc(t['legal'])}</span></div></footer>"
    footer_new = "<span>·</span> {sitemap_link} <span>·</span> <span>{esc(t['legal'])}</span></div></footer>"
    if footer_new not in src:
        if src.count(footer_old) != 1:
            raise RuntimeError('Could not find SEO footer markup to add sitemap link')
        src = src.replace(footer_old, footer_new, 1)
    generator.write_text(src, encoding='utf-8')

    # Homepages: real <a href> in the existing footer; RO and RU links are distinct.
    for lang, filename in (('ro', 'index.html'), ('ru', 'ru.html')):
        p = root / filename
        s = p.read_text(encoding='utf-8')
        target = '/ru/sitemap.html' if lang == 'ru' else '/sitemap.html'
        title = 'Карта сайта' if lang == 'ru' else 'Harta site-ului'
        pattern = re.compile(r'(<nav\s+class="p8-links"[^>]*>)(.*?)(</nav>)', flags=re.S)
        def update(m):
            old_links = m.group(2)
            if f'href="{target}"' in old_links:
                return m.group(0)
            return m.group(1) + old_links + f'<a href="{target}">{title}</a>' + m.group(3)
        edited, count = pattern.subn(update, s, count=1)
        if count != 1:
            raise RuntimeError(f'Could not find homepage footer navigation: {filename}')
        if edited != s:
            p.write_text(edited, encoding='utf-8')

    # Prevent obsolete stylesheet from being copied or accidentally referenced.
    xsl = root / 'sitemap.xsl'
    if xsl.is_file():
        xsl.unlink()
    sitemap = root / 'sitemap.xml'
    if sitemap.is_file():
        xml = sitemap.read_text(encoding='utf-8')
        cleaned = re.sub(r'<\?xml-stylesheet\b[^>]*\?>\s*', '', xml)
        if cleaned != xml:
            sitemap.write_text(cleaned, encoding='utf-8')

    print('V32 patch applied: removed XSLT, made HTML sitemap generation permanent, linked it in RO/RU footers')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    opts = ap.parse_args()
    patch(Path(opts.root))
