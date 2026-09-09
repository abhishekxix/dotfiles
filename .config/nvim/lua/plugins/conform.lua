return {
  'stevearc/conform.nvim',
  keys = {
    {
      '<leader>f',
      function()
        require('conform').format { async = true, lsp_format = 'fallback' }
      end,
      mode = { 'n', 'x' },
      desc = '[F]ormat buffer',
    },
    {
      '<leader>tf',
      function()
        vim.g.disable_autoformat = not vim.g.disable_autoformat
        vim.notify(
          'Format on save ' .. (vim.g.disable_autoformat and 'OFF' or 'ON'),
          vim.log.levels.INFO
        )
      end,
      mode = 'n',
      desc = '[T]oggle [F]ormat on save',
    },
  },
  opts = {
    notify_on_error = false,
    -- Default off: opt in per session with <leader>tf.
    format_on_save = function(bufnr)
      if vim.g.disable_autoformat == nil then
        vim.g.disable_autoformat = true
      end
      if vim.g.disable_autoformat then
        return
      end
      return { timeout_ms = 500, lsp_format = 'fallback' }
    end,
    formatters_by_ft = require('langs').get_formatters_by_ft(),
  },
}
