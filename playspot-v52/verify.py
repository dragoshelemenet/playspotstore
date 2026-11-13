#!/usr/bin/env python3
"""Regression checks for V52: 100% desktop, 90% desktop, and touch tablets."""
from pathlib import Path
from patch import ROOT, BEFORE_TABLET, AFTER_TABLET, BEFORE_SHORT, AFTER_SHORT, OLD_LINK, NEW_LINK


def main() -> None:
    css = (ROOT / "playspot-v25.css").read_text(encoding="utf-8")
    assert BEFORE_TABLET not in css, "Old tablet rule still applies to fine-pointer desktop"
    assert BEFORE_SHORT not in css, "Old short-screen tablet rule still applies to desktop"
    assert css.count(AFTER_TABLET) == 1 and css.count(AFTER_SHORT) == 1
    assert "(min-width:1431px) and (max-width:1535px) and (any-pointer:coarse)" in css
    # The third, unrelated media-content rule must not be modified.
    assert "@media (min-width:951px) and (max-width:1150px)" in css

    menu_script = (ROOT / "neon-v5-fixes.js").read_text(encoding="utf-8")
    assert "(max-width: 1535px) and (any-pointer: coarse)" in menu_script

    desktop_css = (ROOT / "playspot-v51.css").read_text(encoding="utf-8")
    assert "body header nav ul#main-menu > li.mobile-search-bar" in desktop_css
    assert "display:none!important" in desktop_css

    for page, lang in (("index.html", "ro"), ("ru.html", "ru")):
        content = (ROOT / page).read_text(encoding="utf-8")
        assert content.count(NEW_LINK) == 1 and OLD_LINK not in content, page
        assert content.count('playspot-v51.css?v=20261113-v51') == 1, page
        assert 'id="main-menu"' in content and 'p22-header-spin' in content, page
        assert f'<html lang="{lang}">' in content, page
        assert 'rel="canonical"' in content and 'hreflang="ru"' in content, page
        assert 'content="noindex"' not in content.lower(), page
    print("PASS V52: desktop uses V51, tablet V25 stays touch-only, both languages cache-busted")


if __name__ == "__main__":
    main()
