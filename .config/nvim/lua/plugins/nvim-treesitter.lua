return {
  'nvim-treesitter/nvim-treesitter',
  lazy = false, -- plugin does NOT support lazy-loading
  build = ':TSUpdate',
  config = function()
    require('nvim-treesitter').setup {
      install_dir = vim.fn.stdpath 'data' .. '/site',
    }

    -- Skip parser installation when the compiler CLI is absent; print one
    -- actionable diagnostic instead of one error per parser.
    if vim.fn.executable 'tree-sitter' == 0 and vim.fn.executable 'cc' == 0 then
      vim.schedule(function()
        vim.notify(
          'nvim-treesitter: no tree-sitter CLI or C compiler found; install tree-sitter-cli to build parsers',
          vim.log.levels.WARN
        )
      end)
      return
    end

    -- Install parsers (async). These replace the old `ensure_installed`.
    require('nvim-treesitter').install(require('langs').get_parsers())
  end,
}