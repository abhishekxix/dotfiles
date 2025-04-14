return {
	github_theme = {
		'projekt0n/github-nvim-theme',
		name = 'github-theme',
		lazy = false,
		priority = 1000,
		config = function()
			require('github-theme').setup {
				options = {
					transparent = true,
				},
			}

			vim.cmd 'colorscheme github_dark_default'
		end,
	},
	catppuccin = {
		'catppuccin/nvim',
		name = 'catpuccin',
		lazy = false,
		priority = 1000,
		config = function()
			require('catppuccin').setup {
				flavour = 'mocha',
				-- transparent_background = true,
			}

			vim.cmd 'colorscheme catppuccin'
		end,
	},
	tokyo_night = {
		'folke/tokyonight.nvim',
		lazy = false,
		priority = 1000,
		config = function()
			require('tokyonight').setup {
				style = 'night',
				transparent = 'true',
			}

			vim.cmd 'colorscheme tokyonight'
		end,
	},
	rose_pine = {
		'rose-pine/neovim',
		name = 'rose-pine',
		lazy = false,
		priority = 1000,
		config = function()
			require('rose-pine').setup {
				styles = {
					transparency = true,
				},
			}

			vim.cmd 'colorscheme rose-pine'
		end,
	},
	moonfly = {
		'bluz71/vim-moonfly-colors',
		name = 'moonfly',
		lazy = false,
		priority = 1000,
		config = function()
			vim.cmd 'colorscheme moonfly'
			vim.g.moonflyUndercurls = false
		end,
	},
}
