return {
  'folke/todo-comments.nvim',
  keys = {
    { '<leader>st', '<cmd>TodoTelescope<CR>', desc = '[S]earch [T]ODOs' },
  },
  dependencies = { 'nvim-lua/plenary.nvim' },
  opts = { signs = false },
}
