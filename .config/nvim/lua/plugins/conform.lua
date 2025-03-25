return {
	'stevearc/conform.nvim',
	keys = {
		{
			'<leader>f',
			function()
				require('conform').format { async = true, lsp_format = 'fallback' }
			end,
			mode = '',
			desc = '[F]ormat buffer',
		},
	},
	opts = {
		notify_on_error = false,
		formatters_by_ft = {
			lua = { 'stylua' },
			bash = { 'shfmt' },
			python = { 'black' },
			go = { 'gofmt' },
			javascript = { 'prettier' },
			typescript = { 'prettier' },
			javascriptreact = { 'prettier' },
			typescriptreact = { 'prettier' },
			json = { 'prettier' },
			css = { 'prettier' },
			scss = { 'prettier' },
		},
	},
}
