vim.keymap.set('n', '<Esc>', '<cmd>nohlsearch<CR>')

vim.keymap.set('n', '<leader>q', vim.diagnostic.setloclist, { desc = 'Open diagnostic [Q]uickfix list' })

vim.keymap.set('t', '<Esc><Esc>', '<C-\\><C-n>', { desc = 'Exit terminal mode' })

vim.keymap.set('n', '<C-h>', '<C-w><C-h>', { desc = 'Move focus to the left window' })
vim.keymap.set('n', '<C-l>', '<C-w><C-l>', { desc = 'Move focus to the right window' })
vim.keymap.set('n', '<C-j>', '<C-w><C-j>', { desc = 'Move focus to the lower window' })
vim.keymap.set('n', '<C-k>', '<C-w><C-k>', { desc = 'Move focus to the upper window' })

vim.keymap.set('n', '<leader>ad', '"+d', { desc = 'Delete to system clipboard' })
vim.keymap.set('n', '<leader>ay', '"+y', { desc = 'Yank to system clipboard' })
vim.keymap.set('n', '<leader>ap', '"+p', { desc = 'Put from system clipboard' })
vim.keymap.set('n', '<leader>aP', '"+P', { desc = 'Put from system clipboard' })
vim.keymap.set('v', '<leader>ad', '"+d', { desc = 'Delete to system clipboard' })
vim.keymap.set('v', '<leader>ay', '"+y', { desc = 'Yank to system clipboard' })
vim.keymap.set('v', '<leader>ap', '"+p', { desc = 'Put from system clipboard' })
vim.keymap.set('v', '<leader>aP', '"+P', { desc = 'Put from system clipboard' })
