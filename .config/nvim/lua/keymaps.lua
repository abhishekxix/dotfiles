vim.keymap.set('n', '<Esc>', '<cmd>nohlsearch<CR>')

vim.keymap.set('n', '<leader>q', vim.diagnostic.setloclist, { desc = 'Open diagnostic [Q]uickfix list' })

vim.keymap.set('t', '<Esc><Esc>', '<C-\\><C-n>', { desc = 'Exit terminal mode' })

vim.keymap.set('n', '<C-h>', '<C-w><C-h>', { desc = 'Move focus to the left window' })
vim.keymap.set('n', '<C-l>', '<C-w><C-l>', { desc = 'Move focus to the right window' })
vim.keymap.set('n', '<C-j>', '<C-w><C-j>', { desc = 'Move focus to the lower window' })
vim.keymap.set('n', '<C-k>', '<C-w><C-k>', { desc = 'Move focus to the upper window' })

-- Save (NB: <leader>w is the [W]orkspace group; <leader>W avoids the clash)
vim.keymap.set({ 'n', 'i', 'v' }, '<C-s>', '<cmd>w<CR><Esc>', { desc = '[S]ave buffer' })
vim.keymap.set('n', '<leader>W', '<cmd>w<CR>', { desc = '[W]rite buffer' })

-- Buffers
vim.keymap.set('n', '<leader>bd', '<cmd>bd<CR>', { desc = '[B]uffer [D]elete' })
vim.keymap.set('n', '<leader>bx', '<cmd>bd!<CR>', { desc = '[B]uffer delete (!) force' })

-- Diagnostics / quickfix navigation
vim.keymap.set('n', '[d', vim.diagnostic.goto_prev, { desc = 'Previous [D]iagnostic' })
vim.keymap.set('n', ']d', vim.diagnostic.goto_next, { desc = 'Next [D]iagnostic' })
vim.keymap.set('n', '[q', '<cmd>cprev<CR>', { desc = 'Previous [Q]uickfix' })
vim.keymap.set('n', ']q', '<cmd>cnext<CR>', { desc = 'Next [Q]uickfix' })

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
