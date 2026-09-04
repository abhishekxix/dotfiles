-- Single source of truth for languages/tools we care about in Neovim.
-- Exports `language_config` (the spec list) plus getter functions that
-- derive filetypes, parsers, servers, formatters, linters, and the
-- conform/nvim-lint by-ft mappings from it.

local M = {}

---@class langs.Spec
---@field ft? string|string[] Neovim filetype(s); omit if not a standalone filetype.
---@field parser? string treesitter parser name; omit if no parser to install.
---@field servers? string[] LSP server names installed via mason-tool-installer.
---@field formatters? string[] formatter names installed via mason, used by conform.nvim.
---@field linters? string[] linter names installed via mason, used by nvim-lint.

--- Per-language spec list. Add a language/tool by adding an entry here.
---@type langs.Spec[]
M.language_config = {
  {
    ft = { 'bash', 'sh', 'zsh' },
    parser = 'bash',
    servers = { 'bashls' },
    formatters = { 'shfmt' },
    linters = { 'shellcheck' },
  },
  {
    ft = 'c',
    parser = 'c',
    servers = { 'clangd' },
    formatters = { 'clang-format' },
  },
  {
    ft = 'cpp',
    parser = 'cpp',
    servers = { 'clangd' },
    formatters = { 'clang-format' },
  },
  {
    ft = 'css',
    parser = 'css',
    servers = { 'cssls' },
    formatters = { 'prettier' },
    linters = { 'stylelint' },
  },
  { ft = 'diff', parser = 'diff' },
  { ft = 'html', parser = 'html' },
  {
    ft = 'javascript',
    parser = 'javascript',
    servers = { 'ts_ls' },
    formatters = { 'prettier' },
    linters = { 'eslint_d' },
  },
  {
    ft = 'json',
    parser = 'json',
    servers = { 'jsonls' },
    formatters = { 'prettier' },
  },
  {
    ft = 'lua',
    parser = 'lua',
    servers = { 'lua_ls' },
    formatters = { 'stylua' },
  },
  { ft = 'markdown', parser = 'markdown' },
  {
    ft = 'php',
    parser = 'php',
    servers = { 'phpactor' },
  },
  {
    ft = 'python',
    parser = 'python',
    servers = { 'pyright' },
    formatters = { 'black' },
  },
  {
    ft = 'scss',
    parser = 'scss',
    servers = { 'somesass_ls' },
    formatters = { 'prettier' },
    linters = { 'stylelint' },
  },
  {
    ft = 'toml',
    parser = 'toml',
    servers = { 'taplo' },
  },
  {
    ft = 'typescriptreact',
    parser = 'tsx',
    servers = { 'ts_ls' },
    formatters = { 'prettier' },
    linters = { 'eslint_d' },
  },
  {
    ft = { 'yaml', 'yaml.docker-compose' },
    parser = 'yaml',
    servers = { 'yamlls' },
    formatters = { 'prettier' },
  },
  -- JSX filetype. No `parser` because the `javascriptreact` filetype
  -- is handled by the `javascript` parser (installed by the entry above).
  {
    ft = 'javascriptreact',
    servers = { 'ts_ls' },
    formatters = { 'prettier' },
    linters = { 'eslint_d' },
  },
  {
    ft = 'typescript',
    parser = 'typescript',
    servers = { 'ts_ls' },
    formatters = { 'prettier' },
    linters = { 'eslint_d' },
  },
  { ft = 'vim', parser = 'vim' },

  -- Auxiliary treesitter parsers (no standalone filetype).
  { parser = 'jsdoc' },
  { parser = 'luadoc' },
  { parser = 'markdown_inline' },
  { parser = 'query' },
  { parser = 'vimdoc' },

  -- Server-only entries (no filetype or parser of their own).
  { servers = { 'emmet_ls' } },
  { servers = { 'tailwindcss' } },
  -- Dockerfile / Docker Compose. Only `dockerfile` has a treesitter
  -- parser; `yaml.docker-compose` needs `yaml` installed first (not yet
  -- listed in a parser entry), so omit its ft to avoid an autocmd error.
  {
    ft = 'dockerfile',
    parser = 'dockerfile',
    servers = { 'docker_language_server' },
  },
}

-- Derived getters -----------------------------------------------------------

--- Return a new list with duplicates removed, preserving first-seen order.
local function dedup(list)
  local seen = {}
  local result = {}
  for _, item in ipairs(list) do
    if not seen[item] then
      seen[item] = true
      table.insert(result, item)
    end
  end
  return result
end

--- Collect all filetypes declared across specs (deduped).
---@return string[]
function M.get_filetypes()
  local result = {}
  for _, spec in ipairs(M.language_config) do
    local ft = spec.ft
    if ft then
      local fts = type(ft) == 'table' and ft or { ft }
      for _, f in ipairs(fts) do
        table.insert(result, f)
      end
    end
  end
  return dedup(result)
end

--- Collect all treesitter parsers declared across specs (deduped).
---@return string[]
function M.get_parsers()
  local result = {}
  for _, spec in ipairs(M.language_config) do
    if spec.parser then
      table.insert(result, spec.parser)
    end
  end
  return dedup(result)
end

--- Collect all LSP servers declared across specs (deduped).
---@return string[]
function M.get_servers()
  local result = {}
  for _, spec in ipairs(M.language_config) do
    for _, server in ipairs(spec.servers or {}) do
      table.insert(result, server)
    end
  end
  return dedup(result)
end

--- Collect all formatter tools declared across specs (deduped).
---@return string[]
function M.get_formatters()
  local result = {}
  for _, spec in ipairs(M.language_config) do
    for _, formatter in ipairs(spec.formatters or {}) do
      table.insert(result, formatter)
    end
  end
  return dedup(result)
end

--- Collect all linter tools declared across specs (deduped).
---@return string[]
function M.get_linters()
  local result = {}
  for _, spec in ipairs(M.language_config) do
    for _, linter in ipairs(spec.linters or {}) do
      table.insert(result, linter)
    end
  end
  return dedup(result)
end

--- Build the conform.nvim `formatters_by_ft` table from specs.
---@return table<string, string[]>
function M.get_formatters_by_ft()
  local result = {}
  for _, spec in ipairs(M.language_config) do
    local ft = spec.ft
    if ft and spec.formatters and #spec.formatters > 0 then
      local fts = type(ft) == 'table' and ft or { ft }
      for _, f in ipairs(fts) do
        result[f] = spec.formatters
      end
    end
  end
  return result
end

--- Build the nvim-lint `linters_by_ft` table from specs.
---@return table<string, string[]>
function M.get_linters_by_ft()
  local result = {}
  for _, spec in ipairs(M.language_config) do
    local ft = spec.ft
    if ft and spec.linters and #spec.linters > 0 then
      local fts = type(ft) == 'table' and ft or { ft }
      for _, f in ipairs(fts) do
        result[f] = spec.linters
      end
    end
  end
  return result
end

return M
