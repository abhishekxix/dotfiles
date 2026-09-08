# Set default shell to zsh

| Field | Value |
|---|---|
| Status | In progress |
| Component | ANSIBLE |
| Created | 2026-09-08 |

## Goal

After a fresh `./install` run, the invoking user's login shell is `/usr/bin/zsh`
without any manual `chsh`. Today the playbook installs zsh and links
`~/.zshrc`, but the account keeps `/bin/bash` until the user changes it by hand.

## Context & Research

- `ansible/vars/packages.json` already installs the `zsh` apt package for both
  `workstation` and `server` profiles.
- Debian ships zsh as `/usr/bin/zsh`, which is registered in `/etc/shells` on
  install, so `chsh` (and Ansible's `user` module, which uses it) accepts it.
- The playbook runs as the normal user with per-task `become: true` (see
  `tasks/toolchain.yml` flatpak task); changing `/etc/passwd` requires root.
- `ansible.builtin.user` with a `shell` parameter is the idiomatic, idempotent
  way to do this: it reports `ok` when the shell already matches, `changed`
  only when it differs.
- `tasks/dotfiles.yml` is the user-environment phase and runs after
  `packages.yml`, so zsh is guaranteed present by then. Gating on `zsh` being
  in the selected manifest keeps the task manifest-driven (same pattern as
  `toolchain.yml`'s source gates).
- `ansible_user_id` is the invoking user (preflight already refuses root runs),
  so no extra fact gathering is needed.

## Non-goals

- No `chsh` for other users, root, or multi-host setups (single-user
  fresh-host scope, same as `dotfiles_home` in v1).
- No shell installs outside the manifest; if a future profile drops zsh, the
  gate disables the task rather than failing.
- No change to `~/.zshenv`/`~/.zshrc` contents or to the `install` script.

## Steps

### 01 — Set login shell via user module

- **Files:** `ansible/tasks/dotfiles.yml` (EDIT)
- **Changes:** Add a first task "Set user's default shell to zsh":
  `ansible.builtin.user` with `name: "{{ ansible_user_id }}"`,
  `shell: /usr/bin/zsh`, `become: true`, gated on
  `zsh` being in `dotfiles_packages_selected` keys, tagged `dotfiles`. Placed
  before linking so the very next login on a fresh host uses zsh for the
  linked shell config.
- **Acceptance:**
  - [x] Task reports `changed` while the account uses bash — verified via a check-mode run of the task with a divergent desired shell (this host was already switched to zsh by hand, so the real playbook reports `ok` here).
  - [x] `getent passwd abhi` ends with `/usr/bin/zsh`.
  - [x] Re-running reports `ok` for the task — idempotent (verified in check mode).
  - [x] `--skip-tags packages --list-tasks` shows the task first under the `dotfiles` tag; `--tags dotfiles` unaffected. Privileged real-run re-verification pending user (sudo password required).

## Risks & Rollback

- Lowest risk: if zsh were absent from `/etc/shells` the task would fail
  loudly before touching anything; the manifest gate prevents that on
  profiles without zsh. Revert is a single `git revert` of the step commit.
