# Split ansible playbook into section task files

| Field | Value |
|---|---|
| Status | Planning |
| Component | ANSIBLE |
| Created | 2026-09-07 |

## Goal

Improve readability of `ansible/playbook.yml` (640 lines) by extracting its
task sections into per-topic files under `ansible/tasks/`, keeping
`playbook.yml` as a thin entrypoint that carries the play vars and imports
the sections in order. No behavior change.

## Context & Research

- The playbook already follows this pattern partially: `tasks/link.yml` is
  used via `include_tasks` for dotfile linking.
- Registers (`dotfiles_key_download`, `dotfiles_git_marker`, …) are host
  facts scoped to the play, so tasks that consume a `register` from another
  section keep working when moved to separate files **as long as the
  consuming task is not skipped** — with dynamic includes a skipped include
  skips the whole file, so section files must be imported statically.
- `import_tasks` is static: tags defined on tasks inside the imported file
  (or inherited from the `import_tasks` line) behave exactly like the
  current inline tasks, including `--skip-tags packages` behavior and
  `--list-tags`/`--list-tasks` output.
- Task ordering and `when` gating on cross-section registers (e.g. "Update
  APT metadata after adding third-party repos" reads registers set in the
  repos section) must be preserved exactly.

## Non-goals

- No renaming of vars, tags, or tasks.
- No change to manifests (`vars/*.json`), `tasks/link.yml`, or installer.
- No new features, tags, or conditionals.
- Not converting the existing `include_tasks: tasks/link.yml` loops to
  `import_tasks` (works today; out of scope).

## Steps

Each step maps to exactly one commit, named `ANSIBLE(<NN>): <summary>`.
After each step, behavior is verified with:

```
ansible-playbook --check --diff --skip-tags packages ansible/playbook.yml
```

### 01 — Extract preflight + manifest validation

- **Files:**
  - `ansible/tasks/preflight.yml` (CREATE)
  - `ansible/playbook.yml` (EDIT)
- **Changes:** Move the "Preflight guards", "Manifest validation", and
  "Build-deps manifest validation" tasks (profile/root/version asserts and
  both manifest schema validates) into `preflight.yml`; replace with
  `import_tasks` at the top of `tasks:`. Keep all tags and comments.
- **Acceptance:**
  - [ ] `--check --diff --skip-tags packages` still runs the preflight
    asserts and completes unchanged (no failed asserts).
  - [ ] `ansible-playbook --list-tasks ansible/playbook.yml` shows the same
    task names in the same order.

### 02 — Extract third-party apt repo setup

- **Files:**
  - `ansible/tasks/repos.yml` (CREATE)
  - `ansible/playbook.yml` (EDIT)
- **Changes:** Move the keyring-prereqs, key download/dearmor/permissions,
  `apt_repository`, and conditional cache-update tasks into `repos.yml`.
- **Acceptance:**
  - [ ] `--check --diff` run shows repos tasks behave identically (keyring
    files found, no repo churn).
  - [ ] Cross-section register (`dotfiles_repo_add` used by the conditional
    apt update) still resolves — run completes with no undefined-variable
    errors.

### 03 — Extract toolchain bootstrap

- **Files:**
  - `ansible/tasks/toolchain.yml` (CREATE)
  - `ansible/playbook.yml` (EDIT)
- **Changes:** Move cargo/rustup, fnm, and pipx-apt bootstrap tasks into
  `toolchain.yml`.
- **Acceptance:**
  - [ ] `--check` run: bootstrap checks report as before (skipped when the
    matching source has no selected packages).

### 04 — Extract per-source package installs

- **Files:**
  - `ansible/tasks/packages.yml` (CREATE)
  - `ansible/playbook.yml` (EDIT)
- **Changes:** Move apt install, build-deps, docker group, pipx ensurepath,
  cargo/npm/pipx/script/deb/archive/git install tasks into `packages.yml`.
- **Acceptance:**
  - [ ] Full `--check --diff` run (no tag skips) reports the same task
    outcomes as before the refactor on the same host.
  - [ ] `ansible-playbook --skip-tags packages ...` skips everything inside
    `packages.yml` (tag inheritance verified).

### 05 — Extract dotfile linking

- **Files:**
  - `ansible/tasks/dotfiles.yml` (CREATE)
  - `ansible/playbook.yml` (EDIT)
- **Changes:** Move the `.config` dir creation, home/config discovery, and
  the two `tasks/link.yml` loops into `dotfiles.yml`.
- **Acceptance:**
  - [ ] `--check --diff --skip-tags packages`: only preflight + dotfiles
    tasks run; symlinks converge (no change) on an already-linked host.
  - [ ] `playbook.yml` is now ~vars + 5 import lines; all comment context
    preserved in the moved sections.

## Risks & Rollback

- **Risk:** tag behavior differs if `include_tasks` is used instead of
  `import_tasks` (skipped includes skip entire files, breaking
  `--skip-tags packages` semantics partially and cross-section registers).
  Mitigation: use `import_tasks` exclusively for section files.
- **Risk:** task-name collisions break `--start-at-task`. Mitigation: names
  are copied verbatim; `--list-tasks` compared before/after.
- **Rollback:** one commit per section, so `git revert <step-commit>`
  restores any section without touching the others.
