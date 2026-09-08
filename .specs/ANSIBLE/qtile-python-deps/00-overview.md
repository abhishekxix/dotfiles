# Declare qtile's Python runtime dependencies in the installer

| Field | Value |
|---|---|
| Status | Done |
| Component | ANSIBLE |
| Created | 2026-09-08 |

## Goal

Represent qtile's runtime Python dependencies in the Ansible vars so a fresh
workstation install needs no manual `apt install` fix-ups, and log the
`packages.json` lexical-ordering convention in `AGENTS.md`.

## Context & Research

- Shell history on this machine shows manual `sudo apt install` of
  `python3-pip`, `python3-psutil`, `python3-venv`, `python3-qtile-extras`,
  `python3-dbus-next`, `python3-dbus`, `python3-dbus-fast`, `python3-pyxdg`,
  `python3-xdg` — trial-and-error fix-ups never captured in the installer.
- **Upstream truth** (qtile `pyproject.toml` @ master + docs.qtile.org
  install guide, checked 2026-09-08):
  - Core deps: `cairocffi`, `cffi`, `xcffib` — already pulled by the apt
    `qtile` package (`python3-qtile` Depends, verified via
    `apt-cache depends python3-qtile` on this machine).
  - apt Recommends (installed by default, but not guaranteed under
    `--no-install-recommends`): `python3-dbus`, `python3-xdg`, `python3-keyring`,
    `lm-sensors`.
  - `optional_core` extra: `dbus-fast` — the docs' notification dep and the
    successor of the legacy `dbus-next` (qtile migrated; `dbus-next` is
    superseded). NOT pulled by apt.
  - `widgets` extra: `psutil`, `pyxdg`, … — NOT pulled by apt.
- **Debian naming**: `python3-xdg` is the Debian binary package that provides
  the `pyxdg` module (there is no `python3-pyxdg`); keep `python3-xdg`.
- **`python3-qtile-extras` is not packaged in Debian trixie** (`apt-cache
  search qtile` finds nothing; user's history entry predates this machine).
  User decision: skip it for now; revisit if packaged or if its widgets are
  needed (would then be a git-source + venv/pip install since it must be
  importable by the qtile process itself).
- `python3-pip` / `python3-venv` are generic tooling, not qtile-specific —
  user decision: generic top-level entries in `packages.json` (both
  workstation + server profiles, matching `curl`/`git`).
- `ansible/vars/package-deps.json` is keyed by dependent package name; deps
  for key `K` install only when `K` is selected for the profile
  (`playbook.yml:22`), in a single apt transaction after the main apt install.
- `ansible/vars/packages.json` keys are kept in lexical order (both top-level
  entries and fields within entries); new entries must be inserted in sorted
  position, not appended.

## Non-goals

- No `python3-qtile-extras` entry (unavailable in trixie; see Context).
- No removal of the redundant `python3-dbus` (apt Recommends already covers
  it; declaring it again would only guard `--no-install-recommends` setups).
- No changes to qtile config under `.config/qtile/`.
- No `python3-dbus-next` entry (superseded by `dbus-fast`).

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

- [x] 01 — qtile runtime deps in package-deps.json (01-qtile-package-deps.md)
- [x] 02 — generic python3-pip / python3-venv entries (02-generic-python-packages.md)
- [x] 03 — lexical-order note in AGENTS.md (03-agents-lexical-order.md)

## Risks & Rollback

- All steps are additive var entries; `git revert` of each commit cleanly
  undoes it. A mistyped package name would fail the apt task loudly
  (`apt-cache policy` confirms all three 01-packages exist in trixie).
