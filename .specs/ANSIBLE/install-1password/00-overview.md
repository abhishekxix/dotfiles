# Install 1Password from upstream apt repo

| Field | Value |
|---|---|
| Status | Planning |
| Component | ANSIBLE |
| Created | 2026-09-13 |
| Verification notes | None |

## Goal

Install the 1Password desktop app from its upstream apt repository via the
existing manifest pipeline (`repos.json` + `packages.json`), including its
required debsig-verify policy.

## Context & Research

- Upstream install docs (downloads.1password.com/linux): apt key at
  `https://downloads.1password.com/linux/keys/1password.asc`, repo line
  `deb [arch=amd64 signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/amd64 stable main`,
  debsig policy `https://downloads.1password.com/linux/debian/debsig/1password.pol`
  installed under `/etc/debsig/policies/AC2D62742012EA22/` with dearmored key at
  `/usr/share/debsig/keyrings/AC2D62742012EA22/debsig.gpg`, then
  `apt update && apt install 1password`.
- Existing third-party repo pipeline (`ansible/tasks/repos.yml`): downloads
  `key_url` to `<keyring>.asc`, dearmors to `<keyring>` with `creates` guard,
  writes the repo line via `copy`, refreshes apt only on change.
- No existing `repos.json` entry needs debsig-verify, so the policy/keyring
  steps need new generic support driven from `repos.json`.
- The `debsig-verify` binary must be present for dpkg signature checks; it is
  not a dependency of the current pipeline.
- Repo line is `amd64`-only upstream (no ARM build of the 1Password app); the
  `@ARCH@` placeholder would write a broken `arch=arm64` line on ARM, so the
  line stays hardcoded to `amd64` and install is limited to x86_64 hosts.

## Non-goals

- No 1Password CLI (`op`) or browser-extension integration.
- No sign-in, vault, or account configuration (user does that in the app).
- No support for ARM hosts (upstream ships amd64 only).

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

- [ ] 01 — 1Password repo + package manifest entries (01-repo-package-entry.md)
- [ ] 02 — debsig-verify policy support in repos pipeline (02-debsig-policy.md)

## Risks & Rollback

- A bad repo line breaks every later apt invocation (repos.yml heals via
  `copy` overwrite; remove the `1password` entries and re-run to roll back).
- `creates`-guarded dearmor is stale-key-blind (same caveat as existing keys;
  key rotation is tracked follow-up, see repos.yml:85-87).
- Each step is its own commit, so `git revert` localizes any regression.
