# 05 — gitconfig hygiene + shell history/aliases

| Field | Value |
|---|---|
| Status | Planning |
| Step | 05 |
| Commit | `CONFIG(05): gitconfig prune/autosetup/rebase, shared history, converged aliases` |

## Files

- `home/.gitconfig` (EDIT)
- `home/.zshrc` (EDIT)
- `home/.bashrc` (EDIT)

## Changes

1. Drop `credential.helper = store` (`.gitconfig:39`) **only if**
   `~/.git-credentials` is empty/absent — the gh helpers (lines 47–50)
   cover github/gist. If non-empty, keep `store` and close that hunk.
2. Add `fetch.prune`, `push.autoSetupRemote`, `pull.rebase`, plus neutral
   diff niceties (`column.ui=auto`, `diff.colorMoved`).
3. zsh history: add `share`/`append`/`inc_append`/`history_verify` (keep the
   existing dedup opts); tune bash history to match.
4. Remove the duplicated `autocd`/`auto_cd` (`.zshrc:2,7` set the same option
   twice).
5. Converge the ls/cp/mv/rm alias sets between bash/zsh — keep or drop `-i`
   consistently (confirm with user at review; `-i` is a foot-gun either way
   until it's consistent).
6. Add a `bash-completion` source guarded by file-exists.

## Test

- `git config --list --show-origin`; `gh auth git-credential` still fills
  github creds.
- New shells share history across sessions; `set -o` shows no duplicates.

## Acceptance

- [ ] no plaintext credential path when gh covers it; prune/autosetup/rebase active
- [ ] history shared + verified; no duplicated shell options
