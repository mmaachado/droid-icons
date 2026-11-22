#!/usr/bin/env bash
# Install the droid-icons themes (every style) for the current user.
#   ./install.sh            install themes/* to ~/.local/share/icons/
#   ./install.sh --build    rebuild from map.toml first (needs network)
#   ./install.sh --remove   uninstall
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
ICONS="${XDG_DATA_HOME:-$HOME/.local/share}/icons"

case "${1:-}" in
    --remove)
        for theme in "$HERE"/themes/*/; do
            rm -rf "${ICONS:?}/$(basename "$theme")"
        done
        echo "Removed the droid-icons themes from $ICONS"
        exit 0
        ;;
    --build)
        python3 -I "$HERE/build.py"
        ;;
esac

compgen -G "$HERE/themes/*/index.theme" >/dev/null || { echo "No built themes: run ./install.sh --build" >&2; exit 1; }
[[ -d $ICONS/Tela-circle || -d /usr/share/icons/Tela-circle ]] \
    || echo "warning: Tela-circle isn't installed; app icons will fall back to breeze/hicolor" >&2

mkdir -p "$ICONS"
for theme in "$HERE"/themes/*/; do
    name=$(basename "$theme")
    rm -rf "${ICONS:?}/$name"
    cp -r "$theme" "$ICONS/$name"
    if [[ -d $ICONS/$name/symbolic ]] && command -v gtk-update-icon-cache >/dev/null; then
        gtk-update-icon-cache -q -f -t "$ICONS/$name" || true
    fi
    echo "Installed $name"
done
# Plasma caches icons per theme; drop the cache so changes show up.
rm -f "${XDG_CACHE_HOME:-$HOME/.cache}"/icon-cache.kcache
