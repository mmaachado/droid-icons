# droid-icons

Android-style system icons for Linux desktops: Google's
[Material Symbols](https://fonts.google.com/icons) as freedesktop icon
themes that only cover status and symbolic UI icons:
Wi-Fi, Ethernet, Bluetooth, battery, volume, brightness, notifications,
media controls, session actions and the usual arrows and buttons.

Everything else, app icons included, falls through to
[Tela-circle](https://github.com/vinceliuice/Tela-circle-icon-theme)
(`Inherits=Tela-circle,breeze,hicolor`), so the desktop keeps Tela's apps
and folders with Android's system glyphs on top.

## Styles

Every Material Symbols family comes filled or unfilled, one theme each:

| Theme | Style | Wi-Fi | Battery | Volume | Power |
| --- | --- | --- | --- | --- | --- |
| `droid-icons-rounded-filled` | Rounded, filled (default) | <img src="themes/droid-icons-rounded-filled/symbolic/status/network-wireless-signal-good-symbolic.svg" width="20"> | <img src="themes/droid-icons-rounded-filled/symbolic/status/battery-level-60-symbolic.svg" width="20"> | <img src="themes/droid-icons-rounded-filled/symbolic/status/audio-volume-medium-symbolic.svg" width="20"> | <img src="themes/droid-icons-rounded-filled/symbolic/actions/system-shutdown-symbolic.svg" width="20"> |
| `droid-icons-rounded` | Rounded | <img src="themes/droid-icons-rounded/symbolic/status/network-wireless-signal-good-symbolic.svg" width="20"> | <img src="themes/droid-icons-rounded/symbolic/status/battery-level-60-symbolic.svg" width="20"> | <img src="themes/droid-icons-rounded/symbolic/status/audio-volume-medium-symbolic.svg" width="20"> | <img src="themes/droid-icons-rounded/symbolic/actions/system-shutdown-symbolic.svg" width="20"> |
| `droid-icons-outlined-filled` | Outlined, filled | <img src="themes/droid-icons-outlined-filled/symbolic/status/network-wireless-signal-good-symbolic.svg" width="20"> | <img src="themes/droid-icons-outlined-filled/symbolic/status/battery-level-60-symbolic.svg" width="20"> | <img src="themes/droid-icons-outlined-filled/symbolic/status/audio-volume-medium-symbolic.svg" width="20"> | <img src="themes/droid-icons-outlined-filled/symbolic/actions/system-shutdown-symbolic.svg" width="20"> |
| `droid-icons-outlined` | Outlined | <img src="themes/droid-icons-outlined/symbolic/status/network-wireless-signal-good-symbolic.svg" width="20"> | <img src="themes/droid-icons-outlined/symbolic/status/battery-level-60-symbolic.svg" width="20"> | <img src="themes/droid-icons-outlined/symbolic/status/audio-volume-medium-symbolic.svg" width="20"> | <img src="themes/droid-icons-outlined/symbolic/actions/system-shutdown-symbolic.svg" width="20"> |
| `droid-icons-sharp-filled` | Sharp, filled | <img src="themes/droid-icons-sharp-filled/symbolic/status/network-wireless-signal-good-symbolic.svg" width="20"> | <img src="themes/droid-icons-sharp-filled/symbolic/status/battery-level-60-symbolic.svg" width="20"> | <img src="themes/droid-icons-sharp-filled/symbolic/status/audio-volume-medium-symbolic.svg" width="20"> | <img src="themes/droid-icons-sharp-filled/symbolic/actions/system-shutdown-symbolic.svg" width="20"> |
| `droid-icons-sharp` | Sharp | <img src="themes/droid-icons-sharp/symbolic/status/network-wireless-signal-good-symbolic.svg" width="20"> | <img src="themes/droid-icons-sharp/symbolic/status/battery-level-60-symbolic.svg" width="20"> | <img src="themes/droid-icons-sharp/symbolic/status/audio-volume-medium-symbolic.svg" width="20"> | <img src="themes/droid-icons-sharp/symbolic/actions/system-shutdown-symbolic.svg" width="20"> |

`droid-icons` is a hidden copy of Rounded Filled, the name droid 1.0 used.
In [droid](https://github.com/mmaachado/droid), Settings → Appearance →
System icons switches between them (`kshell icons on <style> <filled|outline>`).

## Install

```sh
./install.sh            # copies every theme in themes/ to ~/.local/share/icons/
kwriteconfig6 --file kdeglobals --group Icons --key Theme droid-icons-sharp   # KDE
gsettings set org.gnome.desktop.interface icon-theme droid-icons-sharp        # GTK
```

Tela-circle has to be installed too.

## How it's built

`map.toml` maps freedesktop icon names to Material Symbols names.
`build.py` downloads each symbol in every family (Rounded, Outlined,
Sharp; FILL 1 and 0; weight 400, grade 0, 24 px optical size) from Google
Fonts, makes it a recolourable symbolic SVG and writes the themes to
`themes/`. The generated themes are committed, so installing needs no
network. `--style sharp --fill 0` builds a single one.

```sh
python3 -I build.py     # needs Python 3.11+ (tomllib), no other dependencies
```

- Every entry is written as `name-symbolic.svg`. Entries in the `[plain]`
  tables are also written as `name.svg`, which is what KDE's tray, OSD and
  applets ask for. Generic actions (`go-next`, `edit-delete`, ...) stay
  symbolic-only, so app toolbars keep Tela's look.
- A value can list fallbacks, e.g. `["battery_android_frame_6", "battery_6_bar"]`.
  `symbol@0` is always unfilled and `symbol@1` always filled, whatever the theme.
  The first one that exists is used.
- SVGs in `src/` named like a freedesktop icon win over downloaded ones.
- Icons use KDE's `ColorScheme-Text` stylesheet with `fill="currentColor"`,
  so Plasma and Qt recolour them to the colour scheme, and GTK recolours
  them as symbolic icons. The fallback colour is `#dfdfdf`, for dark panels.

## Licence

The build scripts are Apache-2.0. The icons are Material Symbols by Google,
also Apache-2.0. See `NOTICE`.
