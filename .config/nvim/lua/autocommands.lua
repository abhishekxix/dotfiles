vim.api.nvim_create_autocmd('TextYankPost', {
  desc = 'Highlight when yanking (copying) text',
  group = vim.api.nvim_create_augroup('as-highlight-yank', { clear = true }),
  callback = function()
    vim.highlight.on_yank()
  end,
})

-- Enable treesitter highlighting + folds for filetypes that have a parser.
-- (Parser install list lives in plugins/nvim-treesitter.lua.)
local langs = require 'langs'

vim.api.nvim_create_autocmd('FileType', {
  desc = 'Enable treesitter highlighting and folding',
  group = vim.api.nvim_create_augroup('as-treesitter', { clear = true }),
  pattern = langs.get_filetypes(),
  callback = function()
    -- syntax highlighting, provided by [ADDRESS] core
    vim.treesitter.start()
    -- folds, provided by [ADDRESS] core
    vim.wo.foldexpr = 'v:lua.vim.treesitter.foldexpr()'
    vim.wo.foldmethod = 'expr'
  end,
})
