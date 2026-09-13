# GH-26: Shell Startup, History, fzf/zoxide/direnv

| Field | Value |
|---|---|
| Status | In progress |
| Component | CONFIG |
| Created | 2026-09-13 |
| GH issue | GH-26 (`CONFIG: shell startup, history, fzf/zoxide/direnv`) |
| Verification notes | None |

> GH-26 is part 1/8 of the PR #25 split. PR #25 was closed unmerged; its spec
> (`.specs/CONFIG/config-qol-updates/`, steps 01–02) no longer exists in the
> tree. This spec re-derives the GH-26 scope from the issue body, verified
> against the current tree on 2026-09-13. It overlaps
> `config-refinements/04-shell-startup-managers.md` (compinit cache, single
> node manager, fzf-once sourcing — all already-satisfied and user-confirmed
> keep-as-is) and therefore does **not** re-do those hunks; it references them
> as prior art instead.

## Goal

Make interactive zsh/bash startup fast, guarded, and consistent: cached
completion, per-shell live-shared history (zsh sessions share with zsh,
bash with bash, never mixed), scoped fzf previews, and zoxide + direnv
available in both shells on both profiles — degrading silently when any tool
is missing.

## Context & Research

Key facts, verified against the tree on 2026-09-13:

1. **compinit already cached** (`.zshrc:31-32`): `compinit -C -d
   "${XDG_CACHE_HOME:-$HOME/.cache}/zsh/zcompdump-$ZSH_VERSION"`. Cache dir
   `~/.cache/zsh` exists. Nothing to do — prior art from
   `config-refinements/04`.
2. **Single node manager already settled**: fnm is the installed provider
   (`ansible/tasks/toolchain.yml:30-47`), eager-eval'd in both shells
   (`.zshrc:61-64`, `.bashrc:23-26`). User elected to keep eager eval
   (2026-09-13 step-04 decisions). No nvm line, no `NODE_ENV` export exist.
3. **fzf key bindings sourced once** (`.zshrc:47-54`): user file preferred,
   system examples as fallback, guarded by `command -v fzf`. But there is no
   **scoped preview** config — the only fzf env is a global
   `FZF_DEFAULT_OPTS` (`.zshrc:56`) applying a bat preview to *every* fzf
   use (Ctrl-T, Alt-C, Ctrl-R alike).
4. **zoxide + direnv entirely absent**: no package entries in
   `ansible/vars/packages.json` (only `fzf` at line 283 has one), no init
   lines in either rc file, neither binary on this host (`command -v zoxide
   direnv` → not found).
5. **Bash live sessions do not share history**: `.bashrc:14-18` sets a static
   history block (`histappend histverify`, size 100k) but has no
   `PROMPT_COMMAND` composition — a later tool init (direnv/zoxide/fnm hooks)
   that assigns `PROMPT_COMMAND=` would clobber history sync. zsh live-share
   is already done via `share/append/inc_append` (`.zshrc:7-9`); bash
   per-prompt sync (`history -a; history -c; history -r`) is the gap. zsh and
   bash histories must **never** mix — per-shell files stay separate.
6. **No `GPG_TTY` anywhere**: `grep -rn GPG_TTY home/` is empty. tmux
   reattach breaks `gpg --clearsign`/pinentry without it (needs re-export on
   each new shell, interactive-only).
7. **Starship unguarded** (`.zshrc:59`): bare `eval "$(starship init zsh)"`
   with no `command -v` guard — a missing binary breaks every new shell.
   fzf/fnm inits are guarded; starship is the outlier.
8. **No automated shell tests**: `.bin/tests/` does not exist (it was a
   PR #25 artifact, never merged). Spec test commands below use only
   `shellcheck`, `bash -n`, `zsh -n`, and timed interactive shells.

## Non-goals

- Do **not** re-do `config-refinements/04` hunks already settled keep-as-is
  (compinit flags, fnm eagerness, fzf one-or-other sourcing, `_bat_preview`
  helper, `EDITOR=vim`, `NODE_ENV` absence).
- Do **not** converge ls/cp/mv/rm aliases or touch gitconfig — that is
  `config-refinements/05` territory.
- Do **not** add new plugins, prompt segments, or restyle the prompt.
- Do **not** switch node managers (fnm owns node; user-confirmed).

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

### 01 — zoxide + direnv packages (workstation + server)

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** add `zoxide` and `direnv` apt entries in lexical order with
  `profiles: ["workstation", "server"]`, matching the `fzf` entry shape.
  Both shells gain directory navigation (`z`) and per-directory env
  (allow-listed via `direnv allow`) on servers as well as the workstation.
- **Test:** `python3 -c "import json; json.load(open('ansible/vars/packages.json'))"` plus lexical-order check against neighboring keys.
- **Acceptance:**
  - [x] `zoxide` and `direnv` entries parse and sit in sorted position
  - [x] both profiles include both packages

### 02 — Guarded tool init: starship, zoxide, direnv in both shells

- **Files:** `home/.zshrc` (EDIT), `home/.bashrc` (EDIT)
- **Changes:** guard the bare starship eval with `command -v starship`;
  add `zoxide init` + `direnv hook` evals to both shells, each guarded by
  `command -v`, appended after the existing blocks. Actual order: zsh is
  fzf → starship → fnm → zoxide → direnv; bash is fnm → fzf → starship →
  zoxide → direnv → bash-completion (fnm left in place; order is cosmetic —
  no tool reads another's init output). Bring bash to parity: guarded starship init
  (replaces static `PS1` when present), fzf key bindings mirroring zsh
  (`~/.fzf.bash` preferred, else system `key-bindings.bash` +
  `completion.bash`, guarded by `command -v fzf`), plus the shared
  `FZF_DEFAULT_OPTS` / scoped preview env. A missing binary leaves a usable
  shell.
- **Test:** `zsh -n home/.zshrc && bash -n home/.bashrc && shellcheck
  home/.bashrc`; `zsh -ic true` / `bash -ic true` with binaries shadowed
  from PATH — no errors, exit 0.
- **Acceptance:**
  - [x] shell starts clean with any one tool missing (verifiable)
  - [ ] `z` navigation and `direnv allow/deny` work in both shells (manual)
  - [ ] bash shows starship prompt and fzf key bindings work (manual)

### 03 — Scoped fzf previews (self-contained, easily reverted)

- **Files:** `home/.zshrc` (EDIT), `home/.bashrc` (EDIT)
- **Changes:** scope the bat preview to file-finding widgets only
  (`FZF_CTRL_T_OPTS` / `FZF_ALT_C_OPTS`) instead of the global
  `FZF_DEFAULT_OPTS`, so Ctrl-R history search stays preview-free. Kept as
  one self-contained hunk: reverting this step alone restores the current
  global-preview behavior with no effect on any other step.
- **Test:** `zsh -n` / `bash -n` / `shellcheck`; Ctrl-T/Alt-C show previews,
  Ctrl-R does not.
- **Acceptance:**
  - [ ] Ctrl-T/Alt-C show previews, Ctrl-R does not (manual)

### 04 — GPG_TTY interactive-only + bash live-shared history

- **Files:** `home/.zshrc` (EDIT), `home/.bashrc` (EDIT)
- **Changes:** export `GPG_TTY=$(tty)` only when interactive and stdin is a
  tty, so tmux reattach re-points pinentry without polluting non-interactive
  shells. zsh live-share is already-satisfied (`share/append/inc_append`,
  `.zshrc:7-9`) — no change. In bash, compose full per-prompt sync
  (`history -a; history -c; history -r`) into `PROMPT_COMMAND` append-style
  (`PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND; }history -a..."`) so
  later tool hooks cannot clobber it; history files stay per-shell
  (`~/.zsh_history`, `~/.bash_history`) and are never mixed.
- **Test:** `bash -c 'source home/.bashrc; echo GPG_TTY=$GPG_TTY'` prints
  empty (non-interactive guard holds); interactive shells export a tty path.
  Open two concurrent bash shells, run a command in one, Ctrl-R in the other.
- **Acceptance:**
  - [x] non-interactive shells leave `GPG_TTY` unset; tty shells export a pts path (verifiable)
  - [ ] `tmux reattach; gpg --clearsign` works without pinentry failure (manual)
  - [ ] two concurrent bash sessions share history (manual)

## Implementation notes

- Step 02 commit `d451d8d`: bash `_bat_preview` uses `printf` (zsh uses
  `print -r`); SC2155 avoided via declare/export split; SC2089/2090 carry
  per-line disables (single-quoted `--preview '...'` is intentional — fzf
  splits opts itself).
- Step 04 commit `2b863c3`: our `PROMPT_COMMAND` sync line sits *before* the
  starship block in `.bashrc`; starship init captures pre-existing
  `PROMPT_COMMAND` into `STARSHIP_PROMPT_COMMAND` and runs it inside
  `starship_precmd` after `$?` preservation — history sync composes correctly.

## Risks & Rollback

- **zoxide/direnv new to servers**: `cd` gains a hook, project envs evaluate
  only after explicit `direnv allow` per directory — no silent env changes.
  Rollback: revert step 01 + 02 commits.
- **Bash full reload per prompt** (`history -c; history -r`): user-accepted
  for true live-share; at 100k entries a prompt flicker is possible — if it
  annoys, follow-up is append-only (`history -a`). Rollback removes the
  `PROMPT_COMMAND` line. Histories stay per-shell, so no cross-format risk.
- **`PROMPT_COMMAND` compose**: append-style preserves existing hooks
  (direnv/fnm). Rollback restores the static block.
- **`GPG_TTY` tty check**: `tty -s` guard means cron/CI shells unaffected.
  Rollback removes the block.

Each step is its own commit, so `git revert` or `git bisect` localizes any
regression.
