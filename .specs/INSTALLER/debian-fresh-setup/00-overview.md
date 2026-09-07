# Debian Fresh Setup from Scratch

| Field | Value |
|---|---|
| Status | Done |
| Component | INSTALLER |
| Created | 2026-09-04 |

## Goal

Rebuild a from-scratch fresh-OS setup for Debian stable: one `./install --profile workstation|server` command installs the declared application suite and links `home/` + `.config/` into `$HOME`. Previous `install`/`ansible/` implementation in git history is ignored; this spec designs from a clean tree.

## Decisions (confirmed with user)

| Topic | Decision |
|---|---|
| OS scope | Strictly Debian stable only. Ubuntu/Arch/Fedora support is an explicit follow-up. |
| Tool | Ansible (playbook + thin bash wrapper). Alternatives considered: pure bash (simplest, but hand-rolled idempotency), chezmoi/stow (dotfile-focused, weak on packages/services), Nix/home-manager (heaviest, best reproducibility). Ansible chosen as balanced middle. |
| V1 scope | Packages + dotfiles linking only. Full workstation setup (services, fonts, wallpaper, default shell, etc.) is a follow-up. |
| Profiles | Selectable via flag: `--profile workstation` (default, full GUI set) vs `--profile server` (CLI only). Single manifest file, `profiles` tag per entry. |
| Package manifest | JSON, object per package: logical name as key, value is an object with at least `source` + `profiles`. Separate repos file for apt key+repo flows (Docker engine, VSCode). |
| Toolchain gaps | Playbook auto-bootstraps rustup/cargo, fnm/node, pipx when a selected package needs them. |
| URL kinds (v1) | `script` (curl\|sh installer), `deb` (direct .deb download), `archive` (tarball/zip extracted to `~/.local`), `git` (clone + build/install). |
| Installer UX | Keep old UX: `install` is bash, auto-installs Ansible via apt when missing, always `--ask-become-pass`, forwards `--tags packages\|dotfiles` and `--check`. |
| Linking | Keep old behavior: timestamped `~/.local/state/dotfiles/backups/<ts>/`, idempotent, exclude `.config/README.md`. `.bin/` is NOT handled automatically. |

## Context & Research

- The repo's deleted implementation (still visible in git history, `git show HEAD:install`, `git show HEAD:ansible/playbook.yml`) did: bash wrapper auto-installing Ansible per `ID_LIKE`/`ID` (debian/ubuntu, fedora/rhel, arch), `ansible-playbook --ask-become-pass`, `vars/main.yml` with `dotfiles_common_packages` + `dotfiles_packages_by_os_family[os_family]`, `tasks/link.yml` with stat → fail-or-backup → `mv` → symlink. This spec keeps the UX and linking semantics but replaces the package model with JSON + profiles and adds multi-source installs.
- Old `vars/main.yml` starting package list (reference only, step 01 refines): common `curl git tmux zsh`; Debian extras `alacritty dunst flameshot neovim picom rofi xbindkeys xscreensaver`.
- Old tags `packages` / `dotfiles`, `ansible.cfg` (`inventory = ansible/inventory.yml`, `interpreter_python = auto_silent`, `retry_files_enabled = false`), localhost `ansible_connection: local`.
- `.gitignore` whitelists `/ansible/`, `/ansible.cfg`, `/install`, `/README.md`, `/home/`, `/.config/`, `/.bin/`, `/.specs/` — new files under those paths are committable.
- `.shellcheckrc` exists — the `install` wrapper must stay shellcheck-clean.

## Non-goals

- Do **not** support Ubuntu/Arch/Fedora in v1 (follow-up, even though Debian-family abstraction would be cheap).
- Do **not** do full workstation setup: no services, fonts, wallpaper, default-shell changes in v1.
- Do **not** handle `.bin/` automatically.
- Do **not** reuse or revive the deleted `vars/main.yml` YAML package lists; the JSON manifest replaces them.
- Do **not** add `cargo`/`npm`/`script` checksum enforcement in v1 beyond documenting optional `sha256` fields (checksum-verified installs are a hardening follow-up).

## Follow-ups (explicitly deferred)

1. **Multi-distro:** Ubuntu + Arch/Fedora via `os_family` package overlays.
2. **Full workstation setup:** services, fonts, wallpaper, default shell, `xorg.conf`.
3. **Checksum enforcement:** require/verify `sha256` for `script`/`deb`/`archive` sources.

## Steps

Each step maps to exactly one commit, named `INSTALLER(<NN>): <summary>`.

| # | File | Area |
|---|------|------|
| 00 | `00-overview.md` | This overview (no commit) |
| 01 | `01-package-manifest-schema.md` | `ansible/vars/packages.json` — JSON object-per-package + `profiles` tags |
| 02 | `02-apt-repos.md` | `ansible/vars/repos.json` + key/repo tasks (Docker, VSCode pattern) |
| 03 | `03-multi-source-install.md` | `ansible/playbook.yml` — apt/cargo/npm/pipx/script/deb/archive/git + toolchain bootstrap |
| 04 | `04-installer-ux.md` | `install`, `ansible.cfg`, `ansible/inventory.yml`, `README.md` |
| 05 | `05-dotfile-linking.md` | `ansible/playbook.yml` + `ansible/tasks/link.yml` — home/ + .config/ linking |

## Status checklist

- [x] 01 — Package manifest schema
- [x] 02 — Apt repos file
- [x] 03 — Multi-source install + toolchain bootstrap
- [x] 04 — Installer UX
- [x] 05 — Dotfile linking

## Risks & Rollback

- **Third-party apt repos (step 02):** wrong `signed-by` keyring path or repo line breaks all apt installs. Mitigation: key/repo tasks run before any install; verify with `apt-get update` in acceptance. Rollback: `git revert` the step; repos are only added, never purged, so a revert commit should also document manual removal (`/etc/apt/sources.list.d/`, `/usr/share/keyrings/`).
- **`curl|sh` scripts (step 03):** upstream script changes can break idempotency or install outside package managers. Mitigation: every `script` entry declares a `creates:` marker; tasks use it for idempotency. Rollback per-step via `git revert`.
- **Toolchain bootstrap ordering (step 03):** cargo/npm installs fail if rustup/fnm tasks run after them. Mitigation: bootstrap tasks are ordered first and gated on "any selected package needs this toolchain".
- **Symlink conflicts (step 05):** backup-then-link moves real user files. Mitigation: timestamped backup dir, `--check --diff` preview, idempotent re-runs. Rollback: restore from `~/.local/state/dotfiles/backups/<ts>/`.

Each step is its own commit, so `git revert` or `git bisect` localizes any regression.
