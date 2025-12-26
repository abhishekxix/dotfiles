local lazypath = vim.fn.stdpath 'data' .. '/lazy/lazy.nvim'
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  local lazyrepo = 'https://github.com/folke/lazy.nvim.git'
  local out = vim.fn.system { 'git', 'clone', '--filter=blob:none', '--branch=stable', lazyrepo, lazypath }
  if vim.v.shell_error ~= 0 then
    error('Error cloning lazy.nvim:\n' .. out)
  end
end ---@diagnostic disable-next-line: undefined-field
vim.opt.rtp:prepend(lazypath)

local lazy_plugins = {
  require 'plugins.vim-sleuth',
  require 'plugins.git-signs',
  require 'plugins.which-key',
  require 'plugins.telescope',
  require 'plugins.lazydev',
  require 'plugins.luvit-meta',
  require 'plugins.nvim-lspconfig',
  require 'plugins.conform',
  require 'plugins.nvim-cmp',
  require('plugins.my-nvim-theme').catppuccin,
  require 'plugins.todo-comments',
  require 'plugins.mini',
  require 'plugins.nvim-treesitter',
  require 'plugins.nvim-ts-autotag',
  require 'plugins.lint',
  require 'plugins.autopairs',
  require 'plugins.neo-tree',
  require 'plugins.gitsigns',
  require 'plugins.copilot',
}

require('lazy').setup(lazy_plugins, {
  ui = {
    icons = vim.g.have_nerd_font and {} or {
      cmd = '⌘',
      config = '🛠',
      event = '📅',
      ft = '📂',
      init = '⚙',
      keys = '🗝',
      plugin = '🔌',
      runtime = '💻',
      require = '🌙',
      source = '📄',
      start = '🚀',
      task = '📌',
      lazy = '💤 ',
    },
  },
})
