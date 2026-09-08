# Port `install` wrapper to Python 3

| Field | Value |
|---|---|
| Status | Done |
| Component | INSTALLER |
| Created | 2026-09-07 |

## Goal

Replace the bash `install` wrapper with a Python 3 script of identical CLI
behavior. Python 3 is already a hard dependency (the collection floor check
pipes `ansible-galaxy` JSON through `python3`), so this removes the last
reason to keep two languages in the bootstrap path and makes the version
comparison / JSON handling native instead of shelled out.

## Context & Research

- Current wrapper (`install`, 205 lines, bash `set -Eeuo pipefail`):
  1. Pre-scan args to detect become-password options (`-K`, `--ask-become-pass`,
     `--become-password-file`, incl. `=`-joined forms) and `-e`/`--extra-vars`
     values mentioning `dotfiles_profile`.
  2. Parse `--profile NAME` / `--profile=NAME`, `-h/--help`; everything else is
     passthrough for `ansible-playbook`.
  3. Validate profile is `workstation|server`.
  4. If `ansible-playbook` missing: apt-install ansible (Debian `ID=debian`
     only, via `/etc/os-release`; sudo if available).
  5. Collection check: `ansible-galaxy collection list community.general
     --format json` → max version across paths (via python3) → compare against
     floor `10.7.0` via `sort -V -c`; install (`-r ansible/requirements.yml`)
     if missing, `--upgrade` if below floor.
  6. `cd` repo root, append `--ask-become-pass` unless user passed one, append
     `-e dotfiles_profile=<p>` unless user passed their own via `-e`, `exec
     ansible-playbook <become> ansible/playbook.yml <profile> <passthrough>`.
- Design decisions for the port:
  - **Single file**, keep the `install` entry point with `#!/usr/bin/env
    python3` shebang — no new paths, `.gitignore` whitelist already covers it.
  - **Hand-rolled argv parsing** (iterate `sys.argv[1:]`), not `argparse`:
    argparse would mangle/reject unknown passthrough options that must be
    forwarded verbatim to `ansible-playbook`.
  - **Version compare**: stdlib-only; split on `.` and compare numerically
    component-wise (drop the `sort -V -c` trick; `packaging` may not be
    installed at bootstrap time).
  - **Exec, not subprocess**: keep the final `os.execvp` so the process is
    replaced exactly as the bash wrapper did (signals/exit codes pass through
    unchanged).
  - Behavior parity is the contract: same flags, same messages, same exit
    semantics. The JSON/`sort -V` dance disappears — one Python process now
    does parsing *and* comparison.
- `README.md` documents the wrapper behavior (auto-install, backup dir) —
  wording changes only if user-visible behavior changes (it should not, beyond
  nothing observable).

## Non-goals

- Do **not** add new flags, profiles, or distro support (Ubuntu/Arch/Fedora
  remain deferred per `debian-fresh-setup`).
- Do **not** move any ansible/playbook logic into Python — the script stays a
  thin bootstrap + exec wrapper.
- Do **not** add Python packaging, venv, or third-party deps (stdlib only).
- Do **not** change backup/linking behavior or the playbook.

## Steps

Each step maps to exactly one commit, named `INSTALLER(<NN>): <summary>`.

### 01 — Rewrite `install` as a Python 3 wrapper (full port)

Merged from the original 01+02: a parse-only intermediate commit would leave
the tree without a working bootstrap between commits (bad for bisect).

- **Files:** `install` (EDIT — full rewrite, keeps executable bit)
- **Changes:** Replace bash with Python 3:
  - `usage()` → identical help text.
  - Argv pre-scan replicating the bash loop: become-pass flags (incl. `-K*`
    prefix match and `=`-joined forms) and `-e`/`--extra-vars` value capture
    (split `-e VALUE` immediate-next-value rule, joined `-eVALUE`,
    `--extra-vars=VALUE`).
  - Main parse loop: `--profile`/`--profile=`, `-h/--help`, everything else
    appended to passthrough list. Profile validation with same error message
    and exit 1.
  - `install_ansible()`: read `/etc/os-release` (stdlib parse), require
    `ID=debian` else same error/exit; `sudo apt-get update && sudo apt-get
    install --yes ansible`, plain fallback when `sudo` absent. Only when
    `ansible-playbook` is not on PATH.
  - Collection check: `ansible-galaxy collection list community.general
    --format json`, parse JSON in-process, take the highest version across all
    paths; numeric per-component compare against floor `10.7.0` (no
    `sort -V` shell trick). Missing → `ansible-galaxy collection install -r
    ansible/requirements.yml`; below floor → `--upgrade`. Errors tolerated →
    treat as absent.
  - Final `os.execvp("ansible-playbook", ...)` after `os.chdir(repo_root)`.
- **Acceptance:**
  - [x] `./install --help` output identical to the bash version (diffed).
  - [x] `./install --profile bogus` prints the same error and exits 1.
  - [x] Fake `ansible-playbook` on PATH prints the exact invocation; parity
        with the bash wrapper's built command (become/profile injection,
        passthrough order).
  - [x] `-e dotfiles_profile=server ./install` suppresses the injected
        `-e dotfiles_profile=workstation`.
  - [x] `./install -K` / `./install --ask-become-pass` do not add the wrapper's
        `--ask-become-pass`.
  - [x] Version compare sanity: `10.7.0 >= 10.7.0`, `10.6.9 < 10.7.0`,
        `10.10.0 > 10.7.0` (numeric, not string, compare).
  - [x] Unsupported distro path: fake `ID=fedora` os-release → same error
        message, exit 1.

### 02 — Docs + end-to-end verification

- **Files:** `README.md` (EDIT if any wrapper wording needs it),
  `.shellcheckrc`/pre-commit config only if shellcheck exclusions referenced
  `install` (DELETE/EDIT as needed)
- **Changes:** Update any README sentence that implies bash (e.g. "wrapper is
  bash"), confirm nothing else references shellcheck-on-install.
- **Acceptance:**
  - [x] `./install --check --diff --skip-tags packages` runs clean end to end
        and output matches pre-port behavior (no unintended diffs).
  - [x] `grep -rn 'install' .gitignore` still whitelists `/install` (no change
        needed, just confirm).
  - [x] README has no stale "bash wrapper" wording.

## Risks & Rollback

- **Argv parsing regressions** are the top risk: exotic passthrough combos
  (`--limit foo -e @file.yml`, repeated `-e`) must flow to ansible-playbook
  unchanged. Mitigation: hand-rolled parser mirrors the bash loop 1:1, plus
  step-01 acceptance checks. Rollback: `git revert` the step.
- **Version-compare edge cases**: non-numeric or pre-release suffixes
  (e.g. `10.7.0b1`) — current galaxy output for community.general is plain
  dotted digits, but mitigate by falling back to string compare on unexpected
  shapes (treat as below-floor → upgrade, the safe direction).
- **sudo-less fresh install**: unchanged risk from bash version; same code
  path (sudo presence check) so parity is preserved.

Each step is its own commit, so `git revert` or `git bisect` localizes any
regression. The bash version remains one `git revert` away at all times.
