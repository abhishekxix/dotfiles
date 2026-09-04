# 01 — Explicit LSP enable

| Field | Value |
|---|---|
| Status | Planning |
| Step | 01 |
| Commit | `NVIM(01): enable LSP servers explicitly, not only via Mason` |

## Files

- `lua/plugins/nvim-lspconfig.lua` (EDIT)

## Changes

Today the config relies on `mason-lspconfig`'s default `automatic_enable = true`,
which only calls `vim.lsp.enable()` for servers installed *via Mason*. A
system-installed server (system `clangd`, Homebrew `lua-language-server`, etc.)
is never enabled and the LSP silently does not start.

After `mason-lspconfig.setup()`, add an explicit enable of every server declared
in `langs.get_servers()`:

```lua
-- Enable every declared server. mason-lspconfig's automatic_enable only
-- covers servers installed via Mason; this also covers system-installed
-- servers and makes the config reproducible without Mason.
require('mason-lspconfig').setup()
vim.lsp.enable(langs.get_servers())
```

Keep `automatic_enable` at its default (do not set it to `false`) so that
servers installed later via `:Mason` still auto-start; the explicit `enable` is
additive and idempotent.

## Acceptance

- [ ] `:lua print(vim.inspect(vim.lsp.config))` shows entries for every name in
  `langs.get_servers()` after startup.
- [ ] With Mason's package for a server *uninstalled* but the system binary on
  `$PATH` (e.g. `clangd`), opening a C file still attaches the LSP
  (`:lua print(vim.lsp.get_clients({bufnr=0}))` is non-empty).
- [ ] `:checkhealth lspconfig` shows no errors.
- [ ] No regression for Mason-installed servers: open a Lua file and confirm
  `lua_ls` attaches.
