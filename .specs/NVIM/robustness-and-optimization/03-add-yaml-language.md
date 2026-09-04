# 03 — Add `yaml` language spec

| Field | Value |
|---|---|
| Status | Planning |
| Step | 03 |
| Commit | `NVIM(03): add yaml language (parser + yamlls)` |

## Files

- `lua/langs.lua` (EDIT)

## Changes

`langs.lua` has no `yaml` entry, yet the `dockerfile` spec comment references
`yaml.docker-compose`. Docker Compose YAML currently gets no treesitter
highlighting and no LSP. Add a `yaml` spec so the comment becomes true and
Docker Compose / general YAML files get highlighting + completion.

Insert a new entry in `M.language_config` (alphabetical-ish, near `toml`):

```lua
{
  ft = { 'yaml', 'yaml.docker-compose' },
  parser = 'yaml',
  servers = { 'yamlls' },
  formatters = { 'prettier' },
},
```

The `yaml.docker-compose` filetype is set by Neovim's built-in filetype
detection for `compose*.yaml` / `docker-compose*.yaml` files, so both plain
YAML and Docker Compose files get highlighting, completion, and formatting.

No changes needed to `conform.lua` / `lint.lua` / `nvim-treesitter.lua` /
`nvim-lspconfig.lua` — they all derive from `langs.lua` getters, so the new
parser/server/formatter are picked up automatically. `mason-tool-installer`
will install `yamlls` + `prettier` (prettier is already installed for other
languages, so this is a no-op) on next launch, and `nvim-treesitter.install()`
will install the `yaml` parser.

## Acceptance

- [ ] `:lua print(vim.inspect(require('langs').get_servers()))` includes `yamlls`.
- [ ] `:lua print(vim.inspect(require('langs').get_parsers()))` includes `yaml`.
- [ ] After `:Lazy sync` + restart, opening a `compose.yaml` file attaches
  `yamlls` (`:lua print(vim.lsp.get_clients({bufnr=0}))` non-empty) and the
  buffer has treesitter highlighting (`:lua print(vim.treesitter.get_parser(0))`
  is non-nil).
- [ ] `:lua print(vim.inspect(require('langs').get_formatters_by_ft()['yaml']))`
  includes `prettier`; `:ConformInfo` in a `compose.yaml` shows prettier as the
  formatter.
- [ ] `dockerfile` filetype still works (no regression from the new entry).
