# 07 — nvim leftovers: formatters + autocmd polish

| Field | Value |
|---|---|
| Status | Planning |
| Step | 07 |
| Commit | `CONFIG(07): nvim prettier for html/md/php, resize/checktime/last-place/q-close` |

## Files

- `.config/nvim/lua/langs.lua` (EDIT)
- `.config/nvim/lua/autocommands.lua` (EDIT)

## Changes

1. Add `prettier` to the `html`, `markdown`, and `php` specs in `langs.lua`
   (formatters only — no server/parser changes). Prettier is already in the
   toolchain and handles all three; the specs just don't declare it, so
   conform never formats them.
2. Add the deferred small autocmds in `autocommands.lua` (no keymap/plugin
   changes, per Non-goals):
   - `VimResized` → `wincmd =` (equalize splits on resize)
   - `FocusGained`/`BufEnter` checktime reload
   - last-place jump on `BufReadPost`
   - `q`-to-close for help/quickfix buffers

## Test

- `:ConformInfo` on an html/md/php buffer shows prettier.
- Resize splits (equalize), reopen a file (lands on last line), `q` closes help.

## Acceptance

- [ ] format works in html/md/php
- [ ] resize / checktime / last-place / q-close all behave
