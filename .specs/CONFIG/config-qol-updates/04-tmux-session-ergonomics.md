# 04 - Refine tmux session ergonomics

| Field | Value |
|---|---|
| Status | Planning |
| Step | 04 |
| Commit | `CONFIG(04): refine tmux session ergonomics` |

## Files

- `.config/tmux/tmux.conf` (EDIT)

## Changes

When the current session is destroyed, move its client to another available
session; keep messages visible long enough to read; expose the active command
in terminal titles; remove Catppuccin options that are no-ops in the vendored
version: `@catppuccin_window_status`, `@catppuccin_window_default_text`, and
`@catppuccin_window_current_fill`. Preserve one independent tmux session per
Alacritty launch, current prefix/copy behavior, and the vendored plugin revision.

## Test

Automated isolation: `tmux -L dotfiles-qol -f .config/tmux/tmux.conf
new-session -d -s one && tmux -L dotfiles-qol new-session -d -s two && tmux -L
dotfiles-qol show-options -g && tmux -L dotfiles-qol kill-server`.

Manual: repeat on the isolated `dotfiles-qol` socket with an attached client,
destroy one session, and confirm the client switches and Alacritty titles track
the active command. Never test against the default/live tmux socket.

## Acceptance

- [ ] Destroying one session switches to another instead of dropping the client.
- [ ] Status messages and terminal titles are readable and accurate.
- [ ] The three named obsolete Catppuccin options are absent from `tmux.conf`.

## Risks & Rollback

Application-controlled titles can be noisy. Remove only title propagation if
that proves distracting; keep separate-session behavior unchanged.
