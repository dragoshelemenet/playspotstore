#!/usr/bin/env python3
"""Targeted, repeatable PlaySpotStore desktop-header fix (RO + RU)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STYLESHEET = '<link rel="stylesheet" href="/playspot-v51.css?v=20261113-v51">'
MOBILE_QUERY_OLD = (
    "const mq = window.matchMedia("
    "'(max-width: 1430px), (min-width: 1431px) and "
    "(max-width: 1535px) and (any-pointer: coarse)');"
)
MOBILE_QUERY_NEW = (
    "const mq = window.matchMedia("
    "'(max-width: 950px), (min-width: 951px) and "
    "(max-width: 1535px) and (any-pointer: coarse)');"
)


def replace_if_needed(path: Path, old: str, new: str) -> bool:
    content = path.read_text(encoding="utf-8")
    if old in content:
        if content.count(old) != 1:
            raise RuntimeError(f"Expected precisely one old marker in {path}")
        path.write_text(content.replace(old, new, 1), encoding="utf-8")
        return True
    if content.count(new) == 1:
        return False
    raise RuntimeError(f"Unexpected existing content in {path}; refusing broad rewrite.")


def update_home(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
    if content.count(STYLESHEET) == 1:
        return False
    if STYLESHEET in content:
        raise RuntimeError(f"Duplicate V51 stylesheet link in {path}")
    if content.count("</head>") != 1:
        raise RuntimeError(f"Unexpected </head> in {path}")
    for required in ('id="main-menu"', 'class="p22-header-spin"', 'class="hero"'):
        if required not in content:
            raise RuntimeError(f"Missing required HTML in {path}: {required}")
    content = content.replace("</head>", f"  {STYLESHEET}\n</head>", 1)
    path.write_text(content, encoding="utf-8")
    return True


def main() -> None:
    css = ROOT / "playspot-v51.css"
    if not css.is_file():
        raise RuntimeError("Missing playspot-v51.css. Unzip the whole archive first.")
    js = ROOT / "neon-v5-fixes.js"
    if replace_if_needed(js, MOBILE_QUERY_OLD, MOBILE_QUERY_NEW):
        print("Fixed menu relocation breakpoint in neon-v5-fixes.js")
    else:
        print("Menu relocation breakpoint already fixed")
    for name in ("index.html", "ru.html"):
        if update_home(ROOT / name):
            print(f"Added responsive V51 stylesheet to {name}")
        else:
            print(f"V51 stylesheet already present in {name}")


if __name__ == "__main__":
    main()
