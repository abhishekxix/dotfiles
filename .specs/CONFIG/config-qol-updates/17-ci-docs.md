# 17 - Expand CI and operator documentation

| Field | Value |
|---|---|
| Status | Approved |
| Step | 17 |
| Commit | `CONFIG(17): expand CI and operator documentation` |

## Files

- `.github/workflows/validate.yml` (EDIT)
- `.pre-commit-config.yaml` (EDIT)
- `.bin/tests/test_doctor.py` (EDIT)
- `.bin/tests/test_install.py` (EDIT)
- `.bin/tests/test_nvim_startup.py` (EDIT)
- `.bin/tests/test_shell_startup.py` (EDIT)
- `.bin/tests/test_validate_manifest.py` (EDIT)
- `.bin/tests/run-debian-integration` (CREATE)
- `README.md` (EDIT)

## Changes

Pin CI actions and Python/pre-commit tooling; grant read-only permissions; add
timeouts and concurrency cancellation; run ShellCheck and Ansible syntax on a
Debian target; run fast unit/fixture tests on every PR. Add a locally runnable
disposable Debian harness used by a scheduled CI job for both profiles and
second-run idempotency. Correct documentation about excluded config files,
privileged dotfile tasks, supported pre-commit installation, libvirt relogin,
doctor/audit/upgrade usage, and package lifecycle.

Historical frozen spec statuses are not edited here; reconciliation remains a
separately approved follow-up.

## Test

Automated network-dependent integration: `pre-commit run --all-files && python3 -m unittest discover -s
.bin/tests -p 'test_*.py' && ansible-playbook --syntax-check
ansible/playbook.yml && .bin/tests/run-debian-integration --profiles
workstation,server --runs 2`.

Manual review: compare the commands in `.github/workflows/validate.yml` with
the command sequence above and record the reviewed workflow lines.

## Acceptance

- [ ] CI runs the exact pre-commit, unittest-discovery, Ansible-syntax, and Debian-harness command sequence from Test.
- [ ] Debian-specific behavior is tested on Debian rather than inferred from Ubuntu.
- [ ] Both profiles complete in the local disposable harness.
- [ ] The second default run reports `changed=0` or only an exact documented allowlist.
- [ ] README describes current behavior and recovery steps accurately.

## Risks & Rollback

Full integration is slower than PR linting, so keep it scheduled while the
same harness remains locally runnable for implementation verification. Pinning
requires deliberate dependency-update maintenance.
