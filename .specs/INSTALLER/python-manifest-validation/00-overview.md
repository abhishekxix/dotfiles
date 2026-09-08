# Python manifest validator (replace Jinja asserts + jsonschema hook)

| Field | Value |
|---|---|
| Status | Done |
| Component | INSTALLER |
| Created | 2026-09-07 |

## Goal

Move manifest validation out of hand-rolled Jinja `assert` pipelines into a
small stdlib-only Python script under `.bin/`, used by both the ansible
preflight and pre-commit, so violations produce precise per-package errors
and there is a single source of validation truth.

## Context & Research

- Today validation lives in two places with different depth:
  - `.pre-commit-config.yaml` — `check-jsonschema` against
    `ansible/vars/packages.schema.json` / `package-deps.schema.json`
    (structure only; also runs in CI via `.github/workflows/validate.yml` →
    `pre-commit run --all-files`).
  - `ansible/tasks/preflight.yml` — ~30 Jinja `selectattr/rejectattr`
    pipelines asserting semantics (per-source required fields, types,
    non-empty profiles, repo id cross-file, dep keys ⊆ packages).
- The Jinja version fails with one opaque line ("Invalid package manifest: …")
  and cannot point at the offending package/field.
- Constraints carried over:
  - Script must be **stdlib-only** (python3 is already a hard dependency).
  - Runtime fail-fast must survive `--check` (command task runs with
    `check_mode: false`) and print collected errors, exit non-zero.
  - The `dotfiles_deb_arch` UNKNOWN check stays in ansible — it validates a
    host *fact*, not the manifest.
  - `$schema` keys in the manifests are editor hints and are skipped by the
    validator (same as the playbook's `rejectattr('$schema')`).

## Non-goals

- No third-party deps (no `jsonschema` module); no venv.
- No change to manifest schema/semantics — a pure refactor of *where* and
  *how well* they are validated.
- Schema JSON files are kept for editor `$schema` hints but are no longer a
  enforcement point (pre-commit hook is replaced).

## Steps

Each step maps to exactly one commit, named `INSTALLER(<NN>): <summary>`.

### 01 — `.bin/validate-manifest.py`

- **Files:** `.bin/validate-manifest.py` (CREATE, executable)
- **Changes:**
  - CLI: `validate-manifest.py [--packages P] [--deps D] [--repos R]`
    (defaults resolved relative to the repo root via the script's realpath;
    no ansible-specific knowledge).
  - Validates exactly the rules the preflight asserts encode:
    packages.json (mapping, source ∈ set, profiles non-empty ⊆
    {workstation, server}, per-source required fields, `args`/`strip`/
    `build` types, `link` must not start with `~` or `/`, apt `repo` id must
    exist in repos.json) and package-deps.json (mapping, keys ⊆ packages,
    values are non-empty lists of non-empty strings).
  - Collects **all** violations and prints one precise line each, e.g.
    `packages.json: 'picom': source 'git' requires field 'creates'`;
    exit 1 if any, 0 otherwise. Exit 2 for unreadable/invalid JSON files.
- **Acceptance:**
  - [x] Current real manifests pass (exit 0, no output).
  - [x] A fixture with several seeded violations reports *each* violation
        separately (missing required field, bad source, unknown repo id,
        empty profiles, bad dep key, non-string dep).
  - [x] Invalid JSON / missing file exits 2 with a clear message.

### 02 — Playbook preflight calls the validator

- **Files:** `ansible/tasks/preflight.yml` (EDIT)
- **Changes:**
  - Replace the two manifest-validation `assert` blocks with one
    `ansible.builtin.command` task running
    `{{ dotfiles_repo_root }}/.bin/validate-manifest.py`
    (`changed_when: false`, `check_mode: false`, register + `failed_when` on
    rc != 0, stdout+stderr shown on failure so ansible surfaces the precise
    violations).
  - Keep the `dotfiles_deb_arch` UNKNOWN check as an assert (host fact).
- **Acceptance:**
  - [x] `./install --check --diff --skip-tags packages` and full
        `--check --diff` both pass with valid manifests (validator runs even
        in check mode).
  - [x] Temporarily corrupt a manifest copy → playbook fails fast at
        preflight with the script's precise error (verified via a scratch
        manifest + `-e` override or a dry edit reverted immediately).

### 03 — Pre-commit hook consolidation

- **Files:** `.pre-commit-config.yaml` (EDIT)
- **Changes:**
  - Replace the two `check-jsonschema` hooks with one local hook running
    `.bin/validate-manifest.py` (trigger on the three manifest files). CI
    keeps working unchanged because it runs pre-commit.
  - Keep `packages.schema.json` / `package-deps.schema.json` for editor
    `$schema` hints.
- **Acceptance:**
  - [x] `pre-commit run --all-files` passes on the valid manifests.
  - [x] Seeded-violation fixture fails the hook with the script's messages.

### 04 — E2E verification + spec close

- **Files:** `.specs/INSTALLER/python-manifest-validation/00-overview.md` (EDIT)
- **Changes:** Full run, close spec.
- **Acceptance:**
  - [x] `./install --check --diff --skip-tags packages` clean
        (`changed=0`, exit 0).
  - [x] README/docs checked for stale references to the jsonschema gate
        (update if any).
  - [x] Spec status Done, boxes ticked.

## Risks & Rollback

- **Behavior drift** between Jinja asserts and the script (a rule lost or
  tightened silently). Mitigation: the script implements the rule list
  1:1 and step-01 acceptance seeds a fixture for every rule. Rollback:
  `git revert` per step; preflight asserts return verbatim.
- **check-mode regressions**: command tasks are skipped in check mode by
  default — `check_mode: false` is load-bearing; acceptance covers
  `--check` explicitly.
