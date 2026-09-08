# Simplify toolchain bootstrap idempotency

| Field | Value |
|---|---|
| Status | In progress |
| Component | ANSIBLE |
| Created | 2026-09-08 |

## Goal

Drop the exist-probes in `ansible/tasks/toolchain.yml` and rely on each
installer's native idempotency (shell `creates:` markers, apt `state:
present`), and install `build-essential` first so the linker precedes every
toolchain step.

## Context & Research

- The probes were kept deliberately by `always-install-toolchains` step 02
  ("Idempotency guards stay: rc probes, stat checks, creates markers") and
  the AI-30 fnm PATH probe. User decision (2026-09-08): drop them — "the
  installations handle the idempotency".
- Rustup task: `creates: {{ dotfiles_home }}/.cargo/bin/cargo` already makes
  it skip when rustup is present. The cargo rc probe's only extra effect is
  skipping rustup when cargo exists on PATH from apt. After removal, rustup
  always ensures `~/.cargo/bin/cargo` — consistent with rustup being the
  declared cargo provider.
- "Check for fnm" (stat `~/.cargo/bin/fnm`) has identical semantics to the
  install task's `creates: ~/.cargo/bin/fnm` — fully redundant.
- "Check PATH for fnm" (AI-30): only effect is skipping `cargo install fnm`
  when a foreign (apt/manual) fnm is on PATH. After removal, such hosts
  compile a cargo copy into `~/.cargo/bin` (one-time cost); the fnm task's
  PATH already prefers `~/.cargo/bin`, so behavior converges on it. This
  reverses AI-30's intent by user decision.
- Flatpak probe: apt `state: present` is idempotent (ok when present,
  installs when missing) — the probe only converts "ok" into "skipped".
  The build-essential task in the same file already follows this no-probe
  pattern (`install-toolchain-compiler`: "No probe, no `when`").
- Registered vars `dotfiles_{cargo,fnm,fnm_path,flatpak}_check` are
  referenced nowhere outside `toolchain.yml` (grep-verified).
- Ordering: rustup is a prebuilt-binary download needing no `cc`; the first
  compiling task is "Install fnm", which build-essential already precedes —
  so today's order is correct. But installing build-essential first
  guarantees the linker for every step below and reads as "compiler
  toolchain first"; it also warms the apt cache so the flatpak task's
  `update_cache`/`cache_valid_time` no-ops. User decision (2026-09-08):
  build-essential should be the first toolchain step.

## Non-goals

- No changes to `packages.yml` / `package-deps.json`.
- No deletion of stale fnm binaries (non-goal of `always-install-toolchains`
  stands).
- No preflight linker assert (still the open follow-up from
  `install-toolchain-compiler`).
- No version pins on cargo crates.
- No behavior change on this host: every task keeps skipping or reporting ok
  via its `creates` marker / apt idempotence.

## Steps

Each step maps to exactly one commit, named `ANSIBLE(<NN>): <summary>`.

### 01 — drop the exist-probes, rely on installer idempotency

- **Files:** `ansible/tasks/toolchain.yml` (EDIT)
- **Changes:** delete "Check for cargo", "Check for fnm", "Check PATH for
  fnm", "Check for flatpak" and the three `when:` guards on "Install rustup",
  "Install fnm", "Install flatpak CLI". Delete the AI-30 comment (its
  rationale is gone). Keep the header comment and all `creates:` markers.
- **Acceptance:**
  - [x] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
  - [x] `--check --tags packages` run: no "Check ..." tasks; rustup/fnm/Node
    LTS skip via their `creates` markers; build-essential and flatpak report
    ok (`changed=0`, apt idempotence).
  - [x] `rg dotfiles_(cargo|fnm|fnm_path|flatpak)_check` finds nothing under
    `ansible/`.

  Verification note (2026-09-08): syntax-check and the rg sweep pass. The
  full `--check --tags packages` run cannot complete in the agent session —
  `components.yml`'s become task needs an interactive sudo password
  (pre-existing, unrelated). A targeted wrapper importing only
  `tasks/toolchain.yml` verified the creates-skip behavior: rustup, fnm, and
  Node LTS each report "Did not run command since '…' exists",
  `changed=0`. The apt tasks (build-essential, flatpak) need a real
  sudo-capable run — pending.

### 02 — build-essential first in the toolchain bootstrap

- **Files:** `ansible/tasks/toolchain.yml` (EDIT)
- **Changes:** move "Install build tools (cargo linker)" (with its comment)
  above "Install rustup (cargo provider)"; trim the comment's final sentence
  ("No rc probe ... matching the other toolchains' always-install rule") so
  it stays accurate after the probes are gone.
- **Acceptance:**
  - [x] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
  - [x] `--check --tags packages` run: build-essential is the first toolchain
    task and reports ok; section ends `changed=0`.
  - [x] `ansible-playbook --check --diff --skip-tags packages` preview shows
    the file change only (no live-path effects).

  Verification note (2026-09-08): syntax-check passes and file order is
  build-essential → rustup → fnm → Node LTS → flatpak. The sudo-dependent
  items above are covered by the same pending real run as step 01.

## Risks & Rollback

- **Fresh host with apt cargo:** rustup now also installs
  (`~/.cargo/bin/cargo` shadows `/usr/bin/cargo` via the tasks' PATH envs).
  Accepted — rustup is the declared cargo provider.
- **Host with a foreign fnm:** cargo compiles a duplicate into
  `~/.cargo/bin` (one-time cost); PATH order makes the cargo copy win.
  Accepted — reverses AI-30's intent by user decision.
- **Rollback:** one commit per step; `git revert` of 02 restores the
  original order, of 01 restores the probes.
