#!/usr/bin/env python3
"""V52: apply tablet-only V25 breakpoints without changing layout or SEO data."""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BEFORE_TABLET = "@media (min-width:951px) and (max-width:1430px),\n       (min-width:1431px)"
AFTER_TABLET = "@media (min-width:951px) and (max-width:1430px) and (any-pointer:coarse),\n       (min-width:1431px)"
BEFORE_SHORT = "@media (min-width:951px) and (max-width:1430px) and (max-height:850px),\n       (min-width:1431px)"
AFTER_SHORT = "@media (min-width:951px) and (max-width:1430px) and (any-pointer:coarse) and (max-height:850px),\n       (min-width:1431px)"

OLD_LINK = 'playspot-v25.css?v=20261108-v25a'
NEW_LINK = 'playspot-v25.css?v=20261113-v52-desktop'


def one_replacement(path: Path, before: str, after: str) -> bool:
    content = path.read_text(encoding="utf-8")
    if content.count(after) == 1:
        return False
    if content.count(before) != 1:
        raise RuntimeError(f"Expected exactly one matching marker in {path.name}: {before!r}")
    path.write_text(content.replace(before, after, 1), encoding="utf-8")
    return True


def main() -> None:
    css = ROOT / "playspot-v25.css"
    js = ROOT / "neon-v5-fixes.js"
    if "and (any-pointer: coarse)" not in js.read_text(encoding="utf-8"):
        raise RuntimeError("V51 menu script missing. Please install V51 before V52.")
    for name in ("index.html", "ru.html"):
        content = (ROOT / name).read_text(encoding="utf-8")
        if 'playspot-v51.css?v=20261113-v51' not in content:
            raise RuntimeError(f"V51 missing in {name}; install V51 first.")
    changed = False
    changed |= one_replacement(css, BEFORE_TABLET, AFTER_TABLET)
    changed |= one_replacement(css, BEFORE_SHORT, AFTER_SHORT)
    for name in ("index.html", "ru.html"):
        changed |= one_replacement(ROOT / name, OLD_LINK, NEW_LINK)
    print("V52 breakpoint + cache-busting:", "patched" if changed else "already applied")


if __name__ == "__main__":
    main()
