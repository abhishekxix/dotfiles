# 13 - Add non-mutating environment diagnostics

| Field | Value |
|---|---|
| Status | Approved |
| Step | 13 |
| Commit | `CONFIG(13): add environment health diagnostics` |

## Files

- `.bin/doctor` (CREATE)
- `.bin/tests/test_doctor.py` (CREATE)
- `README.md` (EDIT)

## Changes

Provide a read-only report for required commands, manifest-versus-installed
Neovim version, Treesitter CLI, formatter/LSP availability, shell plugins,
broken managed symlinks, terminal capabilities, and desktop-only dependencies.
It may run on non-Debian hosts to explain drift but must not install or alter
anything there.

## Test

Automated: `python3 -m unittest discover -s .bin/tests -p 'test_doctor.py'`.

The unit suite supplies controlled PATH, version-output, symlink, and profile
fixtures, including an installed Neovim version that intentionally differs
from the manifest. Manual: run `.bin/doctor` once on the Debian target and
review host, accepting a nonzero result when required gaps are reported.

## Acceptance

- [ ] Missing tools are grouped by owning config with actionable remediation.
- [ ] Required gaps return nonzero and optional/profile-inapplicable gaps do not.
- [ ] A controlled installed-versus-declared version mismatch is detected.
- [ ] Before/after snapshots of the temporary HOME and tracked worktree are identical in every doctor fixture.

## Risks & Rollback

The doctor must not become a second package manifest. Derive requirements from
existing manifests/configs where possible and keep platform exceptions explicit.
