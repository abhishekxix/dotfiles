-- Adds git related signs to the gutter, as well as utilities for managing changes.
-- This is the single source of truth for the gitsigns.nvim spec.

return {
  'lewis6991/gitsigns.nvim',
  event = { 'BufReadPre', 'BufNewFile' },
  opts = {
    signs = {
      add = { text = '+' },
      change = { text = '~' },
      delete = { text = '_' },
      topdelete = { text = '‾' },
      changedelete = { text = '~' },
      untracked = { text = '┆' },
    },
    signs_staged = {
      add = { text = '+' },
      change = { text = '~' },
      delete = { text = '_' },
      topdelete = { text = '‾' },
      changedelete = { text = '~' },
      untracked = { text = '┆' },
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