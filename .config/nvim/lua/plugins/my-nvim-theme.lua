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
				transparent_background = true,
				float = {
					transparent = true,
					solid = true,
				},
				auto_integrations = true,
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
		config = function()
			require('rose-pine').setup {
				styles = {
					transparency = true,
				},
			}

			vim.cmd 'colorscheme rose-pine'
		end,
	},
}
