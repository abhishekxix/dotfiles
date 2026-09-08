# Auto-migrate legacy one-line apt sources to deb822

| Field | Value |
|---|---|
| Status | Done |
| Component | ANSIBLE |
| Created | 2026-09-08 |

## Goal

On hosts whose only apt sources are the legacy one-line
`/etc/apt/sources.list`, have the playbook migrate them to the canonical
deb822 `/etc/apt/sources.list.d/debian.sources` automatically (with backup
and rollback), instead of failing fast — so a fresh/upgraded host converges
without a manual apt-sources detour.

## Context & Research

- Observed today on a fresh trixie host: the step-01 guard
  (`ansible/tasks/components.yml:19`, from
  `.specs/ANSIBLE/enable-nonfree-components/`) aborted the run with
  "/etc/apt/sources.list.d/debian.sources (deb822) not found". That
  fail-fast was a deliberate v1 decision (regex-fragile in-place rewriting
  was rejected); this spec revises it to *replace the file wholesale*
  rather than edit it — which sidesteps the fragility objection.
- A wholesale replacement only needs apt's one-line format for one thing:
  deciding whether the host uses default mirrors. That is a narrow,
  well-defined parse: `^\s*deb(?:-src)?(?:\s+\[[^\]]*\])?\s+(\S+)`
  (options bracket optional, first URI token) via
  `ansible.builtin.regex_findall` on the slurped file.
- `gather_facts: true` in `ansible/playbook.yml:4`, so
  `ansible_facts.distribution_release` is available — the generated suites
  derive from it (`<release>`, `<release>-updates`, `<release>-security`)
  instead of hardcoding `trixie`.
- Generated file carries all four components (`dotfiles_apt_components`)
  directly, so the existing `Normalize apt source components` task is a
  no-op afterwards and idempotency is preserved by the trigger itself
  (`debian.sources` absent → migrate; present → never re-enter).
- Cache interaction: `ansible/tasks/packages.yml:10` forces a real index
  refresh only when `dotfiles_components_result.changed`. On a migrated
  host normalization does *not* change, and the migration's own
  validation `apt-get update` (which runs before `tasks/repos.yml` adds
  third-party repos) would leave lists <1h old — the packages.yml refresh
  would then be skipped and third-party indexes never fetched on first
  run. `packages.yml` must therefore also force the refresh when the
  migration fired.
- Allowed migration URIs: `deb.debian.org` and `security.debian.org`
  (http/https). `cdrom:` URIs fail the gate naturally (the bracket is part
  of the URI token there, so the regex captures it whole).
- Legacy file is world-readable (`644 root:root`, verified on the
  maintainer host), so the slurp needs no become.

## Non-goals

- No in-place editing or deb822-izing of third-party `.list`/`.sources`
  files (docker, vscode, corretto, google-chrome) — unchanged.
- No support for hosts with custom mirrors: they keep the existing
  fail-fast message (extended to say why). Auto-clobbering a corporate or
  regional mirror is worse than failing.
- No preservation of `deb-src` or `cdrom:` entries (generated file is
  `Types: deb` only, matching Debian's shipped default).
- No pre-trixie claims (`non-free-firmware` assumption inherited from the
  parent spec).
- No change to task ordering (components → repos → packages); the
  migration's extra validation update is accepted as a one-time cost.

## Steps

- [x] 01 — `01-auto-migrate-deb822.md` — migrate legacy-only default-mirror
  sources to deb822 (backup + rescue rollback), extend the fail-fast guard
  for custom mirrors and no-sources hosts, force the packages.yml refresh
  on migration

## Risks & Rollback

- Generated sources invalid (bad codename fact, network): the block's
  rescue restores the legacy file and removes the generated one, so the
  host is never left worse than before; the timestamped `.bak-*` also
  outlives the run. Regression after commit: `git revert` of the single
  step-01 commit restores pure fail-fast behavior.
- Custom mirrors: protected by the URI gate — worst case is the previous
  behavior (fail fast with an actionable message).
