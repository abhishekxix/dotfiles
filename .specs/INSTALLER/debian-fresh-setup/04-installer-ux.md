# 04 — Installer UX

| Field | Value |
|---|---|
| Status | Planning |
| Step | 04 |
| Commit | `INSTALLER(04): add install wrapper and ansible config` |

## Files

- `install` (CREATE, executable bash)
- `ansible.cfg` (CREATE)
- `ansible/inventory.yml` (CREATE)
- `README.md` (CREATE)

## Changes

Recreate the old UX (per user decision — always prompt for become password,
auto-install Ansible; no hybrid/conditional-sudo cleverness).

### `install`

Bash wrapper, `set -Eeuo pipefail`, shellcheck-clean per `.shellcheckrc`:

- Parse `--profile workstation|server` (default `workstation`); reject anything
  else with usage text. Forward it as `-e dotfiles_profile=<value>`.
- If `ansible-playbook` is missing: detect Debian via `/etc/os-release`
  (`ID=debian`, accept `ID_LIKE` containing `debian`); `sudo apt-get update`
  then `sudo apt-get install --yes ansible`. Non-Debian → error telling the
  user v1 supports Debian stable only. Fail if `/etc/os-release` is unreadable.
- `exec ansible-playbook --ask-become-pass ansible/playbook.yml "$@"` so all
  other flags (`--tags packages|dotfiles`, `--check --diff`, `-e ...`) pass
  through. Documented entry points:
  - `./install` (full workstation setup)
  - `./install --profile server` (headless)
  - `./install --tags packages` / `./install --tags dotfiles` (partial runs)
  - `ansible-playbook --check --diff ...` preview (step 05 leans on this)

### `ansible.cfg`

```ini
[defaults]
inventory = ansible/inventory.yml
interpreter_python = auto_silent
retry_files_enabled = false
```

### `ansible/inventory.yml`

```yaml
all:
  hosts:
    localhost:
      ansible_connection: local
```

### `README.md`

`# Dotfiles` + fresh-OS quickstart: clone, `./install` (workstation default),
`./install --profile server`, partial `./install --tags packages|dotfiles`,
conflict-backup note pointing at `~/.local/state/dotfiles/backups/`.

## Acceptance

- [ ] `shellcheck install` is clean; `bash -n install` passes.
- [ ] On Debian stable without Ansible: `./install --help`-equivalent or
  `--check` run installs Ansible via apt and proceeds (test in container or
  by stubbing `ansible-playbook`).
- [ ] `./install --profile bogus` exits non-zero with usage text.
- [ ] `./install --tags dotfiles` runs only linking tasks (no apt activity,
  no password actually needed beyond the prompt); `./install --tags packages`
  runs only installs.
- [ ] `git check-ignore` confirms `install`, `ansible/`, `ansible.cfg`,
  `README.md` are committable (whitelisted in `.gitignore`).
