#!/usr/bin/env python3
"""Offline checks that the V51 patch is safe to publish."""
from pathlib import Path
from patch import ROOT, STYLESHEET, MOBILE_QUERY_NEW, MOBILE_QUERY_OLD


def run() -> None:
    js = (ROOT / "neon-v5-fixes.js").read_text(encoding="utf-8")
    assert js.count(MOBILE_QUERY_NEW) == 1, "Mobile portal must use the new query"
    assert MOBILE_QUERY_OLD not in js
    css = (ROOT / "playspot-v51.css").read_text(encoding="utf-8")
    assert "@media (min-width:951px) and (pointer:fine) and (hover:hover) and (not (any-pointer:coarse))" in css
    assert "body header nav ul#main-menu" in css
    assert "position:static!important" in css
    assert "grid-template-columns:repeat(6,minmax(0,1fr))!important" in css
    assert "body header .p22-header-spin" in css
    for name, language in (("index.html", "ro"), ("ru.html", "ru")):
        html = (ROOT / name).read_text(encoding="utf-8")
        assert html.count(STYLESHEET) == 1, name
        assert html.index(STYLESHEET) < html.index("</head>"), name
        assert f'<html lang="{language}">' in html, name
        assert 'id="main-menu"' in html and 'class="p22-header-spin"' in html, name
        assert 'rel="canonical"' in html and 'hreflang="ru"' in html, name
        assert 'content="noindex"' not in html.lower(), name
    print("PASS V51: bilingual headers, stable canonical/hreflang and compact desktop CSS")


if __name__ == "__main__":
    run()
