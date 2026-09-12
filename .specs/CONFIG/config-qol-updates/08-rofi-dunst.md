# 08 - Reconcile Rofi and Dunst

| Field | Value |
|---|---|
| Status | Approved |
| Step | 08 |
| Commit | `CONFIG(08): reconcile Rofi and Dunst behavior` |

## Files

- `.config/rofi/config.rasi` (EDIT)
- `.config/rofi/themes/catppuccin-mocha.rasi` (EDIT)
- `.config/qtile/config_parts/settings.py` (EDIT)
- `.config/dunst/dunstrc` (EDIT)

## Changes

Enable/configure the Rofi mode Qtile launches and use current option names;
move legacy list layout values into the theme; use Rofi's dmenu-compatible mode
for Dunst actions; retain notifications while the user is idle; delay
noncritical notifications over fullscreen windows while allowing critical
notifications through. Preserve fixed-monitor placement and current
Dunst/Picom corner behavior.

## Test

Automated: `rofi -config "$PWD/.config/rofi/config.rasi" -dump-config
>/dev/null`.

Manual X11: exercise run, desktop, window, and SSH launchers; start Dunst with
`dunst -print`; test actions, idle timeout behavior, and fullscreen normal and
critical notifications.

## Acceptance

- [ ] Both Qtile launcher shortcuts open an enabled Rofi mode without warnings.
- [ ] Dunst actions do not depend on uninstalled dmenu.
- [ ] Idle/fullscreen notification behavior matches the declared policy.

## Risks & Rollback

Rofi option names depend on the Debian package version. Validate against the
installed version and revert only unsupported layout modernization if needed.
