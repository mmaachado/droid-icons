# droid-icons

Android-style system icons for Linux desktops: Google's
[Material Symbols](https://fonts.google.com/icons) (Rounded, filled) as a
freedesktop icon theme that only covers status and symbolic UI icons:
Wi-Fi, Ethernet, Bluetooth, battery, volume, brightness, notifications,
media controls, session actions and the usual arrows and buttons.

Everything else, app icons included, falls through to
[Tela-circle](https://github.com/vinceliuice/Tela-circle-icon-theme)
(`Inherits=Tela-circle,breeze,hicolor`), so the desktop keeps Tela's apps
and folders with Android's system glyphs on top.

## Install

```sh
./install.sh            # copies droid-icons/ to ~/.local/share/icons/droid-icons
kwriteconfig6 --file kdeglobals --group Icons --key Theme droid-icons   # KDE
gsettings set org.gnome.desktop.interface icon-theme droid-icons        # GTK
```

Tela-circle has to be installed too.

## How it's built

`map.toml` maps freedesktop icon names to Material Symbols names.
`build.py` downloads each symbol (Rounded, FILL 1, weight 400, grade 0,
24 px optical size) from Google Fonts, makes it a recolourable symbolic
SVG and writes the theme to `droid-icons/`. The generated theme is
committed, so installing needs no network.

```sh
python3 -I build.py     # needs Python 3.11+ (tomllib), no other dependencies
```

- Every entry is written as `name-symbolic.svg`. Entries in the `[plain]`
  tables are also written as `name.svg`, which is what KDE's tray, OSD and
  applets ask for. Generic actions (`go-next`, `edit-delete`, ...) stay
  symbolic-only, so app toolbars keep Tela's look.
- A value can list fallbacks, e.g. `["battery_android_frame_6", "battery_6_bar"]`.
  The first one that exists is used.
- SVGs in `src/` named like a freedesktop icon win over downloaded ones.
- Icons use KDE's `ColorScheme-Text` stylesheet with `fill="currentColor"`,
  so Plasma and Qt recolour them to the colour scheme, and GTK recolours
  them as symbolic icons. The fallback colour is `#dfdfdf`, for dark panels.

## Licence

The build scripts are Apache-2.0. The icons are Material Symbols by Google,
also Apache-2.0. See `NOTICE`.
