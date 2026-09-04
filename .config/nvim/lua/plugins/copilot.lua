return {
  'github/copilot.vim',
  config = function()
    vim.cmd 'Copilot disable'
    vim.g.copilot_no_tab_map = true

    vim.keymap.set('i', '<C-Y>', 'copilot#Accept("\\<CR>")', {
      expr = true,
      replace_keycodes = false,
      silent = true,
    })

    vim.keymap.set('i', '<C-J>', '<Plug>(copilot-next)')
    vim.keymap.set('i', '<C-K>', '<Plug>(copilot-previous)')
    vim.keymap.set('i', '<C-]>', '<Plug>(copilot-suggest)')
    vim.keymap.set('i', '<C-\\>', '<Plug>(copilot-dismiss)')
    vim.keymap.set('i', '<S-Right>', '<Plug>(copilot-accept-word)')
    vim.keymap.set('i', '<C-S-Right>', '<Plug>(copilot-accept-line)')

    -- set a keymap in normal mode to enable/disable copilot
    local function copilot_enabled()
      return vim.g.copilot_enabled == nil or vim.g.copilot_enabled == 1
    end

    vim.keymap.set('n', '<leader>tc', function()
      if copilot_enabled() then
        vim.cmd 'Copilot disable'
        vim.notify('Copilot disabled', vim.log.levels.INFO)
      else
        vim.cmd 'Copilot enable'
        vim.notify('Copilot enabled', vim.log.levels.INFO)
      end
    end, { desc = 'Toggle Copilot' })
  end,
}
