# 03 - Improve Git conflict/tool ergonomics

| Field | Value |
|---|---|
| Status | In progress |
| Step | 03 |
| Commit | `CONFIG(03): improve Git conflict and tool ergonomics` |

## Files

- `home/.gitconfig` (EDIT)

## Changes

Quote every temporary path passed to Neovim diff/merge tools; disable the
per-file difftool prompt; use `zdiff3` after confirming the minimum supported
Git version; enable recorded conflict-resolution reuse; add a read-only alias
that reports local branches whose upstream is gone. Do not add autocorrect,
automatic pruning/deletion/rebase, or credential-helper changes.

## Test

Automated: `git config --file home/.gitconfig --list >/dev/null`.

Manual fixture: invoke diff/merge from a disposable repository path containing
spaces, resolve the same synthetic conflict twice, and run the gone-branch
report with zero and multiple matches.

## Acceptance

- [ ] Neovim diff/merge commands work for repository paths containing spaces.
- [ ] Repeated conflicts offer the recorded resolution for review.
- [ ] Before/after refs in the zero/multiple-match fixtures are identical after the report.

## Risks & Rollback

Rerere can replay an obsolete resolution. Inspect every replay before commit;
clear repository-local recorded state when it is no longer applicable.
