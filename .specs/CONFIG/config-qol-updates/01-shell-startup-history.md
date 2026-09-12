# 01 - Harden shell startup and history

| Field | Value |
|---|---|
| Status | In progress |
| Step | 01 |
| Commit | `CONFIG(01): harden shell startup and history` |

## Files

- `home/.zshrc` (EDIT)
- `home/.bashrc` (EDIT)
- `.bin/tests/test_shell_startup.py` (CREATE)

## Changes

Create the Zsh completion-cache parent before `compinit`; guard plugin and
Starship initialization; initialize autosuggestions and later widgets before
sourcing syntax highlighting last; keep one coherent Zsh shared-history mode
with additional in-memory capacity for duplicate expiry; compose Bash history
import/export without replacing an existing `PROMPT_COMMAND`; set `GPG_TTY`
only in interactive shells. Keep eager guarded fnm and `EDITOR=vim` unchanged.

## Test

Automated: `bash -n home/.bashrc && zsh -n home/.zshrc && python3 -m
unittest discover -s .bin/tests -p 'test_shell_startup.py'`.

The unit test creates disposable homes with plugin/Starship paths present and
absent. Manual: exercise history in two concurrent shells; after tmux reattach,
run `printf test | gpg --clearsign >/dev/null` without creating a Git commit.

## Acceptance

- [ ] Zsh and Bash start without errors on a partial installation.
- [ ] The Zsh completion dump persists under the XDG cache directory.
- [ ] Commands entered in one live shell appear in another without replacing unrelated prompt hooks.
- [ ] GPG signing sees the current terminal after tmux attach/reattach.

## Risks & Rollback

History import/export can duplicate entries or interfere with prompt hooks if
composed incorrectly. Restore the prior history options and prompt behavior if
the concurrent-shell test regresses.
