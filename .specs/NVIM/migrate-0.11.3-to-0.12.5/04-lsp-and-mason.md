# Step 04 — LSP (nvim-lspconfig → vim.lsp.config), mason, conform, lint

Files touched:
- `lua/plugins/nvim-lspconfig.lua`  (REWRITE — legacy `require('lspconfig').setup()` is deprecated)
- `lua/plugins/conform.lua`          (minor — validates against current API)
- `lua/plugins/lint.lua`             (minor — verify linter names)
- (new) optional `lua/lsp-servers.lua` or inline config

## ⚠️ The big change

`nvim-lspconfig`'s **legacy framework is deprecated** (issue #3693). The modern
path is Neovim's built-in `vim.lsp.config()` + `vim.lsp.enable()` (0.11+).

Your current spec uses the deprecated pattern throughout:

```lua
require('mason-lspconfig').setup {
  handlers = {
    function(server_name)
      local server = servers[server_name] or {}
      server.capabilities = vim.tbl_deep_extend('force', {}, capabilities, server.capabilities or {})
      require('lspconfig')[server_name].setup(server)   -- DEPRECATED
    end,
  },
}
```

Since nvim-lspconfig >= 2.0.0 and 0.12, `require('lspconfig')[name].setup()` will
eventually error. **Migrate to `vim.lsp.config` / `vim.lsp.enable`.**

## New architecture

1. `mason.nvim` installs servers (unchanged).
2. `mason-lspconfig.nvim` **auto-enables** installed servers via `vim.lsp.enable()`
   (its `automatic_enable` defaults to `true`). You no longer need a custom
   `handlers` loop unless you're customizing options per server.
3. Per-server customization is done with `vim.lsp.config('name', { ... })` in a
   plain lua file (before/alongside enabling).
4. Keymaps + capabilities still attach via an `LspAttach` autocmd (unchanged, but
   careful with deprecated APIs).

### Where to put customizations

`nvim-lspconfig` automatically discovers config files under `lsp/` directories on
the runtimepath and merges them. So create:

```
lua/plugins/nvim-lspconfig.lua  (spec only — mason wiring + LspAttach)
lua/lsp/lua_ls.lua              (vim.lsp.config('lua_ls', {...}))
... one per customized server, OR a single lua/lsp/configure.lua
```

Keep this lightweight — many servers need **zero** customization with the new
default configs.

## Target `nvim-lspconfig.lua`

```lua
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
    -- 1. Server-specific customizations via built-in vim.lsp.config
    --    (ids are nvim-lspconfig names: lua_ls, phpactor, ts_ls, ...)
    vim.lsp.config('lua_ls', {
      settings = {
        Lua = {
          completion = { callSnippet = 'Replace' },
        },
      },
    })

    vim.lsp.config('emmet_ls', {
      filetypes = { 'html', 'php', 'javascriptreact', 'typescriptreact' },
      init_options = {
        includeLanguages = { php = 'php' },
        showAbbreviationSuggestions = true,
        showExpandedAbbreviation = 'always',
        showSuggestionsAsSnippets = false,
      },
    })

    -- ... (clangd, bashls, etc. — see full server map below)

    -- 2. LSP attach keymaps (unchanged pattern, port carefully)
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
        map('gD', vim.lsp.buf.declaration, '[G]oto [D]eclaration')

        -- hide inline virtual text (keep, or reconsider with 0.12 inlay hints)
        vim.diagnostic.config { virtual_text = false }

        local client = vim.lsp.get_client_by_id(event.data.client_id)
        if client and client:supports_method(vim.lsp.protocol.Methods.textDocument_inlayHint, event.buf) then
          map('<leader>th', function()
            vim.lsp.inlay_hint.enable(not vim.lsp.inlay_hint.is_enabled { bufnr = event.buf })
          end, '[T]oggle Inlay [H]ints')
        end
      end,
    })

    -- 3. Mason + tool installer (unchanged)
    require('mason').setup()

    local ensure_installed = {
      'lua_ls', 'phpactor', 'ts_ls', 'emmet_ls', 'somesass_ls', 'cssls',
      'tailwindcss', 'clangd', 'bashls', 'pyright', 'jsonls', 'taplo',
      -- formatters
      'stylua', 'shfmt', 'black', 'prettier', 'clang-format',
      -- linters
      'eslint_d', 'stylelint', 'shellcheck',
    }
    require('mason-tool-installer').setup { ensure_installed = ensure_installed }

    -- 4. Auto-enable installed servers (mason-lspconfig default behavior)
    require('mason-lspconfig').setup()
  end,
}
```

### Deprecation gotchas while porting the keymaps

- `documentHighlight` autocmds in the old config use `vim.lsp.buf.document_highlight`
  and `clear_references`. These still work, but note the **0.12 renames**:
  - `vim.lsp.semantic_tokens` `start()/stop()` → `enable()`. The old config doesn't
    call these directly (mason/lspconfig did), but if fidget or others surface
    deprecation warnings, this is the cause.
- `supports_method(vim.lsp.protocol.Methods.textDocument_documentHighlight, ...)`
  — still valid. Keep the document-highlight autocommand if you want it; the
  old config conditionally created it, so preserve that behavior if desired.

### Capabilities

The old config did:
```lua
local capabilities = vim.lsp.protocol.make_client_capabilities()
capabilities = vim.tbl_deep_extend('force', capabilities, require('cmp_nvim_lsp').default_capabilities())
```

With `vim.lsp.config`, you still need to extend capabilities for `cmp-nvim-lsp`.
The idiomatic way is to set it globally:

```lua
vim.lsp.config('*', {
  capabilities = require('cmp_nvim_lsp').default_capabilities(),
})
```

Add that inside `config = function()` before the server-specific configs. This
replaces the old per-server capability merge entirely.

## Full server customization map (port these settings)

| Server | Settings to preserve |
|--------|----------------------|
| `lua_ls` | `Lua.completion.callSnippet = 'Replace'` |
| `phpactor` | (none) |
| `ts_ls` | (none) |
| `emmet_ls` | filetypes + init_options (see above) |
| `somesass_ls` | (none) |
| `cssls` | (none) |
| `tailwindcss` | (none) |
| `clangd` | `capabilities.offsetEncoding = 'utf-8'` (fold into `vim.lsp.config('clangd', { capabilities = { offsetEncoding = 'utf-8' } })`) |
| `bashls` | `filetypes = { 'bash', 'sh', 'zsh' }` |
| `pyright` | (none) |
| `jsonls` | (none) |
| `taplo` | (none) |

> Confirm the server name `somesass_ls` is still valid — it looked like a
> redacted/odd value in inspection. If it was `somesass_ls`, keep it; if it was
> a placeholder, replace with the real server (likely `cssls`, `scss_ls`, or a
> sass server). Verify with `:Mason` list.

## conform.nvim (validate, minimal changes)

Current spec is already close to current API. Note `formatters_by_ft` and
`format_on_save` keys are current. Minimal changes:

- Add `format_on_save` if you want auto-format (the current config formats on
  `<leader>f` only). This is optional.
- Ensure `lua = { 'stylua' }` stays — stylua is installed via mason above.
- No 0.12 breakage in conform.

```lua
return {
  'stevearc/conform.nvim',
  keys = {
    { '<leader>f', function() require('conform').format { async = true, lsp_format = 'fallback' } end, mode = '', desc = '[F]ormat buffer' },
  },
  opts = {
    notify_on_error = false,
    formatters_by_ft = {
      lua = { 'stylua' },
      bash = { 'shfmt' },
      python = { 'black' },
      javascript = { 'prettier' },
      typescript = { 'prettier' },
      javascriptreact = { 'prettier' },
      typescriptreact = { 'prettier' },
      json = { 'prettier' },
      css = { 'prettier' },
      scss = { 'prettier' },
    },
    -- optional:
    -- format_on_save = { timeout_ms = 500, lsp_format = 'fallback' },
  },
}
```

## nvim-lint (validate)

Current spec is mostly fine. Check linter registry names still match
(`eslint_d`, `stylelint`, `shellcheck`). No 0.12 breakage. Optionally add a
`lint.linters_by_ft` entry for `python` if you want (e.g. ruff). Keep as-is
unless you want ruff.

## Acceptance checklist

- [ ] No usage of `require('lspconfig')[name].setup()` remains (`grep -rn "lspconfig']['" lua/` is empty).
- [ ] `vim.lsp.config('*', ...)` sets cmp capabilities globally.
- [ ] `:LspInfo` shows clients attaching correctly for each language.
- [ ] `gd`, `gr`, `<leader>rn`, `<leader>ca` still work.
- [ ] `:Mason` lists servers; installed servers `enable` automatically.
- [ ] `:checkhealth lspconfig` and `:checkhealth vim.lsp` pass.
- [ ] Formatters (`<leader>f`) and linters still run.