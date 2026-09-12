# 11 - Make wallpaper/screenshots portable

| Field | Value |
|---|---|
| Status | Approved |
| Step | 11 |
| Commit | `CONFIG(11): make wallpaper and screenshots portable` |

## Files

- `.bin/change_wallpaper.sh` (EDIT)
- `.bin/screens.sh` (EDIT)
- `.config/qtile/autostart.sh` (EDIT)
- `.config/flameshot/flameshot.ini` (EDIT)
- `ansible/vars/packages.json` (EDIT)

## Changes

Canonicalize an explicitly selected wallpaper before persistence; reconstruct
per-output wallpaper commands with arrays so spaces survive login; label the
static screen script as a superseded emergency fallback; remove the hardcoded
fixed Flameshot home path and use portable/XDG behavior; explicitly declare
`x11-xserver-utils`, which supplies the non-base `xrandr` dependency.

## Test

Automated: `shellcheck .bin/change_wallpaper.sh .bin/screens.sh
.config/qtile/autostart.sh && bash -n .bin/change_wallpaper.sh
.config/qtile/autostart.sh && sh -n .bin/screens.sh &&
.bin/validate-manifest.py`.

Manual X11: use a wallpaper filename containing spaces through selection,
login, and monitor replug; save a screenshot as a fresh user.

## Acceptance

- [ ] Wallpaper state is absolute and safe for spaces across login/hotplug.
- [ ] The emergency screen script cannot be mistaken for current automation.
- [ ] Screenshots do not depend on `/home/abhi` existing.
- [ ] Non-base runtime commands used by affected scripts are manifest-backed.

## Risks & Rollback

Flameshot's XDG behavior varies by packaged version. Verify the effective save
directory before removing the fixed path.
