#!/usr/bin/env python3
"""Stage only V45-owned generated paths and scripts; don't add unrelated uploads."""
import argparse
import subprocess
from pathlib import Path
from migrate import routes

def stage(root:Path):
    root=root.resolve()
    paths=routes(root)
    names=list(paths)+list(paths.values())+[
      'index.html','ru.html','sitemap.xml','sitemap.html','ru/sitemap.html',
      'jocuri-video-chisinau-moldova.html','ru/videoigry-kishinev-moldova.html',
      'playspot-v29/generate.py','playspot-v44/patch.py','playspot-v44/validate.py',
      'playspot-v42/validate.py',
    ]
    names+=sorted(x.relative_to(root).as_posix() for x in (root/'playspot-v45').iterdir() if x.is_file() and x.suffix!='.pyc')
    names=list(dict.fromkeys(names))
    for i in range(0,len(names),100):
        subprocess.run(['git','add','--']+names[i:i+100],cwd=root,check=True)
    print(f'V45 STAGED: {len(names)} owned files (no ZIP uploads or unrelated edits)')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.')
    a=p.parse_args();stage(Path(a.root))
