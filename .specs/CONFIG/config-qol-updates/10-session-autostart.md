# 10 - Establish one session/autostart owner

| Field | Value |
|---|---|
| Status | Planning |
| Step | 10 |
| Commit | `CONFIG(10): establish one session and autostart owner` |

## Files

- `.config/qtile/autostart.sh` (EDIT)
- `.config/lxsession/qtile/desktop.conf` (EDIT)
- `home/.xsessionrc` (CREATE)

## Changes

Set session-wide XDG/scale values from Debian Xsession before Qtile starts
rather than only for autostart children. GNOME Keyring initialized through the
PAM/Xsession path owns SSH keys and secrets; disable LXSession's separate
`ssh-agent` owner and verify the keyring environment reaches Qtile-launched
terminals. Disable LXSession application autostart and keep Qtile's guarded
script as the single owner of picom, Xbindkeys, Flameshot, Dunst, volumeicon,
CopyQ, nm-applet, blueman-applet, and XScreenSaver. Flameshot's own
startup-launch setting remains disabled/unset.

## Test

Automated: `bash -n .config/qtile/autostart.sh && sh -n home/.xsessionrc`.

Manual X11 after a fresh login: inspect Qtile and child process environments,
verify `SSH_AUTH_SOCK`, secret-service unlock, one instance/tray icon per
daemon, and a clean session log.

## Acceptance

- [ ] Qtile and its launchers inherit the intended XDG session identity.
- [ ] Exactly one agent owns SSH keys and GNOME secrets remain available.
- [ ] The nine named Qtile-managed processes each have one owner and at most one running instance.

## Risks & Rollback

Display managers differ in startup order. Confirm Debian Xsession loads
`.xsessionrc` on the target before removing the existing fallback exports.
