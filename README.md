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

## Customize

Edit `ansible/vars/packages.json` to change the package manifest (one object
per package with `source` + `profiles`) and `ansible/vars/repos.json` for
third-party apt signing keys and repository lines.

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
