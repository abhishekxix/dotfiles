return {
	'neovim/nvim-lspconfig',
	dependencies = {
		{ 'williamboman/mason.nvim', config = true },
		'williamboman/mason-lspconfig.nvim',
		'WhoIsSethDaniel/mason-tool-installer.nvim',
		{ 'j-hui/fidget.nvim', opts = {} },
		'hrsh7th/cmp-nvim-lsp',
	},
	config = function()
		vim.api.nvim_create_autocmd('LspAttach', {
			group = vim.api.nvim_create_augroup('as-lsp-attach', { clear = true }),
			callback = function(event)
				local map = function(keys, func, desc, mode)
					mode = mode or 'n'
					vim.keymap.set(mode, keys, func, { buffer = event.buf, desc = 'LSP: ' .. desc })
				end

				map('gd', require('telescope.builtin').lsp_definitions, '[G]oto [D]efinition')

				map('gr', require('telescope.builtin').lsp_references, '[G]oto [R]eferences')

				map('gI', require('telescope.builtin').lsp_implementations, '[G]oto [I]mplementation')

				map('<leader>D', require('telescope.builtin').lsp_type_definitions, 'Type [D]efinition')

				map('<leader>ds', require('telescope.builtin').lsp_document_symbols, '[D]ocument [S]ymbols')

				map('<leader>ws', require('telescope.builtin').lsp_dynamic_workspace_symbols, '[W]orkspace [S]ymbols')

				map('<leader>rn', vim.lsp.buf.rename, '[R]e[n]ame')

				map('<leader>ca', vim.lsp.buf.code_action, '[C]ode [A]ction', { 'n', 'x' })
				map('<leader>cd', vim.diagnostic.open_float, '[C]ode [d]iagnostic')

				-- Hide the virtual text
				vim.diagnostic.config {
					virtual_text = false,
				}

				map('gD', vim.lsp.buf.declaration, '[G]oto [D]eclaration')

				local client = vim.lsp.get_client_by_id(event.data.client_id)
				if client and client:supports_method(vim.lsp.protocol.Methods.textDocument_documentHighlight, event.buf) then
					local highlight_augroup = vim.api.nvim_create_augroup('as-lsp-highlight', { clear = false })
					vim.api.nvim_create_autocmd({ 'CursorHold', 'CursorHoldI' }, {
						buffer = event.buf,
						group = highlight_augroup,
						callback = vim.lsp.buf.document_highlight,
					})

					vim.api.nvim_create_autocmd({ 'CursorMoved', 'CursorMovedI' }, {
						buffer = event.buf,
						group = highlight_augroup,
						callback = vim.lsp.buf.clear_references,
					})

					vim.api.nvim_create_autocmd('LspDetach', {
						group = vim.api.nvim_create_augroup('as-lsp-detach', { clear = true }),
						callback = function(event2)
							vim.lsp.buf.clear_references()
							vim.api.nvim_clear_autocmds { group = 'as-lsp-highlight', buffer = event2.buf }
						end,
					})
				end

				if client and client:supports_method(vim.lsp.protocol.Methods.textDocument_inlayHint, event.buf) then
					map('<leader>th', function()
						vim.lsp.inlay_hint.enable(not vim.lsp.inlay_hint.is_enabled { bufnr = event.buf })
					end, '[T]oggle Inlay [H]ints')
				end
			end,
		})

		local capabilities = vim.lsp.protocol.make_client_capabilities()
		capabilities = vim.tbl_deep_extend('force', capabilities, require('cmp_nvim_lsp').default_capabilities())

		local servers = {
			lua_ls = {
				settings = {
					Lua = {
						completion = {
							callSnippet = 'Replace',
						},
					},
				},
			},
			phpactor = {},
			ts_ls = {},
			emmet_ls = {
				filetypes = { 'html', 'php', 'blade', 'javascriptreact', 'typescriptreact' },
				init_options = {
					includeLanguages = {
						blade = 'php',
						php = 'php',
					},
					showAbbreviationSuggestions = true,
					showExpandedAbbreviation = 'always',
					showSuggestionsAsSnippets = false,
				},
			},
			somesass_ls = {},
			cssls = {},
			clangd = {
				capabilities = {
					offsetEncoding = 'utf-8',
				},
			},
			bashls = {
				filetypes = { 'bash', 'sh' },
			},
			pyright = {},
			jsonls = {},
			jdtls = {},
			gopls = {},
		}

		require('mason').setup()

		local ensure_installed = vim.tbl_keys(servers or {})
		vim.list_extend(ensure_installed, {
			'stylua',
		})
		require('mason-tool-installer').setup { ensure_installed = ensure_installed }

		require('mason-lspconfig').setup {
			handlers = {
				function(server_name)
					local server = servers[server_name] or {}
					server.capabilities = vim.tbl_deep_extend('force', {}, capabilities, server.capabilities or {})
					require('lspconfig')[server_name].setup(server)
				end,
			},
		}
	end,
}
