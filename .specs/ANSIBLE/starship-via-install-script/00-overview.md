# Starship via upstream install script

| Field | Value |
|---|---|
| Status | Done |
| Component | ANSIBLE |
| Created | 2026-09-09 |

## Goal

Install starship via its upstream install script (`https://starship.rs/install.sh`,
`script` source) at the script's default location instead of extracting a
pinned musl tarball into `~/.local/bin` (`archive` source). Track upstream
`latest` (user decision 2026-09-09) rather than the current `v1.22.1` pin.

## Context & Research

- Current entry is `archive` (`ansible/vars/packages.json:503-513`),
  extracting into `~/.local/bin`. User decision (2026-09-09): prefer the
  upstream script installer where one exists, let it install to its default
  location (no user-local install required), and take `latest`.
- Upstream script behavior (read 2026-09-09 from
  `https://starship.rs/install.sh`): defaults `BIN_DIR=/usr/local/bin`,
  self-escalates via `sudo -v` + `sudo tar` when the bin dir is not writable;
  flags `-b/--bin-dir`, `-v/--version` (defaults to `latest/download`),
  `-f/-y/--force/--yes` (skips the `[y/N]` prompt, which reads from
  `/dev/tty` and cannot succeed under Ansible).
- Two blockers in the current `script` pipeline
  (`ansible/tasks/packages.yml:100-113`):
  1. **Shell guard.** The task pipes the download into `bash -s` under
     `executable: /bin/bash`. Starship's `verify_shell_is_posix_or_exit`
     aborts when `BASH_VERSION` is set without `POSIXLY_CORRECT`
     ("Please use `sh` instead", exit 1). The pipe target — not the outer
     shell — must be overridable per entry (default stays `bash` so the
     `claude-code`/`opencode` installers are unaffected).
  2. **Absolute `creates`.** The script schema types `creates` as `homePath`
     (`^~/`; `ansible/vars/packages.schema.json:122`), but the default
     install lands at `/usr/local/bin/starship`. The schema must accept an
     absolute path for script `creates`. (The stdlib validator
     `.bin/validate-manifest.py` only checks presence of `url`/`creates`,
     not their shape, so no validator change is expected — to be confirmed
     while implementing.)
- **No migration needed.** The setup is still in dev — no provisioned
  host carries the archive-era `~/.local/bin/starship`, so no cleanup task
  is required. (If that changes, note `~/.local/bin` precedes
  `/usr/local/bin` on PATH, so a stale archive-era file would silently
  shadow the script install.)
- **Sudo.** The script task runs unprivileged (no `become`); the installer
  escalates itself. The `./install` wrapper defaults to `--ask-become-pass`,
  and the `apt` tasks earlier in the same run already escalate, so the sudo
  timestamp is fresh when the script runs. No `become` on the script task
  itself (that would run the whole pipeline as root and mis-resolve
  `~/.local/bin`, `~/.cargo/bin` in its `PATH`).
- **Version tracking.** No `-v` flag: each fresh host installs upstream
  `latest` at provision time. The `creates` guard (`/usr/local/bin/starship`
  exists → skip) means existing hosts do not auto-upgrade on re-runs;
  upgrading means deleting the binary and re-running — the same limitation
  the `archive` source already has.

## Non-goals

- No changes to the `claude-code`/`opencode` script entries (they keep the
  `bash` pipe target).
- No `link` handling for starship (the binary lands directly on PATH in
  `/usr/local/bin`).
- No version-aware upgrade logic (re-runs do not re-check `latest`).
- No generalization of absolute `creates` to `archive`/`git` sources.

## Steps

Each step maps to exactly one commit, named `ANSIBLE(<NN>): <summary>`.

### 01 — per-entry interpreter + absolute creates for script installs

- **Files:** `ansible/vars/packages.schema.json` (EDIT),
  `.bin/validate-manifest.py` (EDIT only if it needs the new field —
  expected no change), `ansible/tasks/packages.yml` (EDIT)
- **Changes:** script definition gains optional `interpreter` (absolute
  path, default `bash`); script `creates` accepts an absolute path in
  addition to `~/`-rooted paths. The "Run script installers" task pipes
  into `{{ item.value.interpreter | default('bash', true) }} -s --` instead
  of hardcoded `bash -s`. Outer `executable: /bin/bash` stays (keeps
  `pipefail`). Field order in new/edited entries stays alphabetized per
  `AGENTS.md`.
- **Acceptance:**
  - [x] `python3 .bin/validate-manifest.py` exits 0.
  - [x] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
  - [x] Existing script entries (`claude-code`, `opencode`) render
    unchanged — no `interpreter` key → `bash` pipe target as today
    (verified 2026-09-09 via a debug playbook rendering both commands:
    `... install.sh | bash -s --` vs `... install.sh | sh -s -- -y`).

### 02 — starship uses the install script

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** starship entry becomes (fields alphabetized, key stays in
  lexical position):
  `args: ["-y"]`, `creates: "/usr/local/bin/starship"`,
  `interpreter: "sh"`, `profiles: [workstation, server]`,
  `source: "script"`, `url: "https://starship.rs/install.sh"`.
- **Acceptance:**
  - [x] `python3 .bin/validate-manifest.py` exits 0; lexical key order
    intact.
  - [x] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
  - [ ] After a run: `which starship` → `/usr/local/bin/starship` (live
    run pending — no provisioned host has run this yet).
  - [ ] Re-run is idempotent (script task reports no change via the
    `creates` guard) — same, pending a live run.

## Risks & Rollback

- **Sudo timestamp cold.** If the script task ever runs without a prior
  `become` (e.g. `--skip-tags` slicing or a future reorder), the
  installer's `sudo -v` prompts on `/dev/tty` and fails under Ansible.
  Mitigation: keep the task after the apt transaction; failure mode is a
  loud installer error, not a partial install.
- **Pinned-version drift.** The `creates` guard means a future `-v` bump
  alone will not reinstall; document "delete the binary, re-run" at bump
  time (same as the archive source today).
- **Rollback:** one commit per step; `git revert` of 02 restores the
  archive entry (re-extracts `~/.local/bin/starship` on next run), of 01
  removes the `interpreter`/absolute-`creates` mechanism.
