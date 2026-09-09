# Installer hook scripts

| Field | Value |
|---|---|
| Status | Approved |
| Component | ANSIBLE |

## Goal

Move all before/after logic for package installs out of
`ansible/tasks/packages.yml` into plain `bash`/`python` scripts under
`ansible/hooks/`, dispatched by two generic tasks. The playbook shrinks;
every special case becomes an idempotent ensure-state script.

## Context & Research

- `packages.yml` accumulates per-package special cases, each a bespoke
  task with `when:` gates mirroring package selection: mscopefonts EULA
  preseed (`packages.yml:19-28`), docker group (`packages.yml:51-61`),
  libvirt group (`packages.yml:63-74`). Each new special case adds another
  task + gate + comment.
- Precedent for out-of-playbook logic: `.bin/validate-manifest.py`
  (stdlib-only validator invoked via `command`, `preflight.yml:56-65`).
- Convention-discovery precedent: per-source package lists are derived in
  `playbook.yml` vars (e.g. `dotfiles_pkgs_apt`), and `validate-manifest.py`
  cross-checks keys across manifests — the orphan-hook check follows the
  same pattern.
- User decisions (2026-09-09 brainstorming): both global and per-package
  scopes; convention-based discovery (no manifest schema change); Ansible
  invokes hooks (not the `install` wrapper); hook filename format
  `<key>.<pre|post>[.root].<sh|py>`; `global` reserved key for run-once
  hooks.
- Toolchain bootstrap (`toolchain.yml`: cargo/fnm/flatpak providers) stays
  hook-free — hooks may depend on the toolchain, so it is the provider
  layer, not a hook target.
- Parsing is unambiguous: package keys never contain dots (hyphens only),
  so `key = everything before .pre` / `.post`.

## Non-goals

- No change to the `packages.json` manifest schema.
- No change to how per-source installs work (apt, cargo, npm, script,
  deb, archive, git, flatpak tasks untouched).
- No hooks around toolchain bootstrap.
- No change to `install` wrapper behavior.

## Steps

Each step maps to exactly one commit, named `ANSIBLE(<NN>): <summary>`.

### 01 — hook dispatch tasks

- **Files:** `ansible/tasks/hooks-pre.yml` (CREATE),
  `ansible/tasks/hooks-post.yml` (CREATE), `ansible/playbook.yml` (EDIT),
  `ansible/hooks/README.md` (CREATE)
- **Changes:** playbook gains two import lines — `hooks-pre.yml` before
  `packages.yml`, `hooks-post.yml` after. Each hooks file holds generic
  loops (not per-package tasks): run `global.<phase>` once if present,
  then loop per-package hooks whose key is in the selected package set,
  split into user hooks and `.root` hooks (`become: true`). Discovery via
  `fileglob` over `ansible/hooks/`. Runner: `ansible.builtin.script`
  (honors shebang; `.sh` and `.py` both work). Hooks run with
  `changed_when: false, failed_when: rc != 0`. All hook tasks carry
  `tags: packages`. `README.md` documents the `<key>.<pre|post>[.root].<ext>`
  contract and the idempotency requirement (check state before mutating).
- **Test:** `ansible-playbook --syntax-check ansible/playbook.yml`; fixture play in plan 01-Step 6
- **Acceptance:**
  - [ ] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
  - [ ] `--check` run with empty `hooks/` dir is a no-op for hook tasks.
  - [ ] A fixture `global.pre.sh` (e.g. `exit 0`) runs once per play.

### 02 — migrate the three inline special cases to hooks

- **Files:** `ansible/hooks/ttf-mscorefonts-installer.pre.root.sh` (CREATE),
  `ansible/hooks/docker-ce.post.root.sh` (CREATE),
  `ansible/hooks/libvirt-daemon-system.post.root.sh` (CREATE),
  `ansible/tasks/packages.yml` (EDIT)
- **Changes:** behavior-verbatim moves — EULA preseed → pre-hook (apt
  needs the debconf preseed before the transaction); docker/libvirt group
  memberships → post-hooks (groups must exist before `usermod`). The three
  Ansible tasks (preseed, docker group, libvirt group) are deleted from
  `packages.yml`. Net-negative playbook lines.
- **Test:** `ansible-playbook --check --diff --skip-tags packages ansible/playbook.yml`; `shellcheck ansible/hooks/*.sh`
- **Acceptance:**
  - [ ] `ansible-playbook --check --diff --skip-tags packages
        ansible/playbook.yml` passes (validation tasks green).
  - [ ] Double `--tags packages` run: second pass reports no changes
    from hook tasks (idempotency).
  - [ ] `shellcheck` passes on the new `.sh` hooks.

### 03 — preflight validation for hooks

- **Files:** `.bin/validate-manifest.py` (EDIT) or new validator invoked
  from `ansible/tasks/preflight.yml` (CREATE + EDIT)
- **Changes:** fail fast on orphan hooks (hook key other than `global`
  with no matching `packages.json` entry) and on non-executable hook
  files. Follows the existing `preflight.yml:56-65` validation pattern.
- **Test:** `python3 .bin/validate-manifest.py` (plus orphan / non-executable fixtures in plan 03-Steps 2–3)
- **Acceptance:**
  - [ ] Orphan-hook fixture fails validation with the key named.
  - [ ] Non-executable hook fixture fails validation.
  - [ ] `python3 .bin/validate-manifest.py` (or successor) exits 0 on the
    migrated tree.

## Risks & Rollback

- **Hook ordering vs. apt transaction.** Pre-hooks must not assume
  packages exist; post-hooks must not assume services are enabled (service
  enablement stays out of scope, same as today).
- **Silent no-op on typo'd key.** A misspelled package key parses as an
  orphan — step 03 makes this a loud failure instead.
- **Rollback:** one commit per step; `git revert` of 02 restores the three
  inline tasks (hooks dir ignored when empty), of 01 removes dispatch.
