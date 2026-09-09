vim.keymap.set('n', '<Esc>', '<cmd>nohlsearch<CR>')

vim.keymap.set('n', '<leader>q', vim.diagnostic.setloclist, { desc = 'Open diagnostic [Q]uickfix list' })

vim.keymap.set('t', '<Esc><Esc>', '<C-\\><C-n>', { desc = 'Exit terminal mode' })

vim.keymap.set('n', '<C-h>', '<C-w><C-h>', { desc = 'Move focus to the left window' })
vim.keymap.set('n', '<C-l>', '<C-w><C-l>', { desc = 'Move focus to the right window' })
vim.keymap.set('n', '<C-j>', '<C-w><C-j>', { desc = 'Move focus to the lower window' })
vim.keymap.set('n', '<C-k>', '<C-w><C-k>', { desc = 'Move focus to the upper window' })

-- Personal: system clipboard (+", which is X11 PRIMARY/CLIPBOARD depending on tool)
for _, mode in ipairs { 'n', 'v' } do
  for lhs, map in pairs {
    d = { '"+d', 'Delete to system clipboard' },
    y = { '"+y', 'Yank to system clipboard' },
    p = { '"+p', 'Put from system clipboard' },
    P = { '"+P', 'Put from system clipboard' },
  } do
    local rhs, desc = map[1], map[2]
    vim.keymap.set(mode, '<leader>p' .. lhs, rhs, { desc = desc })
  end
end
