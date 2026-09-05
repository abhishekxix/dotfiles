# 05 — Dotfile linking

| Field | Value |
|---|---|
| Status | Done |
| Step | 05 |
| Commit | `INSTALLER(05): link home and config entries with backup` |

## Files

- `ansible/playbook.yml` (EDIT — linking tasks)
- `ansible/tasks/link.yml` (CREATE — shared stat/backup/link unit)

## Changes

Keep the old linking semantics exactly (user decision): every immediate child
of `home/` links into `$HOME`; every immediate child of `.config/` links into
`$HOME/.config`, except `.config/README.md`. Idempotent; conflicts move to a
timestamped `~/.local/state/dotfiles/backups/<iso8601_basic_short>/` dir.

- Ensure `~/.config` exists (`0755`), tagged `dotfiles`.
- `find` (non-recursive, include hidden) over repo `home/` and `.config/`;
  filter `.config` results against an excludes list (`README.md`).
- Reusable `ansible/tasks/link.yml` included per entry with
  `link_source` / `link_destination` / `link_backup_group` (`home`|`config`):
  `stat` (no follow) → `fail` when `dotfiles_backup_conflicts` is false and
  the destination is not already the managed symlink → `mkdir -p` backup group
  dir (`0700`) → `mv` conflict into it → `file: state=link` (no force; correct
  links are left untouched so re-runs are no-ops). In `--check` mode the
  `mkdir`/`mv`/real link steps are skipped and `debug` predict-tasks report the
  planned backup + link instead, so preview no longer errors on conflicts.
- `dotfiles_backup_conflicts: true` default (overridable via `-e`); backup
  root derived from `ansible_facts.user_dir` + `ansible_date_time`, not
  hardcoded `/home/`.
- All tasks tagged `dotfiles`. No profile gating — both profiles get identical
  links. `.bin/` is explicitly untouched.

## Acceptance

- [ ] Fresh link: `./install --profile server --tags dotfiles` creates correct
  symlinks for every `home/` child and every `.config/` child except
  `README.md` (`ls -l ~/.config/README.md` shows no repo symlink).
- [ ] Idempotency: immediate re-run reports `ok`, `changed=0`.
- [ ] Conflict: place a regular file at `~/.zshrc`, re-run, confirm it moved
  under `~/.local/state/dotfiles/backups/<ts>/home/` and `~/.zshrc` is now the
  managed symlink.
- [ ] Correct-link no-op: re-run with links already correct creates no new
  backup directory.
- [ ] Preview: `ansible-playbook --check --diff --skip-tags packages
  ansible/playbook.yml` accurately predicts link changes.
- [ ] Opt-out: `-e dotfiles_backup_conflicts=false` with a conflicting file
  fails with the "already exists" message instead of moving anything.
