# 14 - Strengthen installer preflight/link safety

| Field | Value |
|---|---|
| Status | In progress |
| Step | 14 |
| Commit | `CONFIG(14): strengthen installer preflight and link safety` |

## Files

- `install` (EDIT)
- `ansible/tasks/preflight.yml` (EDIT)
- `ansible/tasks/link.yml` (EDIT)
- `ansible/tasks/packages.yml` (EDIT)
- `.bin/tests/test_install.py` (CREATE)
- `README.md` (EDIT)

## Changes

Reject root before wrapper-side collection changes; fail clearly when sudo is
required but unavailable; enforce Debian release and declared architecture
support before APT mutation; restore a backed-up destination if link creation
fails; apply conflict protection to script/archive binary links rather than
force-replacing arbitrary files; report post-run relogin/manual actions.

## Test

Automated: `python3 -m unittest discover -s .bin/tests -p 'test_install.py'` and
`ansible-playbook --syntax-check ansible/playbook.yml`. The unit test creates
temporary root, unsupported OS/architecture, conflict, and link-failure
fixtures; no fixture directory is committed.

## Acceptance

- [ ] Root, unsupported-OS, and unsupported-architecture fixtures fail before their mutation sentinel is touched.
- [ ] Each conflict/link-failure fixture restores its original destination bytes.
- [ ] Each binary-link conflict fixture fails or backs up according to the selected policy.
- [ ] Post-run output reports required relogins and manual actions once.

## Risks & Rollback

Rollback logic must not overwrite a new file created after backup. Fixture-test
every state transition before applying it to real home-directory entries.
