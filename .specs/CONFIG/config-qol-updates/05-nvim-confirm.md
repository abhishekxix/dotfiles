# 05 - Add safe Neovim exit confirmation

| Field | Value |
|---|---|
| Status | In progress |
| Step | 05 |
| Commit | `CONFIG(05): add safe Neovim exit confirmation` |

## Files

- `.config/nvim/lua/opts.lua` (EDIT)

## Changes

Enable Neovim's native confirmation behavior so commands that would abandon a
modified buffer offer save, discard, and cancel choices instead of only
failing. Add no keymap or plugin.

## Test

Automated: `nvim -u NONE --headless '+luafile
.config/nvim/lua/opts.lua' '+lua assert(vim.o.confirm)' +qa`.

Manual: modify a disposable buffer, invoke quit, exercise save/discard/cancel,
then quit a clean buffer as a control.

## Acceptance

- [ ] Dirty-buffer quit presents native confirmation choices.
- [ ] Clean-buffer quit remains immediate.

## Risks & Rollback

This changes command-line quit behavior but not mappings. Disable the option to
restore error-only handling.
