#!/usr/bin/env python3
"""V31 FIX: attach the original XSL sitemap viewer to V29 or V30 sitemap generators.

Fixes the earlier V31 installer error when V30 switched from ET.ElementTree(...).write
into tree.write(...). Never alters URL entries, robots rules, metadata or catalog pages.
"""
from pathlib import Path
import argparse
import re
import shutil
import xml.etree.ElementTree as ET

XML_PI = '<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>'
MARKER = '# V31 FIX: Retain the sitemap XSL viewer after regenerating the SEO pages.'
# Allow the V29 and V30 styles of sitemap generation, without rewriting code elsewhere.
WRITE_PATTERN = re.compile(
    r"^(?P<indent>[ \t]*)(?P<stmt>(?:ET\.ElementTree\(rootxml\)|tree)\.write\(\s*root\s*/\s*['\"]sitemap\.xml['\"][^\n]*\))\s*$",
    re.MULTILINE,
)
INSERT = r'''# V31 FIX: Retain the sitemap XSL viewer after regenerating the SEO pages.
xml_file = root/'sitemap.xml'
xml_text = xml_file.read_text(encoding='utf-8')
xml_text = re.sub(r'<\?xml-stylesheet\b[^>]*\?>\s*', '', xml_text)
xml_text = re.sub(r'^(<\?xml\b[^>]*\?>)',
                  r'\1\n<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>',
                  xml_text, count=1)
xml_file.write_text(xml_text, encoding='utf-8')'''


def attach_pi(xml):
    if not re.match(r'^<\?xml\b[^>]*\?>', xml):
        raise RuntimeError('sitemap.xml is missing its XML declaration; leaving it untouched.')
    xml = re.sub(r'<\?xml-stylesheet\b[^>]*\?>\s*', '', xml)
    return re.sub(r'^(<\?xml\b[^>]*\?>)', lambda m: m.group(1) + '\n' + XML_PI,
                  xml, count=1)


def sitemap_urls(xml):
    element = ET.fromstring(xml)
    namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    if element.tag != namespace + 'urlset':
        raise RuntimeError('Not a standard XML sitemap; refusing changes.')
    result = [node.text for node in element.findall('.//' + namespace + 'loc')]
    if not result or any(not (u or '').startswith('https://playspotstore.online/') for u in result):
        raise RuntimeError('Invalid or empty sitemap URL list; refusing changes.')
    return result


def patch(root):
    root = root.resolve()
    generator_path = root/'playspot-v29/generate.py'
    xml_path = root/'sitemap.xml'
    xsl_path = Path(__file__).with_name('sitemap.xsl')
    if not (root/'index.html').is_file() or not generator_path.is_file() or not xml_path.is_file():
        raise RuntimeError('Run from the PlaySpotStore repository root with V29/V30 installed.')
    ET.parse(xsl_path)  # Verify the actual XSL file before any edits.
    before = xml_path.read_text(encoding='utf-8')
    original_urls = sitemap_urls(before)
    after = attach_pi(before)
    if sitemap_urls(after) != original_urls:
        raise RuntimeError('URL list changed unexpectedly, refusing to replace sitemap.')

    source = generator_path.read_text(encoding='utf-8')
    if MARKER not in source:
        matches = list(WRITE_PATTERN.finditer(source))
        if len(matches) != 1:
            raise RuntimeError('Could not locate a unique sitemap XML write in the V29/V30 generator. No files changed.')
        match = matches[0]
        indent = match.group('indent')
        addition = '\n' + '\n'.join(indent + line for line in INSERT.splitlines())
        source = source[:match.end()] + addition + source[match.end():]
        compile(source, str(generator_path), 'exec')  # Catch accidental syntax errors.

    # All validation is finished; write the three specific files only.
    generator_path.write_text(source, encoding='utf-8')
    shutil.copyfile(xsl_path, root/'sitemap.xsl')
    xml_path.write_text(after, encoding='utf-8')
    assert sitemap_urls(xml_path.read_text(encoding='utf-8')) == original_urls
    assert xml_path.read_text(encoding='utf-8').count(XML_PI) == 1
    print(f'✅ Sitemap viewer fixed: {len(original_urls)} original URLs preserved')
    print('✅ V29/V30 generator patched, future regeneration keeps /sitemap.xsl')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='.')
    patch(Path(p.parse_args().root))
