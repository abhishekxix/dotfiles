# 02 — Alacritty env + window polish

| Field | Value |
|---|---|
| Status | Planning |
| Step | 02 |
| Commit | `CONFIG(02): alacritty TERM default, scrollback, absolute theme, bigger window` |

## Files

- `.config/alacritty/alacritty.toml` (EDIT)

## Changes

1. Drop the `TERM = "xterm-256color"` override (line 45) so it defaults to
   `alacritty`, matching tmux's `Tc` handling — but verify first: launch and
   confirm no breakage, and check SSH targets have the `alacritty` terminfo
   entry. If remote breakage appears, keep the override and drop that hunk.
2. Add `[scrolling]` history + `[selection]`/clipboard save (neither section
   exists today).
3. Delete the dangling empty `[terminal]` section (line 50).
4. Make the theme import absolute (`~/.config/alacritty/...`) so launch cwd
   never matters (today's relative `./themes/...` depends on cwd).
5. Bump the default window from 80×25 (lines 11–13) to something usable on a
   1440p/1080p setup.

## Test

- Launch alacritty from `/`, confirm the Catppuccin theme loads.
- `echo $TERM`; scrollback works; clipboard copy works.

## Acceptance

- [ ] correct theme regardless of cwd; no empty `[terminal]` section
- [ ] scrollback present; TERM sane locally and over SSH
