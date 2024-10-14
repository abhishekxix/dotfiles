return {
	github_theme = {
		'projekt0n/github-nvim-theme',
		name = 'github-theme',
		lazy = false,
		priority = 1000,
		config = function()
			require('github-theme').setup {}

			vim.cmd 'colorscheme github_dark_default'
		end,
	},
	gruvbox = {
		'ellisonleao/gruvbox.nvim',
		lazy = false,
		priority = 1000,
		config = function()
			vim.cmd 'colorscheme gruvbox'
		end
	},
}
