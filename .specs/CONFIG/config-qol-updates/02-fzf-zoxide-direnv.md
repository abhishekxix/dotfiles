# 02 - Scope fzf and add zoxide/direnv

| Field | Value |
|---|---|
| Status | In progress |
| Step | 02 |
| Commit | `CONFIG(02): scope fzf and add project-aware shell tools` |

## Files

- `home/.zshrc` (EDIT)
- `home/.bashrc` (EDIT)
- `ansible/vars/packages.json` (EDIT)
- `.bin/tests/test_shell_startup.py` (EDIT)

## Changes

Keep UI-only flags in global fzf options. Apply file previews only to file
selection and directory previews only to directory selection; history and
arbitrary input receive no file preview. Omit a preview when its backing
command is unavailable. Add `zoxide` and `direnv` to workstation and server
profiles and initialize each only when installed.

## Test

Automated: `.bin/validate-manifest.py && bash -n home/.bashrc && zsh -n
home/.zshrc && python3 -m unittest discover -s .bin/tests -p
'test_shell_startup.py'`.

Manual: exercise Ctrl-T, Alt-C, Ctrl-R, zoxide navigation, and direnv
allow/deny behavior in both shells.

## Acceptance

- [ ] Fzf history search no longer treats command text as file paths.
- [ ] File/directory pickers retain useful previews and degrade cleanly.
- [ ] Zoxide navigation works in Bash and Zsh.
- [ ] Direnv remains inactive until a directory is explicitly allowed.

## Risks & Rollback

Direnv evaluates project-controlled environment changes. Explicit review and
`direnv allow` remain mandatory; removing its shell hook disables behavior
without deleting project files.
