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
			'cpp',
			'css',
			'diff',
			'html',
			'javascript',
			'lua',
			'luadoc',
			'markdown',
			'markdown_inline',
			'php',
			'python',
			'query',
			'scss',
			'typescript',
			'vim',
			'vimdoc',
			'php'
		},
		auto_install = true,
		highlight = {
			enable = true,
			additional_vim_regex_highlighting = { 'ruby' },
		},
		indent = { enable = true, disable = { 'ruby' } },
	},
}
