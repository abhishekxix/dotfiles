# 09 - Make hardware keys reliable

| Field | Value |
|---|---|
| Status | In progress |
| Step | 09 |
| Commit | `CONFIG(09): make hardware keys reliable` |

## Files

- `home/.xbindkeysrc` (EDIT)

## Changes

Remove captured numeric keycode/mask lines and make symbolic keysyms/modifiers
authoritative; add default-sink volume up, down, and mute. Preserve the current
brightness command and prior no-new-brightness-dependency decision in this
step. Keep media/notification bindings in Xbindkeys rather than duplicating
them in Qtile. Keep locking manual; use `xscreensaver-command --lock` for the
lock key and `xscreensaver-command --suspend && systemctl suspend` for suspend
so a failed XScreenSaver request aborts system suspension.

## Test

Automated: `.bin/validate-manifest.py`.

Manual X11: run `xbindkeys --show >/dev/null`; exercise every target symbolic
binding, manual lock, forced lock-command failure, and
the exact `xscreensaver-command --suspend && systemctl suspend` path on the
laptop.

## Acceptance

- [ ] Bindings survive a changed X keycode map because they use symbolic names.
- [ ] Symbolic brightness bindings invoke the unchanged configured command.
- [ ] Speaker controls change the default sink through the already-provisioned audio stack.
- [ ] Manual lock invokes XScreenSaver and suspend-aware failure prevents system suspend.
- [ ] The tested suspend/resume path returns to the lock screen.

## Risks & Rollback

Keysyms vary by hardware. Keep the old file available through the step commit
while testing each symbolic binding on the target laptop.
