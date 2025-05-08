return {
	'github/copilot.vim',
	config = function()
		vim.cmd 'Copilot disable'
		vim.g.copilot_no_tab_map = true

		vim.keymap.set('i', '<C-Y>', 'copilot#Accept("\\<CR>")', {
			expr = true,
			replace_keycodes = false,
			silent = true,
		})

		vim.keymap.set('i', '<C-J>', '<Plug>(copilot-next)')
		vim.keymap.set('i', '<C-K>', '<Plug>(copilot-previous)')
		vim.keymap.set('i', '<C-]>', '<Plug>(copilot-suggest)')
		vim.keymap.set('i', '<C-\\>', '<Plug>(copilot-dismiss)')
		vim.keymap.set('i', '<S-Right>', '<Plug>(copilot-accept-word)')
		vim.keymap.set('i', '<C-S-Right>', '<Plug>(copilot-accept-line)')

		-- set a keymap in normal mode to enable/disable copilot
		vim.keymap.set('n', '<leader>ace', function()
				vim.cmd 'Copilot enable'
		end, { desc = 'Enable Copilot' })

		vim.keymap.set('n', '<leader>acd', function()
				vim.cmd 'Copilot disable'
		end, { desc = 'Disable Copilot' })
	end,
}
