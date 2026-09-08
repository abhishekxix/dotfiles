# Extract PATH setup into a shared POSIX file

| Field | Value |
|---|---|
| Status | In progress |
| Component | HOME |
| Created | 2026-09-08 |

## Goal

Move all `PATH` setup into one POSIX-sh file (`~/.path`) that is sourced from
`.zshenv`, `.profile`, and `.bashrc`, so every shell flavor gets the same PATH,
there are no duplicate entries even when the file is sourced more than once,
and zsh no longer depends on the X/session environment for `~/.local/bin`.

## Context & Research

Current state (live-verified):

- `home/.zshenv` sources `~/.cargo/env` (unconditional prepend of
  `~/.cargo/bin`) on every zsh invocation — nested `zsh` processes re-prepend
  it.
- `home/.profile` prepends `~/bin`, `~/.local/bin` (each only if the dir
  exists), sources `~/.cargo/env` again, and re-exports
  `QT_QPA_PLATFORMTHEME`.
- `home/.bashrc` has no PATH logic at all, and returns early for
  non-interactive shells.
- **zsh never reads `.profile`** (zsh order: zshenv → zprofile → zshrc →
  zlogin). There is no `~/.zprofile`. Debian's `/etc/zsh/zprofile` is empty and
  `/etc/zsh/zshenv` only sets a fallback PATH.
- Therefore `env -i HOME=$HOME zsh -lc 'echo $PATH'` today yields
  `~/.cargo/bin` only — `~/.local/bin` and `~/bin` are missing from a clean
  login zsh. Interactive zsh gets them only because the X/systemd session
  environment (which *does* read `.profile`) inherits them down. That is
  fragile.
- `~/.cargo/env` contains only the one `export PATH=...` line plus comments —
  inlining `~/.cargo/bin` is equivalent and lets the dedup guard apply.
- Linking needs no installer/ansible changes: `ansible/tasks/dotfiles.yml`
  auto-discovers every immediate child of `home/` and links it to `$HOME`
  (README.md:17 documents this contract).
- Existing specs reference `home/.profile:15` as the mechanism that puts
  `~/.local/bin` on PATH (`ANSIBLE/nvim-from-github-release`,
  `ANSIBLE/picom-from-upstream`, `ANSIBLE/expose-script-binaries`) — the
  mechanism stays, only its location moves.

Design:

- `~/.path` is plain POSIX sh (no bashisms/zshisms) so `.profile`, `.zshenv`,
  and `.bashrc` can all source it.
- Dedup via `case ":$PATH:" in *":$1:"*)` — sourcing the file any number of
  times (including from nested shells and from both `.profile` and `.bashrc`
  in the same bash login) is idempotent. No load-guard variable needed.
- Call order inside the file preserves today's bash-login PATH order
  (`cargo : .local/bin : bin : <system>`): add `~/bin` first, then
  `~/.local/bin`, then `~/.cargo/bin`.
- `.zshenv` keeps only non-PATH exports (`GTK2_RC_FILES`,
  `QT_QPA_PLATFORMTHEME`) and gains the `.path` source; `.profile` and
  `.bashrc` keep their roles and gain/replace the same source line.

## Non-goals

- No cleanup of stale `fnm_multishells/*` entries (separate concern).
- No MANPATH, CDPATH, or other env-var changes; `QT_QPA_PLATFORMTHEME` /
  `GTK2_RC_FILES` duplication across `.zshenv`/`.profile` stays as-is.
- No `~/.zprofile` shim sourcing `.profile` (`.zshenv` covers zsh for every
  invocation).
- No changes to `.zshrc`, `fpath`, fnm/nvm init, or any `ansible/` task.
- No new installer flags or manifest fields.

## Steps

Each step maps to exactly one commit, named `HOME(<NN>): <summary>`.

### 01 — create `~/.path` and link it

- **Files:** `home/.path` (CREATE)
- **Changes:** New POSIX file. Defines `dot_path_add()` (prepend only if dir
  exists and `case ":$PATH:"` shows it is absent), then adds, in order:
  `$HOME/bin`, `$HOME/.local/bin`, `$HOME/.cargo/bin`. A comment notes this
  intentionally replaces sourcing `~/.cargo/env` so dedup applies. Mode
  `0644` (sourced, not executed). Then run the dotfiles link task
  (`./install --tags dotfiles` or the equivalent playbook invocation) so
  `~/.path` is live — later steps test through the symlink.
- **Acceptance:**
  - [x] `shellcheck home/.path` clean and `sh -n home/.path` clean.
  - [x] `PATH= sh -c '. ~/.path; . ~/.path; echo $PATH'` prints each dir
        exactly once (double-source idempotent; also proves empty-PATH
        safety).
  - [x] `ls -l ~/.path` is a symlink to
        `/home/abhi/dotfiles/home/.path` with mode `0644` on the target.
  - [ ] `ansible-playbook --check --diff --skip-tags packages
        ansible/playbook.yml` reports no pending link changes.
        (Blocked here: sudo password required for the playbook's become
        task. The symlink was created manually with the exact
        `state=link` absolute form `tasks/link.yml` produces, so the
        check should report convergence — run `./install` or the
        playbook once to confirm.)

### 02 — source `~/.path` from `.zshenv`

- **Files:** `home/.zshenv` (EDIT)
- **Changes:** Replace the `~/.cargo/env` source with
  `. "$HOME/.path"`. Keep `GTK2_RC_FILES` / `QT_QPA_PLATFORMTHEME` exports.
- **Acceptance:**
  - [x] `env -i HOME="$HOME" zsh -lc 'echo $PATH'` now contains
        `~/.local/bin`, `~/bin`, and `~/.cargo/bin` (the fragility fix).
  - [x] `zsh -c 'echo $PATH' | tr ':' '\n' | sort | uniq -d` prints nothing
        when run from an interactive zsh (nested shells add nothing).
  - [x] `grep -c cargo/env home/.zshenv` is `0`.

### 03 — replace `.profile` PATH block with the source

- **Files:** `home/.profile` (EDIT)
- **Changes:** Delete the `~/bin` / `~/.local/bin` prepends and the
  `~/.cargo/env` source; add `. "$HOME/.path"` in their place. Keep the
  bash-sources-`.bashrc` block and the `QT_QPA_PLATFORMTHEME` export.
- **Acceptance:**
  - [ ] `env -i HOME="$HOME" bash -lc 'echo $PATH' | tr ':' '\n' | sort`
        is unchanged from before this spec (same set of dirs, same
        cargo-then-.local/bin-then-bin relative order).
  - [ ] No duplicates: `env -i HOME="$HOME" bash -lc 'echo $PATH' |
        tr ':' '\n' | sort | uniq -d` is empty (`.profile` sources both
        `.bashrc`→`.path` and `.path` directly).

### 04 — source `~/.path` from `.bashrc`, final verification

- **Files:** `home/.bashrc` (EDIT)
- **Changes:** Add `. "$HOME/.path"` **before** the interactive guard
  (`[[ $- != *i* ]] && return`) so non-interactive bash (`bash -c`, scripts)
  also finds user tools. Interactive-only config (nvm) stays behind the
  guard.
- **Acceptance:**
  - [ ] `bash -c 'echo $PATH'` (non-login, non-interactive) contains
        `~/.local/bin`, `~/bin`, `~/.cargo/bin`.
  - [ ] `env -i HOME="$HOME" bash -lc 'echo $PATH' | tr ':' '\n' | sort |
        uniq -d` still empty; shellcheck clean on all three edited files.
  - [ ] Fresh login zsh and bash both show the expected PATH with no
        duplicates; spec status flipped to Done.

## Risks & Rollback

- Dropping the `~/.cargo/env` source: if a future rustup adds more than a
  PATH export to that file, we would miss it. Mitigation: the `.path`
  comment documents the substitution; rustup still manages
  `~/.cargo/bin` content.
- `dot_path_add` enters the global function namespace — named with a
  `dot_` prefix to avoid collisions.
- Non-interactive bash now reads `.path`: it must stay silent (no output)
  or it would corrupt scripted output; acceptance in 01 covers silence by
  using the file in command substitution.
- Each step is one commit: `git revert <step>` restores any single file, and
  the file is inert until sourced, so reverting step 01 alone is safe even
  while other files still reference it (source target is absent → shells
  skip nothing today; the sources added in 02–04 are unguarded `.`, so
  bisect order is: revert 04, 03, 02, then 01).
