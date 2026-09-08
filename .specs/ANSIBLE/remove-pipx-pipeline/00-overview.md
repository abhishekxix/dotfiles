# Remove the dormant pipx pipeline

| Field | Value |
|---|---|
| Status | Done |
| Component | ANSIBLE (touches INSTALLER, DOCS in later steps) |
| Created | 2026-09-08 |

## Goal

Delete the pipx package-manager pipeline: the apt `pipx` manifest entry, the
pipx toolchain bootstrap, the `pipx ensurepath` task, the
`community.general.pipx` install task, and the `pipx` source type from the
manifest contract. The pipeline has been dormant since the
`remove-prettier-ruff-lazygit` spec left zero `source: "pipx"` entries; if a
Python-CLI source is ever needed again, `uv` will be evaluated in a fresh
spec (not feasible as a drop-in today: no `uv` CLI in Debian stable, no
`uv_tool` module in community.general).

## Context & Research

- Current pipx touchpoints:
  - `ansible/vars/packages.json` — `pipx` as an **apt** entry (workstation +
    server); the only pipx-related thing actually installed.
  - `ansible/tasks/toolchain.yml` — "Install pipx via apt when a pipx package
    is selected" (never fires: zero pipx-source entries).
  - `ansible/tasks/packages.yml` — `pipx ensurepath` task (gated on
    `dotfiles_pkgs_pipx | length > 0`) and `community.general.pipx` install
    task (same gate; both never fire).
  - `ansible/playbook.yml` — `dotfiles_pkgs_pipx` var + "(cargo, fnm, pipx)"
    task-name comment.
- The `community.general >= 10.7.0` floor (`install` COLLECTION_FLOOR,
  `ansible/requirements.yml`, `ansible/tasks/preflight.yml:31`) was introduced
  **solely** for `pipx: name: pkg==ver` (spec AI-16). The remaining collection
  users (`community.general.cargo`, `.npm`) are far older modules, but the
  floor is kept: it is a known-good floor for them and for the ansible-core
  that Debian stable ships, and `ansible-galaxy` installs the latest
  collection on fresh hosts regardless. Only the now-false justification
  comment is reworded.
- No references to pipx anywhere in `home/` or `.config/` (verified: only
  `.specs/` history, `ansible/`, `.bin/`, `README.md`).
- `pipx` source type appears in three contract places that must stay in sync:
  `packages.schema.json`, `.bin/validate-manifest.py` (SOURCES +
  REQUIRED_FIELDS), and the playbook's per-source task. Data removal
  (`packages.json`) is independent of contract removal (zero pipx entries
  today).

## Non-goals

- No purge/uninstall of the already-installed `pipx` apt package on existing
  hosts (dormant and harmless; `sudo apt remove pipx` manually if wanted).
- No introduction of `uv` (future spec if Python CLI tools are added).
- No changes to the cargo/npm source types or their bootstrap tasks.
- No change to the 10.7.0 community.general floor or `requirements.yml`.
- No edits to historical `.specs/` files.

## Steps

### 01 — Strip pipx from playbook and tasks

- **Files:** `ansible/playbook.yml` (EDIT), `ansible/tasks/toolchain.yml`
  (EDIT), `ansible/tasks/packages.yml` (EDIT), `ansible/tasks/preflight.yml`
  (EDIT)
- **Changes:** drop `dotfiles_pkgs_pipx`; drop the toolchain pipx-apt task;
  drop the `ensurepath` and `community.general.pipx` tasks; fix the playbook
  task-name comment to "(cargo, fnm)"; reword the preflight floor comment so
  it no longer cites `pipx: name: pkg==ver`.
- **Acceptance:**
  - [x] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
  - [x] `grep -rn pipx ansible/` returns nothing (except step 02 scope).

### 02 — Remove pipx from manifest data and schema

- **Files:** `ansible/vars/packages.json` (EDIT), `ansible/vars/packages.schema.json`
  (EDIT)
- **Changes:** delete the `pipx` apt entry (workstation+server selection
  counts drop by 1 each); delete the `pipx` definition and its `oneOf` ref.
- **Acceptance:**
  - [x] `python3 -m json.tool` exits 0 on both files.
  - [x] `.bin/validate-manifest.py` exits 0.

### 03 — Remove pipx from the manifest validator

- **Files:** `.bin/validate-manifest.py` (EDIT)
- **Changes:** drop `"pipx"` from `SOURCES` and from `REQUIRED_FIELDS`, so a
  future `source: "pipx"` entry fails validation instead of silently
  installing nothing.
- **Acceptance:**
  - [x] `.bin/validate-manifest.py` exits 0 on the real manifests.
  - [x] A probe manifest entry with `source: "pipx"` reports an unknown-source
        error (then discarded).

### 04 — Update README

- **Files:** `README.md` (EDIT)
- **Changes:** reword the community.general paragraph: cargo/npm modules;
  10.7.0 kept as a known-good floor.
- **Acceptance:**
  - [x] `grep -rn pipx ansible/ .bin/ README.md` returns nothing.

## Risks & Rollback

- Minimal: every removed task is currently gated to a no-op by zero
  `source: "pipx"` entries, and the apt `pipx` entry removal only stops
  installing a dormant binary on fresh hosts.
- Per-step commits localize any regression to a single `git revert`; step 01
  is the only one that touches playbook behavior.
- If a Python-CLI source is needed again, re-add via a new spec (`uv` or a
  revived `pipx`), not by resurrecting this pipeline.
