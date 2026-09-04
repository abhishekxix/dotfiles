# Migration Plan: Neovim 0.11.3 → 0.12.5

| Field | Value |
|---|---|
| Status | Done |
| Component | NVIM |
| Created | 2026-09-04 |

## Goal

Modernize the [ADDRESS] config from **0.11.3** to **0.12.5** with no loss of
functionality: every plugin and keybinding still works, and deprecated APIs are
replaced with their 0.12-native equivalents.

## Execution notes

- **Do not modify files while they are being migrated in a live session.**
  Each step should be done as its own commit so you can bisect if something
  breaks.
- After each step, run `:checkhealth <plugin>` inside Neovim and confirm the
  plugin loads without errors (`:Lazy` → check no red/error lines).
- Test plan: after each step, open a representative file for every filetype you
  use, and confirm highlighting, completion, linting, and formatting still work.

## Suggested order

| # | File | Area |
|---|------|------|
| 00 | `00-overview-and-readme.md` | This overview |
| 01 | `01-core-options-keymaps-autocmds.md` | `opts.lua`, `keymaps.lua`, `autocommands.lua`, `init.lua`, `lazy-config.lua` |
| 02 | `02-gitsigns.md` | `gitsigns` (merge the two duplicate files) |
| 03 | `03-treesitter-and-autotag.md` | `nvim-treesitter`, `nvim-ts-autotag` (major rewrite) |
| 04 | `04-lsp-and-mason.md` | `nvim-lspconfig`, `mason`, `conform`, `lint`, `fidget` |
| 05 | `05-cmp-snippets-autopairs.md` | `nvim-cmp`, LuaSnip, `nvim-autopairs` |
| 06 | `06-telescope-neo-tree.md` | `telescope`, `neo-tree` |
| 07 | `07-mini.md` | `mini.nvim` (`mini.ai`, `mini.surround`, `mini.statusline`, etc.) |
| 08 | `08-themes-misc-copilot.md` | themes, `which-key`, `todo-comments`, `vim-sleuth`, `copilot` |

## Status checklist

- [x] 01 — Core options, keymaps, autocommands, init, lazy-config
- [x] 02 — gitsigns (merge duplicates, modernize API)
- [x] 03 — nvim-treesitter rewrite + nvim-ts-autotag
- [x] 04 — LSP + mason + conform + lint
- [x] 05 — nvim-cmp + LuaSnip + nvim-autopairs
- [x] 06 — telescope + neo-tree
- [x] 07 — mini.nvim
- [x] 08 — themes + which-key + todo-comments + misc + copilot

## Non-goals

- Do **not** drop plugins in favor of native 0.12 replacements (built-in
  completion, `vim.snippet`, `LspProgress`, etc.). Keeping all current plugins is
  intentional — this is a like-for-like migration, not a plugin-pruning pass.
- Do **not** adopt new plugins (e.g. `blink.cmp`, `mini.files`) as part of this
  spec. Scope is strictly 0.11.3 → 0.12.5 compatibility.

## Context & Research

1. **Neovim 0.12 removes/changes several APIs the config relies on.**
   Full details in each step file, but highlights:
   - `vim.diff` → renamed to `vim.text.diff`.
   - `vim.diagnostic.disable()` / `is_disabled()` removed.
   - `diagnostic-signs` can no longer be configured via `sign_define()`.
   - `vim.lsp.semantic_tokens` `start()/stop()` → renamed to `enable()`.
   - `get_parser()` now returns `nil` instead of throwing.
   - `'shelltemp'` now defaults to `false`.

2. **`nvim-treesitter` has been fully rewritten.** The old `opts = { ensure_installed, highlight, indent }`
   lazy.nvim pattern is **gone** and **no longer works** on the `main` branch.
   The whole config must be re-done. (Covered in step 03.)

3. **`nvim-lspconfig` legacy `require('lspconfig').setup()` is deprecated.**
   The modern approach is `vim.lsp.config()` + `vim.lsp.enable()` (Nvim 0.11+),
   with `mason-lspconfig` auto-enabling servers. (Covered in step 04.)

4. **Two gitsigns specs exist** (`git-signs.lua` and `gitsigns.lua`). Both load
   the same plugin and fight over `opts`. Must be merged. (Covered in step 02.)

5. **`mini.statusline` and other mini modules are fine and current** — no
   deprecation — but the config predates some newer `mini.*` modules and can be
   tidied. (Covered in step 07.)

6. **`which-key.nvim` v3** changed its icon/option schema (`icons.mappings`,
   `icons.keys`, `spec` shape, `preset`, `delay`, `expand`). The current icons
   config in `which-key.lua` uses the old-style `icons.keys` table. (Covered in step 08.)

## Current config inventory

```
.config/nvim/
├── init.lua                  # requires opts, keymaps, autocommands, lazy-config
├── lazy-lock.json
├── .stylua.toml
├── .gitignore
└── lua/
    ├── opts.lua
    ├── keymaps.lua
    ├── autocommands.lua
    ├── lazy-config.lua       # hardcoded plugin require list
    └── plugins/
        ├── autopairs.lua
        ├── conform.lua
        ├── copilot.lua
        ├── git-signs.lua     # <-- DUPLICATE, merge into gitsigns
        ├── gitsigns.lua
        ├── lazydev.lua
        ├── lint.lua
        ├── luvit-meta.lua
        ├── mini.lua
        ├── my-nvim-theme.lua
        ├── neo-tree.lua
        ├── nvim-cmp.lua
        ├── nvim-lspconfig.lua
        ├── nvim-treesitter.lua
        ├── nvim-ts-autotag.lua
        ├── telescope.lua
        ├── todo-comments.lua
        ├── vim-sleuth.lua
        └── which-key.lua
```

## How the files map to this plan

- The `plugins/` file names are the canonical units of work. Each plan file
  names the exact source file(s) to edit and the target end state.
- `lazy-config.lua` currently enumerates every plugin via an explicit
  `require 'plugins.X'` list. This is redundant with lazy.nvim's own
  auto-discovery of `plugins/` and adds a maintenance burden. Step 01 proposes
  simplifying to a folder-based spec so new plugin files are picked up
  automatically.