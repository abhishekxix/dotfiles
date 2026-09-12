# Dotfiles

Ansible-managed workstation configuration for Debian stable.

## Development

This repository uses spec-driven development. Before implementing a multi-file
or non-trivial change, read `AGENTS.md` and `.specs/README.md`, then draft or
update the matching spec under `.specs/<COMPONENT>/<slug>/` using
`.specs/TEMPLATE.md`. An overview links one numbered file per implementation
step; each step names exact files, executable test commands, and bounded
acceptance criteria. Drafts remain `Planning` until explicitly approved.

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
files remain as editor hints for `$schema` autocompletion. Install the
supported hook with:

```bash
pip install "pre-commit==4.0.1" && pre-commit install
```

CI pins its actions and Python/pre-commit tooling (see
`.github/workflows/validate.yml`), grants only read-only permissions, and
sets timeouts with concurrency cancellation. Every PR runs the fast gate:

```bash
pre-commit run --all-files && python3 -m unittest discover -s .bin/tests -p 'test_*.py' && ansible-playbook --syntax-check ansible/playbook.yml
```

ShellCheck and Ansible syntax also run on a Debian target. Debian-specific
behavior is tested on Debian, never inferred from Ubuntu: the disposable
harness below covers both profiles with two runs (the second must report
`changed=0` or only the documented allowlist):

```bash
.bin/tests/run-debian-integration --profiles workstation,server --runs 2
```

The same harness runs on a weekly schedule in CI; label a PR
`full-integration` to run it there on demand.

The playbook needs the `community.general` collection (cargo and npm
modules; 10.7.0 is kept as a known-good floor). The `install` wrapper
installs it from `ansible/requirements.yml` automatically; for direct
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

Excluded and privileged notes:

- `.config/README.md` is never linked (it is in `dotfiles_config_excludes`).
- Setting the login shell to zsh and any `*.root.*` hook are the only
  privileged dotfile tasks; everything else runs unprivileged.
- `docker-ce` group membership and `libvirt` access take effect only after
  relogin (or `newgrp docker`); see the post-run report after install.

`xorg.conf` is intentionally not installed because it is system- and
hardware-specific.

## Doctor

`.bin/doctor` prints a read-only health report (missing tools grouped by
owning config, installed-vs-manifest Neovim version, broken managed
symlinks). It never installs or changes anything and exits nonzero only
for required gaps:

```bash
.bin/doctor
```

## Package lifecycle

Each manifest entry declares its `source`:

- `apt`: converged to present by the package manager.
- `deb`/`archive`: pinned payloads, SHA-256 verified when `sha256` is
  set; re-extracted only when absent (default) or always in upgrade mode.
- `git`: pinned `version` entries converge in upgrade mode; floating
  (unversioned) clones update only in upgrade mode, never on a default
  existing-install run.
- `script`: installers download to a temporary file before execution
  (never piped from the network to a shell). Entries without an
  upstream-verifiable payload carry an explicit `floating_ok: true`
  exception, install when absent, refresh only in upgrade mode, and
  print a visible integrity warning.

Modes:

```bash
./install            # fresh installs; existing installs left alone
./install --audit    # non-mutating drift report (check + diff)
./install --upgrade  # converge floating sources and declared versions
```

One installer run holds `~/.cache/dotfiles-install.lock`; a second
concurrent run exits with the lock diagnostic instead of interleaving
APT transactions. Repository key rotation requires the manifest's
expected fingerprint to match before the dearmored keyring is replaced.
