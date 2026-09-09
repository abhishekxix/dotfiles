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
  callback = function(args)
    -- Skip filetypes with no installed parser (e.g. zsh,
    -- yaml.docker-compose): start() would raise and spam ERROR
    -- notifications. get_lang maps ft -> parser name; the parser/*.so
    -- lookup checks one is actually installed.
    local lang = vim.treesitter.language.get_lang(args.match)
    if #vim.api.nvim_get_runtime_file('parser/' .. lang .. '.so', true) == 0 then
      return
    end
    local ok, err = pcall(vim.treesitter.start)
    if not ok then
      vim.schedule(function()
        vim.notify(
          ('treesitter: no parser for %s: %s'):format(args.match, err),
          vim.log.levels.ERROR
        )
      end)
      return
    end
    vim.wo.foldexpr = 'v:lua.vim.treesitter.foldexpr()'
    vim.wo.foldmethod = 'expr'
  end,
})
