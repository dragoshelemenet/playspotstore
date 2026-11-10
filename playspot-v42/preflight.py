#!/usr/bin/env python3
"""Guard local user edits when continuing a failed V42 install, without reset/stash."""
import argparse, json, subprocess
from pathlib import Path

CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')

def check(root:Path):
    root=root.resolve()
    dirty=subprocess.run(['git','diff','--name-only','--'],cwd=root,capture_output=True,text=True,check=True).stdout.splitlines()
    allowed=lambda p: (p=='playspot-v29/generate.py'
                       or (p.startswith('data/') and p.endswith('.json') and p.count('/')==1)
                       or (p.startswith(('produse/','ru/produse/')) and p.endswith('.html')))
    disallowed=[p for p in dirty if not allowed(p)]
    if disallowed:
        raise SystemExit('ERROR: Other tracked files are modified; refusing to proceed: '+', '.join(disallowed[:8]))
    if dirty:
        generator=(root/'playspot-v29/generate.py').read_text(encoding='utf-8')
        if 'V42_EDITORIAL_PRODUCT' not in generator:
            raise SystemExit('ERROR: Tracked edits found, but V42 generator marker is missing; refusing to overwrite user changes.')
        for cat in CATS:
            for ext in ('.json','_ru.json'):
                records=json.loads((root/'data'/f'{cat}{ext}').read_text(encoding='utf-8'))
                if not records or any(p.get('seo_copy_version')!='v42' or not p.get('seo_editorial_review') for p in records):
                    raise SystemExit('ERROR: Partial V42 data incomplete, refusing unsafe continuation: '+cat+ext)
        print('PREFLIGHT: found complete V42 product data and expected interrupted-install edits; no unrelated tracked changes.')
    else:
        print('PREFLIGHT: clean tracked worktree.')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.')
    check(Path(ap.parse_args().root))
