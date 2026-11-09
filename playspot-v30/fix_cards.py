#!/usr/bin/env python3
"""V30: prevent SEO catalog cards' image/content overlap, persist fixes in generator, readable XML."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
expected = (root / 'playspot-v29' / 'seo.css', root / 'seo' / 'site.css', root / 'playspot-v29' / 'generate.py')
missing = [str(p.relative_to(root)) for p in expected if not p.is_file()]
if missing:
    raise SystemExit('V29 is required; missing: ' + ', '.join(missing))

MARKER = '/* PlaySpotStore V30: fixed-image SEO cards'
extra = r'''/* PlaySpotStore V30: fixed-image SEO cards — reserve separate, non-overlapping media and copy areas.
   Covers with different aspect ratios stay fully visible via object-fit:contain.
   The fallback logo is constrained exactly like other catalog images. */
.seo-grid .seo-product-card {
  display:flex!important;
  flex-direction:column!important;
  min-width:0!important;
  overflow:hidden!important;
}
.seo-grid .seo-product-card > a {
  display:flex!important;
  flex-direction:column!important;
  width:100%!important;
  height:100%!important;
  min-width:0!important;
  min-height:0!important;
  overflow:hidden!important;
}
.seo-grid .seo-product-card .seo-product-art {
  box-sizing:border-box!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  flex:0 0 240px!important;
  width:100%!important;
  height:240px!important;
  min-height:0!important;
  max-height:240px!important;
  padding:14px!important;
  overflow:hidden!important;
  position:relative!important;
  isolation:isolate;
}
.seo-grid .seo-product-card .seo-product-art img {
  display:block!important;
  box-sizing:border-box!important;
  width:100%!important;
  height:100%!important;
  min-width:0!important;
  min-height:0!important;
  max-width:100%!important;
  max-height:100%!important;
  object-fit:contain!important;
  object-position:center center!important;
  aspect-ratio:auto!important;
  position:static!important;
  inset:auto!important;
  margin:0!important;
  transform:none!important;
  flex:0 0 auto!important;
}
.seo-grid .seo-product-card .seo-product-body {
  box-sizing:border-box!important;
  position:relative!important;
  z-index:2!important;
  display:flex!important;
  flex-direction:column!important;
  gap:8px!important;
  flex:1 1 auto!important;
  min-width:0!important;
  min-height:145px!important;
  width:100%!important;
  padding:16px 17px 18px!important;
  background:linear-gradient(160deg,rgba(10,34,38,.99),rgba(8,23,37,.99))!important;
  overflow:hidden!important;
}
.seo-grid .seo-product-card .seo-product-body h3 {
  display:-webkit-box!important;
  -webkit-box-orient:vertical!important;
  -webkit-line-clamp:3!important;
  line-clamp:3!important;
  overflow:hidden!important;
  max-height:4.15em!important;
  line-height:1.37!important;
  min-height:2.74em!important;
  margin:0!important;
  overflow-wrap:anywhere!important;
}
.seo-grid .seo-product-card .seo-product-price {margin:0!important;}
.seo-grid .seo-product-card .seo-product-details {
  flex:0 0 auto!important;
  margin-top:auto!important;
  align-self:flex-start!important;
}
@media(max-width:1100px){
  .seo-grid .seo-product-card .seo-product-art {
    flex-basis:220px!important;height:220px!important;max-height:220px!important;
  }
}
@media(max-width:730px){
  .seo-grid .seo-product-card .seo-product-art {
    flex-basis:176px!important;height:176px!important;max-height:176px!important;padding:10px!important;
  }
  .seo-grid .seo-product-card .seo-product-body {
    padding:13px 12px 15px!important;min-height:138px!important;
  }
}
@media(max-width:370px){
  .seo-grid .seo-product-card .seo-product-art {
    flex-basis:145px!important;height:145px!important;max-height:145px!important;padding:8px!important;
  }
  .seo-grid .seo-product-card .seo-product-body {
    padding:12px 10px 13px!important;min-height:136px!important;
  }
}
'''
for path in expected[:2]:
    before = path.read_text(encoding='utf-8')
    head = before.split(MARKER, 1)[0].rstrip()
    updated = head + '\n\n' + extra.strip() + '\n'
    if before != updated:
        path.write_text(updated, encoding='utf-8')
        print('Updated', path.relative_to(root))
    else:
        print('Already up to date:', path.relative_to(root))

generator = expected[2]
s = generator.read_text(encoding='utf-8')
old_link = '<link rel="stylesheet" href="/seo/site.css">'
new_link = '<link rel="stylesheet" href="/seo/site.css?v=20261109-v30">'
if old_link in s:
    s = s.replace(old_link, new_link, 1)
elif new_link not in s:
    raise SystemExit('V29 generator stylesheet markup not recognized. No unsafe patch applied.')
old_write = "    ET.ElementTree(rootxml).write(root/'sitemap.xml',encoding='utf-8',xml_declaration=True)"
new_write = "    tree=ET.ElementTree(rootxml)\n    ET.indent(tree, space='  ', level=0)  # Human-readable XML; same URL entries for crawlers.\n    tree.write(root/'sitemap.xml',encoding='utf-8',xml_declaration=True)"
if old_write in s:
    s=s.replace(old_write,new_write,1)
elif new_write not in s:
    raise SystemExit('V29 generator sitemap markup not recognized. No unsafe patch applied.')
if s != generator.read_text(encoding='utf-8'):
    generator.write_text(s,encoding='utf-8')
    print('Updated', generator.relative_to(root))
else:
    print('Already up to date:',generator.relative_to(root))
