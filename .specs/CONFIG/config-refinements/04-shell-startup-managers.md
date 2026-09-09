# 04 — Shell startup: compinit cache, one node manager, fzf/bat hardening

| Field | Value |
|---|---|
| Status | Planning |
| Step | 04 |
| Commit | `CONFIG(04): cached compinit, lazy fnm, single node manager, guarded fzf/bat` |

## Files

- `home/.zshrc` (EDIT)
- `home/.bashrc` (EDIT)

## Changes

1. `compinit -C -d <dumpfile>` (`.zshrc:29-30`): skip the rehash check with a
   cached dump. Bare `compinit` costs ~100–300ms every shell; on a
   single-user laptop `-C` is standard practice.
2. Lazy-load fnm (`.zshrc:58` eagerly evals `fnm env` every shell): defer to
   first `node`/`fnm` use or first prompt instead of eager eval.
3. Drop the eager system-`nvm` source (`.bashrc:16`, 0.3–0.8s) — fnm owns
   node; keep bash functional without it. Grep for `init-nvm` users first.
   Two node managers at once is the worst of both.
4. Source fzf once: prefer `~/.fzf.zsh` *or* the system examples when the
   other is absent (`.zshrc:49-52` double-sources today), guarded by
   `command -v fzf`.
5. `batcat` → `bat` with fallback (`.zshrc:50` preview breaks off-Debian).
6. `EDITOR=nvim` (`.zshrc:13` says `vim`, git says `nvim` — converge on nvim).
7. Scope `NODE_ENV` out of the global env (`.zshrc:14` leaks it into every
   GUI app — set per-project instead).

## Test

- `time zsh -ic true` before/after; `bash -ic true`.
- Open a shell on a machine without fzf/bat/fnm — no errors, shell usable.
- `node`/`npm` still work in both shells via the single manager.

## Acceptance

- [ ] interactive shell start measurably faster; missing tools degrade silently
- [ ] `node`/`npm` work in both shells via the single manager
