-- autopairs
-- https://github.com/windwp/nvim-autopairs

return {
  'windwp/nvim-autopairs',
  event = 'InsertEnter',
  -- Optional dependency
  dependencies = { 'hrsh7th/nvim-cmp' },
  config = function()
    require('nvim-autopairs').setup {}

    -- Automatically add `(` after selecting a function or method. Guard the
    -- cmp wiring so it only runs when nvim-cmp is actually available.
    local ok, cmp = pcall(require, 'cmp')
    if ok then
      local cmp_autopairs = require 'nvim-autopairs.completion.cmp'
      cmp.event:on('confirm_done', cmp_autopairs.on_confirm_done())
    end
  end,
}