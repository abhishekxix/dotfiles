# Manifest schema validation via pre-commit + CI

| Field | Value |
|---|---|
| Status | In progress |
| Component | INSTALLER |
| Created | 2026-09-07 |

## Goal

Validate `ansible/vars/packages.json` and `ansible/vars/package-deps.json`
against their existing JSON Schemas with a standard tool (`check-jsonschema`),
enforced by a git pre-commit hook and a GitHub Actions workflow so broken
manifests can never be committed or merged.

## Context & Research

- JSON Schemas already exist (`packages.schema.json`, `package-deps.schema.json`,
  draft-07) and the manifests carry `$schema` editor pointers; the playbook
  strips the `$schema` key before use.
- The preflight asserts (ansible/tasks/preflight.yml:50) stay as a runtime
  backstop: they cover the cross-file rule JSON Schema cannot express
  (`apt.repo` must exist in `repos.json`) and keep `install`/playbook safe on
  machines without hooks.
- `check-jsonschema` (https://github.com/python-jsonschema/check-jsonschema)
  validates a file against an explicit schema file; the `pre-commit` framework
  bootstraps hook environments automatically (no global pip installs) and the
  same config runs in CI, so hook and workflow cannot drift.
- No `.git/hooks` are configured today and no `.github/workflows/` exists.

## Non-goals

- Removing or reducing the playbook preflight asserts (runtime backstop +
  cross-file `repo` check stays).
- Migrating the schemas to a newer draft or restructuring the manifests.
- Editing `repos.json` validation (no schema exists for it; out of scope).

## Steps

### 01 — pre-commit config with check-jsonschema hooks

- **Files:** `.pre-commit-config.yaml` (CREATE), `README.md` (EDIT, if it
  documents setup) 
- **Changes:** Two `check-jsonschema` hooks pinned to a tag:
  `ansible/vars/packages.json --schemafile ansible/vars/packages.schema.json`
  and `ansible/vars/package-deps.json --schemafile
  ansible/vars/package-deps.schema.json`. Document `pre-commit install`.
- **Acceptance:**
  - [x] `pre-commit run --all-files` passes on the current manifests.
  - [x] Deliberately breaking an entry (e.g. `source: tgz`) makes
    `pre-commit run --all-files` fail with a useful error.
  - [x] `git commit` with a broken manifest is rejected after
    `pre-commit install`.

### 02 — GitHub Actions workflow

- **Files:** `.github/workflows/validate.yml` (CREATE)
- **Changes:** Workflow on `pull_request` (and pushes to `main`): checkout,
  `pip install pre-commit`, cache `~/.cache/pre-commit`, run
  `pre-commit run --all-files`.
- **Acceptance:**
  - [ ] Workflow runs green on a PR touching nothing, and red when the schema
    check is broken. (Requires a push; verify on first PR.)
  - [ ] (Manual, outside git) Branch protection on `main` set to require the
    `validate` check before merge.

## Risks & Rollback

- Contributors without `pre-commit` installed can bypass the hook with
  `git commit --no-verify`; the CI workflow is the real gate.
- Rollback is `git revert` of each step; the playbook behavior is untouched.
