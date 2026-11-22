#!/usr/bin/env bash
# Install the droid-icons theme for the current user.
#   ./install.sh            install to ~/.local/share/icons/droid-icons
#   ./install.sh --build    rebuild from map.toml first (needs network)
#   ./install.sh --remove   uninstall
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/icons/droid-icons"

case "${1:-}" in
    --remove)
        rm -rf "$DEST"
        echo "Removed $DEST"
        exit 0
        ;;
    --build)
        python3 -I "$HERE/build.py"
        ;;
esac

[[ -f $HERE/droid-icons/index.theme ]] || { echo "No built theme: run ./install.sh --build" >&2; exit 1; }
[[ -d "${XDG_DATA_HOME:-$HOME/.local/share}/icons/Tela-circle" || -d /usr/share/icons/Tela-circle ]] \
    || echo "warning: Tela-circle isn't installed; app icons will fall back to breeze/hicolor" >&2

rm -rf "$DEST"
mkdir -p "$(dirname "$DEST")"
cp -r "$HERE/droid-icons" "$DEST"
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q -f -t "$DEST" || true
# Plasma caches icons per theme; drop the cache so changes show up.
rm -f "${XDG_CACHE_HOME:-$HOME/.cache}"/icon-cache.kcache
echo "Installed to $DEST"
