#!/usr/bin/env python3
"""Build the droid-icons themes from map.toml.

Downloads Material Symbols SVGs from Google Fonts, turns them into
recolourable symbolic icons and writes one theme per style to themes/:
droid-icons-{rounded,outlined,sharp}[-filled], plus the droid-icons alias
(rounded, filled).

    python3 -I build.py                          every style
    python3 -I build.py --style sharp --fill 0   one style
    python3 -I build.py --offline                only the cache and src/
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "themes"
CACHE = HERE / ".cache"
SRC = HERE / "src"

URL = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbols{family}/{name}/{fill}/24px.svg"
STYLES = ("rounded", "outlined", "sharp")
# What the plain droid-icons theme (and droid 1.0) uses.
DEFAULT = ("rounded", True)
# Fallback colour when nothing recolours the icon (dark panels, like Tela-circle's).
TEXT = "#dfdfdf"

CONTEXTS = {
    "actions": "Actions",
    "apps": "Applications",
    "devices": "Devices",
    "places": "Places",
    "status": "Status",
}


def theme_name(style: str, filled: bool) -> str:
    return f"droid-icons-{style}" + ("-filled" if filled else "")


def fetch(symbol: str, style: str, filled: bool, offline: bool) -> str | None:
    """SVG source of a Material symbol, or None if it doesn't exist.

    `symbol` may end in "@0" (always unfilled) or "@1" (always filled);
    otherwise the theme's fill is used.
    """
    name, _, force = symbol.partition("@")
    if force in ("0", "1"):
        filled = force == "1"
    fill = "fill1" if filled else "default"
    cached = CACHE / style / f"{name}.{fill}.svg"
    if cached.exists():
        return cached.read_text() or None
    if offline:
        return None
    url = URL.format(family=style, name=name, fill=fill)
    req = urllib.request.Request(url, headers={"User-Agent": "droid-icons-build"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            svg = r.read().decode()
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        svg = ""
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_text(svg)  # empty = known missing
    return svg or None


def symbolic(svg: str) -> str:
    """Material SVG → 16 px symbolic icon with KDE's recolouring stylesheet."""
    view = re.search(r'viewBox="([^"]+)"', svg)
    paths = re.findall(r'<path[^>]*\sd="([^"]+)"', svg)
    if not view or not paths:
        raise ValueError("unexpected SVG")
    body = "\n".join(f' <path class="ColorScheme-Text" fill="currentColor" d="{d}"/>' for d in paths)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="{view.group(1)}">\n'
        f' <style id="current-color-scheme" type="text/css">.ColorScheme-Text {{ color:{TEXT}; }}</style>\n'
        f"{body}\n</svg>\n"
    )


def expand_levels(spec: dict) -> dict[str, list[str]]:
    """Expand a [levels.*] table into {icon name: [symbols]}.

    names: patterns with {n} (level) or {n03} (zero-padded to 3 digits)
    steps: the levels to write
    icons: [[threshold, symbol], ...], ascending; a level uses the last
           entry whose threshold it reaches
    suffixes: {"-charging": symbol, ...}, extra names per level and pattern
    """
    out: dict[str, list[str]] = {}
    icons = sorted(spec["icons"], key=lambda e: e[0])
    for n in spec["steps"]:
        symbol = [s for t, s in icons if n >= t][-1]
        for pattern in spec["names"]:
            name = pattern.format(n=n, n03=f"{n:03}", n02=f"{n:02}")
            out[name] = as_list(symbol)
            for suffix, alt in spec.get("suffixes", {}).items():
                out[name + suffix] = as_list(alt)
    return out


def as_list(v: str | list[str]) -> list[str]:
    return [v] if isinstance(v, str) else list(v)


def load_map() -> list[tuple[str, str, list[str], bool]]:
    """(context, icon name, symbol fallbacks, also write the plain name)."""
    data = tomllib.loads((HERE / "map.toml").read_text())
    entries: list[tuple[str, str, list[str], bool]] = []
    for kind in ("plain", "symbolic"):
        for context, table in data.get(kind, {}).items():
            for name, symbol in table.items():
                entries.append((context, name, as_list(symbol), kind == "plain"))
    for spec in data.get("levels", {}).values():
        for name, symbols in expand_levels(spec).items():
            entries.append((spec["context"], name, symbols, spec.get("plain", True)))
    return entries


def index_theme(style: str, filled: bool, dirs: list[str]) -> str:
    label = style.capitalize() + (" Filled" if filled else "")
    lines = [
        "[Icon Theme]",
        f"Name=Droid {label}",
        f"Comment=Material Symbols {label} system icons on top of Tela-circle",
        "Inherits=Tela-circle,breeze,hicolor",
        "Example=network-wireless-signal-excellent-symbolic",
        "",
        "# KDE",
        "FollowsColorScheme=true",
        f"Directories={','.join(dirs)}",
        "",
    ]
    for d in dirs:
        context = CONTEXTS[d.split("/")[1]]
        lines += [f"[{d}]", f"Context={context}", "Size=16", "MinSize=8", "MaxSize=512", "Type=Scalable", ""]
    return "\n".join(lines)


def build_one(entries, style: str, filled: bool, offline: bool) -> tuple[dict[Path, str], list[str]]:
    missing: list[str] = []
    files: dict[Path, str] = {}
    for context, name, symbols, plain in entries:
        base = name.removesuffix("-symbolic")
        own = SRC / f"{base}.svg"
        if own.exists():
            svg = own.read_text()
        else:
            src = next((s for s in (fetch(sym, style, filled, offline) for sym in symbols) if s), None)
            if src is None:
                missing.append(f"{theme_name(style, filled)}: {name} ({', '.join(symbols)})")
                continue
            svg = symbolic(src)
        d = Path("symbolic") / context
        files[d / f"{base}-symbolic.svg"] = svg
        if plain:
            files[d / f"{base}.svg"] = svg
    return files, missing


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--style", choices=STYLES, help="build only this style")
    ap.add_argument("--fill", choices=("0", "1"), help="with --style: unfilled (0) or filled (1); default both")
    ap.add_argument("--offline", action="store_true", help="only use the download cache and src/")
    args = ap.parse_args()

    entries = load_map()
    for context, name, _, _ in entries:
        if context not in CONTEXTS:
            print(f"unknown context {context!r} for {name}", file=sys.stderr)
            return 1

    styles = [args.style] if args.style else list(STYLES)
    fills = [args.fill == "1"] if args.fill else [True, False]
    themes: dict[str, dict[Path, str]] = {}
    missing: list[str] = []
    for style in styles:
        for filled in fills:
            files, miss = build_one(entries, style, filled, args.offline)
            themes[theme_name(style, filled)] = files
            missing += miss
            dirs = sorted({str(p.parent) for p in files})
            files[Path("index.theme")] = index_theme(style, filled, dirs)

    if missing:
        print("Symbols not found:\n  " + "\n  ".join(missing), file=sys.stderr)
        return 1

    for name, files in themes.items():
        out = OUT / name
        if out.exists():
            shutil.rmtree(out)
        for path, svg in files.items():
            (out / path).parent.mkdir(parents=True, exist_ok=True)
            (out / path).write_text(svg)
        print(f"Wrote {len(files) - 1} icons to themes/{name}/")
    # droid-icons: the default style under the name droid 1.0 set. A full
    # copy, because Qt ignores a theme without directories, Inherits and all.
    default = OUT / theme_name(*DEFAULT)
    if default.exists():
        alias = OUT / "droid-icons"
        if alias.exists():
            shutil.rmtree(alias)
        shutil.copytree(default, alias)
        index = (alias / "index.theme").read_text()
        index = re.sub(r"^Name=.*$", "Name=Droid\nHidden=true", index, count=1, flags=re.M)
        (alias / "index.theme").write_text(index)
    return 0


if __name__ == "__main__":
    sys.exit(main())
