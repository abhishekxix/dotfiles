# Dotfiles

Ansible-managed workstation configuration for Debian stable.

## Install

Clone the repository, then run:

```bash
./install
```

This installs the full workstation set (default profile), asks for the
privilege-escalation password, installs the declared applications, and links
dotfiles into `$HOME`:

- Every immediate child of `home/` is linked directly into `$HOME`.
- Every immediate child of `.config/` is linked into `$HOME/.config`.

For a headless machine, use the server profile (CLI tools only):

```bash
./install --profile server
```

Existing destinations that are not already the correct symlink are moved to a
timestamped directory under `~/.local/state/dotfiles/backups/` before linking.
The operation is idempotent, so subsequent runs only apply new or changed items.
Backup directories use microsecond timestamps, so back-to-back runs never
collide; old backups are kept (never auto-pruned) — delete them yourself once
you are sure nothing valuable is inside.

Post-install notes:

- `docker-ce` adds your user to the `docker` group automatically, but group
  membership takes effect only after you log out and back in (or run
  `newgrp docker`).
- Switching profiles (`workstation` → `server`) does not remove third-party
  apt repos that are no longer referenced. To clean up manually, delete the
  stale files under `/etc/apt/sources.list.d/` and `/usr/share/keyrings/`
  (e.g. `vscode.list` + `packages.microsoft.gpg`).

## Customize

Edit `ansible/vars/packages.json` to change the package manifest (one object
per package with `source` + `profiles`) and `ansible/vars/repos.json` for
third-party apt signing keys and repository lines.

Manifest edits are validated by `.bin/validate-manifest.py` (stdlib-only),
run by [pre-commit](https://pre-commit.com) locally and in CI, and re-checked
by the playbook's preflight before any change. `ansible/vars/*.schema.json`
files remain as editor hints for `$schema` autocompletion. Enable the hook
with:

```bash
pip install pre-commit && pre-commit install
```

The playbook needs the `community.general` collection (cargo/npm/pipx
modules, minimum version 10.7.0 for `pipx: name: pkg==ver`). The `install`
wrapper installs it from `ansible/requirements.yml` automatically; for direct
`ansible-playbook` runs, install it once with:

```bash
ansible-galaxy collection install -r ansible/requirements.yml
```

Useful targeted runs:

```bash
# Preview dotfile changes without installing packages.
ansible-playbook --check --diff --skip-tags packages ansible/playbook.yml

# Only install applications.
./install --tags packages

# Only manage symlinks. This still asks for a password but does not use it.
./install --tags dotfiles
```

`xorg.conf` is intentionally not installed because it is system- and
hardware-specific.
