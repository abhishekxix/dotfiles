return {
	require 'lazy-plugins.vim-sleuth',
	require 'lazy-plugins.git-signs',
	require 'lazy-plugins.which-key',
	require 'lazy-plugins.telescope',
	require 'lazy-plugins.lazydev',
	require 'lazy-plugins.luvit-meta',
	require 'lazy-plugins.nvim-lspconfig',
	require 'lazy-plugins.conform',
	require 'lazy-plugins.nvim-cmp',
	require('lazy-plugins.my-nvim-theme').tokyo_night,
	require 'lazy-plugins.todo-comments',
	require 'lazy-plugins.mini',
	require 'lazy-plugins.nvim-treesitter',
	require 'lazy-plugins.nvim-ts-autotag',
	-- require 'kickstart.plugins.debug',
	-- require 'kickstart.plugins.indent_line',
	require 'kickstart.plugins.lint',
	require 'kickstart.plugins.autopairs',
	require 'kickstart.plugins.neo-tree',
	require 'kickstart.plugins.gitsigns', -- adds gitsigns recommend keymaps

	{ import = 'custom.plugins' },
}
