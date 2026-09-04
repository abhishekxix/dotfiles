# Step 02 — gitsigns (merge duplicates, modernize API)

Files touched:
- `lua/plugins/git-signs.lua`  (DELETE)
- `lua/plugins/gitsigns.lua`   (REWRITE to single source of truth)

## Problem

Two files register the same plugin `lewis6991/gitsigns.nvim`, each with a
different spec:

- `git-signs.lua`: only sets `opts.signs`.
- `gitsigns.lua`: sets `opts.on_attach` + all keymaps.

Both are loaded, so lazy.nvim merges the two `opts` in an unspecified/erroneous
way, and the two keymap sets overlap. This is a latent bug. Merge into ONE file.

## 0.12 relevance

gitsigns requires Neovim >= 0.9.0, so 0.12 is fine. No API break from Neovim
itself. The API drift in the current `gitsigns.lua` is *plugin-internal* and
should be updated to the current README example:

- `diffthis` → `gitsigns.diffthis` (present) and `diffthis('~')` for last commit
  (current file calls `diffthis('@')` which is not the documented convention —
  use `'~'` per README).
- Add `preview_hunk_inline` (`:Gitsigns preview_hunk_inline`) — currently missing.
- Add `select_hunk` text object (`ih` in `o`/`x` mode) — currently missing.
- Add `setqflist` (`<leader>hQ` / `<leader>hq`) — currently missing (newer feature).
- `toggle_word_diff` is newer and replaces the older word-diff approach.
- `undo_stage_hunk` remains valid.

## Target file: `lua/plugins/gitsigns.lua`

```lua
return {
  'lewis6991/gitsigns.nvim',
  event = { 'BufReadPre', 'BufNewFile' },
  opts = {
    signs = {
      add          = { text = '+' },
      change       = { text = '~' },
      delete       = { text = '_' },
      topdelete    = { text = '‾' },
      changedelete = { text = '~' },
      untracked    = { text = '┆' },
    },
    signs_staged = {
      add          = { text = '+' },
      change       = { text = '~' },
      delete       = { text = '_' },
      topdelete    = { text = '‾' },
      changedelete = { text = '~' },
      untracked    = { text = '┆' },
    },
    signs_staged_enable = true,
    on_attach = function(bufnr)
      local gs = package.loaded.gitsigns or require 'gitsigns'

      local function map(mode, l, r, opts)
        opts = opts or {}
        opts.buffer = bufnr
        vim.keymap.set(mode, l, r, opts)
      end

      -- Navigation
      map('n', ']c', function()
        if vim.wo.diff then
          vim.cmd.normal { ']c', bang = true }
        else
          gs.nav_hunk 'next'
        end
      end, { desc = 'Next git hunk' })

      map('n', '[c', function()
        if vim.wo.diff then
          vim.cmd.normal { '[c', bang = true }
        else
          gs.nav_hunk 'prev'
        end
      end, { desc = 'Previous git hunk' })

      -- Actions
      map('n', '<leader>hs', gs.stage_hunk, { desc = 'Stage hunk' })
      map('n', '<leader>hr', gs.reset_hunk, { desc = 'Reset hunk' })
      map('v', '<leader>hs', function() gs.stage_hunk { vim.fn.line '.', vim.fn.line 'v' } end, { desc = 'Stage hunk' })
      map('v', '<leader>hr', function() gs.reset_hunk { vim.fn.line '.', vim.fn.line 'v' } end, { desc = 'Reset hunk' })
      map('n', '<leader>hS', gs.stage_buffer, { desc = 'Stage buffer' })
      map('n', '<leader>hu', gs.undo_stage_hunk, { desc = 'Undo stage hunk' })
      map('n', '<leader>hR', gs.reset_buffer, { desc = 'Reset buffer' })
      map('n', '<leader>hp', gs.preview_hunk, { desc = 'Preview hunk' })
      map('n', '<leader>hi', gs.preview_hunk_inline, { desc = 'Preview hunk inline' })
      map('n', '<leader>hb', function() gs.blame_line { full = true } end, { desc = 'Blame line' })
      map('n', '<leader>hd', gs.diffthis, { desc = 'Diff against index' })
      map('n', '<leader>hD', function() gs.diffthis '~' end, { desc = 'Diff against last commit' })
      map('n', '<leader>hQ', function() gs.setqflist 'all' end, { desc = 'Quickfix all hunks' })
      map('n', '<leader>hq', gs.setqflist, { desc = 'Quickfix hunks' })

      -- Text object
      map({ 'o', 'x' }, 'ih', gs.select_hunk, { desc = 'Select hunk' })

      -- Toggles
      map('n', '<leader>tb', gs.toggle_current_line_blame, { desc = 'Toggle line blame' })
      map('n', '<leader>tw', gs.toggle_word_diff, { desc = 'Toggle word diff' })
      map('n', '<leader>td', gs.toggle_deleted, { desc = 'Toggle deleted' })
    end,
  },
}
```

Then delete `lua/plugins/git-signs.lua`.

## `topdelete` glyph note

The old `git-signs.lua` used a multi-byte glyph for `topdelete` (shown redacted
in some views). Pick an explicit, unambiguous glyph (e.g. `'‾'` = U+203E
overline, or the gitsigns default `'┃'`). Ensure it renders in your terminal
font before finalizing.

## Note on `event`

The README doesn't force a specific event. `event = { 'BufReadPre', 'BufNewFile' }`
keeps it lazy but attaches before first render in normal file editing.

## Acceptance checklist

- [ ] Only ONE gitsigns spec remains: `grep -r "gitsigns.nvim" lua/plugins/` returns a single file.
- [ ] `:Gitsigns` commands listed and no duplicate keymap warnings at startup.
- [ ] `]c`/`[c` navigate hunks in both normal diff and gitsigns mode.
- [ ] `<leader>h*` actions all work (stage, reset, preview inline, blame, diff, qflist).
- [ ] `ih` selects a hunk in operator-pending and visual mode.