#!/usr/bin/env python3
"""Persistence fixes for V44/V42 after geolocated V45 canonical URL migration."""
from pathlib import Path
import argparse


def ensure(root:Path):
    out={}
    v44=root/'playspot-v44/patch.py'
    s=v44.read_text(encoding='utf-8')
    mark='P45_SKIP_MIGRATED_PRODUCTS'
    if mark not in s:
        old="   for path in directory.glob('*.html'):\n    source=path.read_text(encoding='utf-8')"
        new="   for path in directory.glob('*.html'):\n    # P45_SKIP_MIGRATED_PRODUCTS: V29 regenerates old routes, V45 redirects them.\n    if path.name.endswith(('-chisinau-moldova.html','-kishinev-moldova.html')):continue\n    source=path.read_text(encoding='utf-8')"
        if s.count(old)!=1:raise ValueError('Unsupported V44 patch.py product scanner; no change made')
        s=s.replace(old,new,1)
    if 'P45_SKIP_MIGRATED_GUIDE' not in s:
        old="   for page in folder.glob('*.html'):\n    if f'\"sku\":\"{pid}\"' in page.read_text(encoding='utf-8'):"
        new="   for page in folder.glob('*.html'):\n    # P45_SKIP_MIGRATED_GUIDE: the existing new geo URL is the same SKU.\n    if page.name.endswith(('-chisinau-moldova.html','-kishinev-moldova.html')):continue\n    if f'\"sku\":\"{pid}\"' in page.read_text(encoding='utf-8'):"
        if s.count(old)!=1:raise ValueError('Unsupported V44 landing guide SKU scanner; no change made')
        s=s.replace(old,new,1)
    if s!=v44.read_text(encoding='utf-8'):out[v44]=s
    v42=root/'playspot-v42/validate.py'
    s=v42.read_text(encoding='utf-8')
    if 'P45_ALIAS_SKIP' not in s:
        old="    source=path.read_text(encoding='utf-8')\n    m=re.search"
        new="    source=path.read_text(encoding='utf-8')\n    if '<!-- P45 LEGACY REDIRECT -->' in source:continue  # P45_ALIAS_SKIP\n    m=re.search"
        if s.count(old)!=1:raise ValueError('Unsupported V42 validator scanner; no change made')
        out[v42]=s.replace(old,new,1)
    # V44 validator should be useful to owners even after V45's migration.
    v44check=root/'playspot-v44/validate.py'
    s=v44check.read_text(encoding='utf-8')
    if 'P45_GEO_VALIDATOR' not in s:
        old="   cp=base/'categorii'/f'{cat}.html';s=cp.read_text(encoding='utf-8')"
        new="   cp=base/'categorii'/f'{cat}.html'\n   # P45_GEO_VALIDATOR: prefer relocated canonical pages when V45 is installed.\n   if (root/'playspot-v45/url-map.json').is_file():\n    import json as _json\n    _map=_json.loads((root/'playspot-v45/url-map.json').read_text(encoding='utf-8'))\n    cp=root/_map.get(cp.relative_to(root).as_posix(),cp.relative_to(root).as_posix())\n   s=cp.read_text(encoding='utf-8')"
        if s.count(old)!=1:raise ValueError('Unsupported V44 validator category path; no change made')
        s=s.replace(old,new,1)
        old="   pages=list(directory.glob('*.html'))"
        new="   pages=list(directory.glob('*.html'))\n   if (root/'playspot-v45/url-map.json').is_file():\n    _suffix='-kishinev-moldova.html' if lang=='ru' else '-chisinau-moldova.html'\n    pages=[page for page in pages if page.name.endswith(_suffix)]"
        if s.count(old)!=1:raise ValueError('Unsupported V44 validator product scan; no change made')
        s=s.replace(old,new,1)
        out[v44check]=s
    return out


def main(root:Path,check:bool):
    edits=ensure(root.resolve())
    print(('V45 COMPAT CHECK' if check else 'V45 COMPAT PATCH')+f': {len(edits)} validation/regeneration scripts to update')
    if not check:
        for path,s in edits.items():path.write_text(s,encoding='utf-8')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--check',action='store_true')
    args=ap.parse_args();main(Path(args.root),args.check)
