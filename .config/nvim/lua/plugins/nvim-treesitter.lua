return {
  'nvim-treesitter/nvim-treesitter',
  lazy = false, -- plugin does NOT support lazy-loading
  build = ':TSUpdate',
  config = function()
    require('nvim-treesitter').setup {
      install_dir = vim.fn.stdpath 'data' .. '/site',
    }

    -- Install parsers (async). These replace the old `ensure_installed`.
    require('nvim-treesitter').install {
      'bash',
      'c',
      'cpp',
      'css',
      'diff',
      'html',
      'javascript',
      'jsdoc',
      'json',
      'lua',
      'luadoc',
      'markdown',
      'markdown_inline',
      'php',
      'python',
      'query',
      'scss',
      'toml',
      'tsx',
      'typescript',
      'vim',
      'vimdoc',
    }
  end,
}