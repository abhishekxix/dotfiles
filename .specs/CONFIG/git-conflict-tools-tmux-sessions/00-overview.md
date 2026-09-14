# GH-27: Git Conflict Tools and Tmux Sessions

| Field | Value |
|---|---|
| Status | Approved |
| Component | CONFIG |
| Created | 2026-09-14 |
| GH issue | GH-27 (`CONFIG: git conflict tools and tmux sessions`) |
| Verification notes | None |

> GH-27 is part 2/8 of the PR #25 split. PR #25 was closed unmerged; its spec
> (`.specs/CONFIG/config-qol-updates/`, steps 03–04) no longer exists in the
> tree. This spec re-derives the GH-27 scope from the issue body plus the two
> original commit diffs (fetched via `gh api` from the closed PR: `67195d5`
> for gitconfig, `e382c5e` for tmux), verified against the current tree on
> 2026-09-14. It covers only `home/.gitconfig` and `.config/tmux/tmux.conf`;
> gitconfig history/alias and shell-init concerns belong to GH-26 and
> `config-refinements/04–05`.

## Goal

Make Git merge/diff conflict resolution safer and path-proof, and make tmux
session teardown keep clients attached with readable titles.

## Context & Research

Key facts, verified against the tree on 2026-09-14:

1. **Unquoted `$LOCAL/$REMOTE/$BASE/$MERGED`** (`home/.gitconfig:16,33`):
   difftool/mergetool `cmd` lines expand bare `$LOCAL` etc. Paths with spaces
   word-split before nvim sees them. Quoting (`\"$LOCAL\"`) is the fix.
2. **Per-file difftool prompt kept deliberately** (`home/.gitconfig:15-16`):
   the `vimdiff` difftool section has no `prompt = false`, so every
   `git difftool` confirms each file. User chose to keep the prompt (re-spec
   2026-09-14) — it stays as a safety gate.
3. **`conflictstyle = diff3`** (`home/.gitconfig:25`): plain `diff3` hides the
   common-ancestor hunk; `zdiff3` compacts shared lines for smaller, readable
   conflicts. Git 2.47.3 on this host supports `zdiff3`.
4. **No rerere, deliberately** (`home/.gitconfig` has no `[rerere]`): user
   chose to skip rerere (re-spec 2026-09-14) — repeated resolutions stay
   manual, no silent replays.
5. **No gone-branch alias, deliberately**: user chose to skip the
   `branches-gone` alias (re-spec 2026-09-14) — stale-branch cleanup stays
   out of scope.
6. **tmux session teardown detaches** (no `detach-on-destroy` in
   `.config/tmux/tmux.conf`): destroying the attached session kicks the
   client off the server. `detach-on-destroy off` moves the client to another
   session instead. tmux 3.5a supports all three new options
   (`detach-on-destroy`, `display-time`, `set-titles`/`set-titles-string`).
7. **Unreadable titles/messages** (`tmux.conf` has no `display-time`,
   `set-titles`): status messages flash at the 750ms default; terminal
   emulator titles never show session/command. Proposed: `display-time 4000`,
   `set-titles on` with `#{session_name}: #{pane_current_command}`.
8. **Catppuccin opts kept deliberately** (`tmux.conf:54,56,57`): user chose
   to keep all three (`@catppuccin_window_status`,
   `@catppuccin_window_default_text`, `@catppuccin_window_current_fill`)
   untouched (re-spec 2026-09-14) — no theme changes in this spec.

## Non-goals

- Do **not** touch shell startup, history, fzf/zoxide/direnv — GH-26 owns that.
- Do **not** touch `credential.helper`, fetch/prune, push/pull, or shell
  history/alias convergence — `config-refinements/05` territory.
- Do **not** touch tmux truecolor/clipboard/vi-copy/resize (already landed via
  `config-refinements/01`), or the remaining live Catppuccin opts.
- Do **not** add rerere or a gone-branch alias — user skipped both in re-spec.

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

### 01 — Quoted nvim diff/merge paths + zdiff3

- **Files:** `home/.gitconfig` (EDIT)
- **Changes:** quote `$LOCAL/$REMOTE/$BASE/$MERGED` in the vimdiff/nvim tool
  commands; switch `conflictstyle` to `zdiff3`. Difftool prompt stays
  (user choice); no rerere; no gone-branch alias.
- **Test:** `git config --file home/.gitconfig --list`; spaced-path diff/merge
  dry run. Manual only, no automated tests (per issue).
- **Acceptance:**
  - [ ] spaced paths open correctly in difftool/mergetool without word-split
  - [ ] `git difftool` still prompts per file (unchanged behavior)
  - [ ] conflicts render compact zdiff3 (manual, pending user confirm)

### 02 — tmux destroy-switch, message time, titles

- **Files:** `.config/tmux/tmux.conf` (EDIT)
- **Changes:** `detach-on-destroy off` so killing the attached session switches
  the client instead of detaching; `display-time 4000`; `set-titles on` with
  session + active-command title string. Catppuccin opts untouched (user choice).
- **Test:** `tmux -L <isolated-socket> -f <edited-conf> ...` — new session,
  destroy attached session, observe client switch + titles. Manual only, no
  automated tests (per issue).
- **Acceptance:**
  - [ ] destroying the attached session switches client, never detaches (manual, pending user confirm)
  - [ ] titles show session + command; messages stay readable (manual, pending user confirm)

## Risks & Rollback

- **Quoted tool paths**: if any wrapper passed pre-split args, quoting changes
  argv — rollback reverts step 01. Verified by spaced-path dry run first.
- **`zdiff3`**: older gits (<2.35) reject the value; host is 2.47.3, but remotes
  with old git ignore the user-level setting anyway. Rollback: `diff3`.
- **`detach-on-destroy off`**: a destroyed last-session now exits tmux instead
  of detaching — expected; reattach starts fresh. Rollback removes the line.

Each step is its own commit, so `git revert` or `git bisect` localizes any
regression.
