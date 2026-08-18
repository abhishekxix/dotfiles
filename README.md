# Dotfiles

Ansible-managed workstation configuration for Linux.

## Install

Clone the repository, then run:

```bash
./install
```

The installer bootstraps Ansible when necessary, asks for the privilege-escalation
password, installs the configured applications, and creates these links:

- Every immediate child of `home/` is linked directly into `$HOME`.
- Every immediate child of `.config/` is linked into `$HOME/.config`.

Existing destinations that are not already the correct symlink are moved to a
timestamped directory under `~/.local/state/dotfiles/backups/` before linking.
The operation is idempotent, so subsequent runs only apply new or changed items.

## Customize

Edit `ansible/vars/main.yml` to change package lists, config exclusions, or
conflict backup behavior. Package names are grouped by Ansible OS family because
names differ between distributions.

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
