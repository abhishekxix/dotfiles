return {
	'nvim-treesitter/nvim-treesitter',
	build = ':TSUpdate',
	main = 'nvim-treesitter.configs',
	config = function()
		vim.filetype.add {
			pattern = {
				['.*%.blade%.php'] = 'html',
			},
		}
	end,
	opts = {
		ensure_installed = {
			'bash',
			'c',
			'css',
			'scss',
			'diff',
			'html',
			'lua',
			'luadoc',
			'markdown',
			'markdown_inline',
			'query',
			'vim',
			'vimdoc',
			'php',
			'cpp',
			'python',
			'javascript',
			'typescript',
		},
		auto_install = true,
		highlight = {
			enable = true,
			additional_vim_regex_highlighting = { 'ruby' },
		},
		indent = { enable = true, disable = { 'ruby' } },
	},
}
