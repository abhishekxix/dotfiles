return {
  'folke/which-key.nvim',
  event = 'VeryLazy',
  opts = {
    preset = 'classic',
    icons = {
      mappings = vim.g.have_nerd_font,
    },
    spec = {
      { '<leader>c', group = '[C]ode', mode = { 'n', 'x' } },
      { '<leader>d', group = '[D]ocument' },
      { '<leader>r', group = '[R]ename' },
      { '<leader>s', group = '[S]earch' },
      { '<leader>w', group = '[W]orkspace' },
      { '<leader>t', group = '[T]oggle' },
      { '<leader>h', group = 'Git [H]unk', mode = { 'n', 'v' } },
      { '<leader>m', group = 'mini.surround' },
      { '<leader>p', group = 'Personal', mode = { 'n', 'v' } },
    },
  },
}