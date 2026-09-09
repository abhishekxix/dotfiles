vim.api.nvim_create_autocmd('TextYankPost', {
  desc = 'Highlight when yanking (copying) text',
  group = vim.api.nvim_create_augroup('as-highlight-yank', { clear = true }),
  callback = function()
    vim.highlight.on_yank()
  end,
})

-- Equalize splits when the terminal window is resized.
vim.api.nvim_create_autocmd('VimResized', {
  desc = 'Equalize splits on terminal resize',
  group = vim.api.nvim_create_augroup('as-resize-splits', { clear = true }),
  callback = function()
    vim.cmd 'wincmd ='
  end,
})

-- Reload files changed on disk when regaining focus or entering a buffer.
vim.api.nvim_create_autocmd({ 'FocusGained', 'BufEnter' }, {
  desc = 'Reload file changed on disk',
  group = vim.api.nvim_create_augroup('as-checktime', { clear = true }),
  command = 'checktime',
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

-- `q` closes help and quickfix buffers.
vim.api.nvim_create_autocmd('FileType', {
  desc = 'q closes help/quickfix',
  group = vim.api.nvim_create_augroup('as-q-close', { clear = true }),
  pattern = { 'help', 'qf' },
  callback = function(args)
    vim.keymap.set('n', 'q', '<cmd>close<cr>', { buffer = args.buf, silent = true })
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
