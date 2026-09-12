vim.api.nvim_create_autocmd('TextYankPost', {
  desc = 'Highlight when yanking (copying) text',
  group = vim.api.nvim_create_augroup('as-highlight-yank', { clear = true }),
  callback = function()
    vim.highlight.on_yank()
  end,
})

-- Jump to the last cursor position when reopening a file.
vim.api.nvim_create_autocmd('BufReadPost', {
  desc = 'Jump to last cursor position',
  group = vim.api.nvim_create_augroup('as-last-place', { clear = true }),
  callback = function(args)
    local mark = vim.api.nvim_buf_get_mark(args.buf, '"')
    local lines = vim.api.nvim_buf_line_count(args.buf)
    if mark[1] > 0 and mark[1] <= lines then
      pcall(vim.api.nvim_win_set_cursor, 0, mark)
    end
  end,
})

-- Enable treesitter highlighting + folds for filetypes that have a parser.
-- (Parser install list lives in plugins/nvim-treesitter.lua.)
local langs = require 'langs'

-- Filetypes whose treesitter parser has a different name.
local parser_aliases = {
  zsh = 'bash',
  ['yaml.docker-compose'] = 'yaml',
  javascriptreact = 'javascript',
  typescriptreact = 'tsx',
}

vim.api.nvim_create_autocmd('FileType', {
  desc = 'Enable treesitter highlighting and folding',
  group = vim.api.nvim_create_augroup('as-treesitter', { clear = true }),
  pattern = langs.get_filetypes(),
  callback = function(args)
    local parser = parser_aliases[args.match] or args.match
    local lang = vim.treesitter.language.get_lang(parser) or parser
    if not pcall(vim.treesitter.language.add, lang) then
      -- One deduped diagnostic per missing parser; never install a broken
      -- fold expression when highlighting cannot start.
      vim.schedule(function()
        vim.notify(
          ('treesitter: no parser for %s (run :TSUpdate, needs tree-sitter CLI)'):format(args.match),
          vim.log.levels.WARN
        )
      end)
      return
    end
    local ok = pcall(vim.treesitter.start, args.buf, lang)
    if not ok then
      vim.schedule(function()
        vim.notify(
          ('treesitter: could not start %s highlighting (run :TSUpdate)'):format(lang),
          vim.log.levels.WARN
        )
      end)
      return
    end
    vim.wo.foldexpr = 'v:lua.vim.treesitter.foldexpr()'
    vim.wo.foldmethod = 'expr'
  end,
})
