#!/usr/bin/env python3
"""Stage only V46-owned modified canonical HTML and generator, not ZIP uploads."""
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path

def stage(root:Path):
    root=root.resolve()
    mapping=json.loads((root/'playspot-v45/url-map.json').read_text(encoding='utf-8'))
    targets=['playspot-v29/generate.py']+list(mapping.values())
    targets+=sorted(p.relative_to(root).as_posix() for p in (root/'playspot-v46').iterdir() if p.is_file() and p.suffix!='.pyc')
    for i in range(0,len(targets),80):
        subprocess.run(['git','add','--']+targets[i:i+80],cwd=root,check=True)
    print(f'V46 STAGED: {len(targets)} owned files; no ZIPs or unrelated changes')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.')
    stage(Path(ap.parse_args().root))
