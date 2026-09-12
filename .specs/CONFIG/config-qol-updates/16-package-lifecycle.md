# 16 - Define package lifecycle/integrity

| Field | Value |
|---|---|
| Status | Approved |
| Step | 16 |
| Commit | `CONFIG(16): define package lifecycle and integrity` |

## Files

- `install` (EDIT)
- `.bin/doctor` (EDIT)
- `.bin/validate-manifest.py` (EDIT)
- `.bin/tests/test_install.py` (EDIT)
- `.bin/tests/test_validate_manifest.py` (EDIT)
- `ansible/tasks/install-script-one.yml` (EDIT)
- `ansible/tasks/install-git-one.yml` (EDIT)
- `ansible/tasks/install-archive-one.yml` (EDIT)
- `ansible/tasks/install-deb-one.yml` (EDIT)
- `ansible/tasks/packages.yml` (EDIT)
- `ansible/tasks/repos.yml` (EDIT)
- `ansible/vars/packages.json` (EDIT)
- `ansible/vars/packages.schema.json` (EDIT)
- `ansible/vars/repos.json` (EDIT)
- `ansible/vars/repos.schema.json` (EDIT)
- `README.md` (EDIT)

## Changes

Document lifecycle by source and add explicit non-mutating audit plus mutating
upgrade modes. A missing package is installed during the default fresh-install
path. On an existing install, floating Git/script sources update only when
upgrade mode is selected. Upgrade mode converges declared archive/Git versions
and floating sources; script tasks report changed only when their artifact
changes. Add finite retries/timeouts and a concurrent-run lock; verify
post-install artifacts.

Pinned deb/archive/script payloads require SHA-256 verification. Script
installers download to a temporary file before execution rather than piping
network content directly to a shell. A floating script without an upstream
verifiable payload must be an explicit manifest exception and produce a visible
integrity warning. It installs when absent; subsequent refreshes execute only in
upgrade mode. Repository key changes require expected-fingerprint verification
before replacing the dearmored keyring.

## Test

Automated: run `python3 -m unittest discover -s .bin/tests -p 'test_install.py' && python3
-m unittest discover -s .bin/tests -p 'test_validate_manifest.py'`. The suite
creates disposable package
fixtures for version N then N+1, default second-run idempotency, audit-only
drift, upgrade convergence, floating/pinned sources, integrity failure, key
rotation, transient retries, and concurrent invocation.

## Acceptance

- [ ] A default second run reports `changed=0` for lifecycle-managed fixtures.
- [ ] Audit reports drift without mutation and upgrade converges it.
- [ ] Floating Git/script sources update only in explicit upgrade mode.
- [ ] Static inspection of `install-script-one.yml` finds no direct network-to-shell pipe.
- [ ] Pinned payloads and repository keys are integrity-checked.
- [ ] In the two-process fixture, one installer acquires the lock and the other exits with the documented lock diagnostic.

## Risks & Rollback

Integrity metadata creates deliberate maintenance overhead. Fail closed for
pinned artifacts; keep floating exceptions visible and narrowly scoped rather
than silently weakening all sources.
