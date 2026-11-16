# Install Claude Desktop from Anthropic's apt repo

| Field | Value |
|---|---|
| Status | Approved |
| Component | ANSIBLE |
| Created | 2026-11-16 |
| Verification notes | None |

## Goal

Track the Claude Desktop app (`claude-desktop`) in the manifest pipeline,
installed from Anthropic's upstream apt repository, so a fresh workstation
gets it the same way this machine already does by hand.

## Context & Research

- Upstream docs (code.claude.com/docs/en/desktop-linux): key at
  `https://downloads.claude.ai/claude-desktop/key.asc`, repo line
  `deb [signed-by=…/claude-desktop-archive-keyring.asc] https://downloads.claude.ai/claude-desktop/apt/stable stable main`,
  then `apt install claude-desktop`. Packages are published for `amd64` and
  `arm64` only.
- Expected signing key fingerprint
  `31DD DE24 DDFA B679 F42D 7BD2 BAA9 29FF 1A7E CACE`
  ("Anthropic Claude Code Release Signing"); the key already on this host at
  `/usr/share/keyrings/claude-desktop-archive-keyring.asc` matches.
- This host was set up manually: `/etc/apt/sources.list.d/claude-desktop.list`
  exists and `claude-desktop` 5.11492.5 is installed from that repo.
- Existing pipeline (`ansible/tasks/repos.yml`) downloads `key_url` to
  `<keyring>.asc` and dearmors it to `<keyring>`; it owns
  `/etc/apt/sources.list.d/<repo-id>.list` via `copy`. Using repo id
  `claude-desktop` and keyring `/usr/share/keyrings/claude-desktop-archive-keyring.gpg`
  means the `.asc` download lands on the existing file and the manual `.list`
  is overwritten in place (same URL/suite, signed-by switches to the `.gpg`).
- The `@ARCH@` placeholder expands to the host's Debian arch, which is valid
  here because upstream ships both amd64 and arm64. The package entry carries
  an `arches: [amd64, arm64]` guard so other arches skip the repo and package
  (repos are selected only through selected packages).
- Claude Code CLI is already tracked as `claude-code` (`source: script`,
  native installer `https://claude.ai/install.sh`) — no change needed.

## Non-goals

- No change to the existing `claude-code` entry.
- No server-profile install (desktop GUI app).
- No sign-in, MCP, or app configuration.
- No live playbook run as part of this spec (check mode only).

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

- [ ] 01 — Claude Desktop repo + package manifest entries (01-repo-package-entry.md)

## Risks & Rollback

- A bad repo line breaks later apt invocations; repos.yml heals by overwriting
  the `.list` on the next run. Roll back by reverting the commit and
  re-running (the `.list` file then needs manual removal, as with any repo
  dropped from the manifest).
- `creates`-guarded dearmor is blind to key rotation (existing pipeline
  caveat, tracked follow-up in repos.yml).
- Single commit, so `git revert` fully undoes the manifest change.
