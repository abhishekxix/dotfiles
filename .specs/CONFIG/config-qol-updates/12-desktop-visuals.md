# 12 - Unify desktop visual defaults

| Field | Value |
|---|---|
| Status | Approved |
| Step | 12 |
| Commit | `CONFIG(12): unify desktop visual defaults` |

## Files

- `.config/lxsession/qtile/desktop.conf` (EDIT)
- `home/.gtkrc-2.0` (EDIT)
- `home/.Xresources` (EDIT)
- `.config/qtile/config.py` (EDIT)
- `.config/picom.conf` (EDIT)

## Changes

Make Yaru Purple Dark, Ubuntu, Papirus Dark, and `breeze_cursors` size 16 the
deliberate GTK/Xcursor policy. Remove the hardcoded user include and
contradictory sound/hinting settings; give Qtile an explicit Nerd Font fallback
for private-use glyphs; remove or mark Picom's inactive kernel-blur setting
while retaining dual-Kawase and square Dunst corners. Keep the existing qt6ct
platform-theme selection unchanged; Yaru is not asserted as a Qt style.

## Test

Automated: `fc-match 'Ubuntu' && fc-match 'Iosevka Nerd Font'`.

Manual X11: confirm `yaru-theme-gtk` supplies the selected identifier, then use
a fresh login with representative GTK2/GTK3 applications. Census every glyph
literal in `.config/qtile/config_parts/screens.py`, inspect cursor identity/size,
run `picom --config "$PWD/.config/picom.conf" --diagnostics`, and smoke-test
one Qt application for regression from qt6ct.

## Acceptance

- [ ] GTK2/GTK3 and Xcursor use the selected theme/font/icon/cursor policy.
- [ ] Every configured Qtile bar glyph passes the font-chain census and renders correctly.
- [ ] Qt applications retain their current qt6ct behavior.
- [ ] `blur-kern` is absent while `blur-method = "dual_kawase"` remains.

## Risks & Rollback

The manifest already declares `yaru-theme-gtk`; verify that Debian's package
contains `Yaru-purple-dark` before making it authoritative. Retain the current
working GTK fallback if that identifier is unavailable.
