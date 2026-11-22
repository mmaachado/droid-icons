#!/usr/bin/env python3
"""Build the droid-icons theme from map.toml.

Downloads Material Symbols Rounded (filled) SVGs from Google Fonts, turns
them into recolourable symbolic icons and writes the theme to droid-icons/.

    python3 -I build.py            build (downloads are cached in .cache/)
    python3 -I build.py --offline  only use the cache and src/
"""

from __future__ import annotations

import re
import shutil
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "droid-icons"
CACHE = HERE / ".cache"
SRC = HERE / "src"

URL = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsrounded/{name}/{fill}/24px.svg"
# Fallback colour when nothing recolours the icon (dark panels, like Tela-circle's).
TEXT = "#dfdfdf"

CONTEXTS = {
    "actions": "Actions",
    "apps": "Applications",
    "devices": "Devices",
    "places": "Places",
    "status": "Status",
}


def fetch(symbol: str, offline: bool) -> str | None:
    """SVG source of a Material symbol, or None if it doesn't exist.

    `symbol` may end in "@0" for the outlined (FILL 0) variant.
    """
    name, _, fill = symbol.partition("@")
    fill = "fill1" if fill != "0" else "default"
    cached = CACHE / f"{name}.{fill}.svg"
    if cached.exists():
        return cached.read_text() or None
    if offline:
        return None
    req = urllib.request.Request(URL.format(name=name, fill=fill), headers={"User-Agent": "droid-icons-build"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            svg = r.read().decode()
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        svg = ""
    CACHE.mkdir(exist_ok=True)
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


def index_theme(dirs: list[str]) -> str:
    lines = [
        "[Icon Theme]",
        "Name=Droid",
        "Comment=Material Symbols Rounded system icons on top of Tela-circle",
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


def main() -> int:
    offline = "--offline" in sys.argv
    entries = load_map()
    missing: list[str] = []
    files: dict[Path, str] = {}

    for context, name, symbols, plain in entries:
        if context not in CONTEXTS:
            print(f"unknown context {context!r} for {name}", file=sys.stderr)
            return 1
        base = name.removesuffix("-symbolic")
        own = SRC / f"{base}.svg"
        if own.exists():
            svg = own.read_text()
        else:
            src = next((s for s in (fetch(sym, offline) for sym in symbols) if s), None)
            if src is None:
                missing.append(f"{name} ({', '.join(symbols)})")
                continue
            svg = symbolic(src)
        d = Path("symbolic") / context
        files[d / f"{base}-symbolic.svg"] = svg
        if plain:
            files[d / f"{base}.svg"] = svg

    if missing:
        print("Symbols not found:\n  " + "\n  ".join(missing), file=sys.stderr)
        return 1

    if OUT.exists():
        shutil.rmtree(OUT)
    for path, svg in files.items():
        (OUT / path).parent.mkdir(parents=True, exist_ok=True)
        (OUT / path).write_text(svg)
    dirs = sorted({str(p.parent) for p in files})
    (OUT / "index.theme").write_text(index_theme(dirs))
    print(f"Wrote {len(files)} icons in {len(dirs)} folders to {OUT.relative_to(HERE)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
