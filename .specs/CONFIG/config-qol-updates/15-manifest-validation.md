# 15 - Make manifest validation strict

| Field | Value |
|---|---|
| Status | In progress |
| Step | 15 |
| Commit | `CONFIG(15): make manifest validation strict` |

## Files

- `.bin/validate-manifest.py` (EDIT)
- `.bin/tests/test_validate_manifest.py` (CREATE)
- `ansible/vars/packages.schema.json` (EDIT)
- `ansible/vars/package-deps.schema.json` (EDIT)
- `ansible/vars/repos.schema.json` (CREATE)
- `ansible/vars/flatpak-remotes.schema.json` (CREATE)
- `ansible/vars/repos.json` (EDIT)
- `ansible/vars/flatpak-remotes.json` (EDIT)
- `.pre-commit-config.yaml` (EDIT)

## Changes

Reject unknown/source-incompatible fields, wrong field types, empty required
strings/lists, invalid URLs/checksums, path traversal, unsupported script
interpreters, duplicate link destinations, and empty dependency lists.
Semantically validate repository key URLs/keyring paths/repository lines and
Flatpak remotes. Malformed input must produce collected diagnostics rather than
tracebacks. Run the gate when validator or hook files change, not only when
manifest JSON changes.

## Test

Automated: run `.bin/validate-manifest.py` and
`python3 -m unittest discover -s .bin/tests -p
'test_validate_manifest.py'`. The unit test
generates temporary malformed manifests covering every validation family and
top-level/value type; no fixture directory is committed.

## Acceptance

- [ ] Valid manifests pass and every malformed fixture fails precisely.
- [ ] Runtime validator behavior matches retained schema guarantees.
- [ ] Repository metadata fails before APT source mutation.
- [ ] Validator/hook changes trigger the local gate.

## Risks & Rollback

Do not reject fields already consumed by Ansible. Build allowed-field sets from
the complete source contract and prove the current manifest remains valid.
