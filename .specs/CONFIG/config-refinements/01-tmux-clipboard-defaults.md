# 01 — tmux truecolor + clipboard + vi-copy + sane defaults

| Field | Value |
|---|---|
| Status | Planning |
| Step | 01 |
| Commit | `CONFIG(01): tmux truecolor, OSC-52 clipboard, vi-copy binds, sane defaults` |

## Files

- `.config/tmux/tmux.conf` (EDIT)

## Changes

1. `default-terminal` → `tmux-256color` (keep/extend the `Tc` override) so
   undercurl/italics survive. Verify `infocmp tmux-256color` exists in the
   installer context first — if missing, this hunk waits.
2. Enable OSC-52 passthrough (`set-clipboard on`) so yanks escape tmux,
   including over SSH.
3. Wire up vi copy-mode: `v` begins selection, `y` copies and exits
   copy-mode (mode-keys vi is set but these binds are missing, so vi mode is
   half-wired today).
4. Add `history-limit`, `renumber-windows`, `focus-events`; add prefix-`r`
   config reload and repeatable `H/J/K/L` resize binds.

Out of scope: resurrect/continuum (tpm plugin adds boot cost for a solo
laptop — Non-goals).

## Test

- `tmux kill-server; tmux new -d 'nvim --headless'` then `:checkhealth` —
  undercurl/italics ok.
- Yank in copy-mode with `y`, paste outside tmux (and over SSH if available).
- Close a middle window, confirm numbering closes the gap; hit prefix-`r`
  and the resize binds.

## Acceptance

- [ ] italics/undercurl render inside tmux
- [ ] `y` in copy-mode lands in the system clipboard
- [ ] windows renumber on close; reload + resize binds work
