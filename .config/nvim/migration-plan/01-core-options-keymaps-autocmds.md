# Step 01 — Core options, keymaps, autocommands, init, lazy-config

Files touched:
- `init.lua`
- `lua/opts.lua`
- `lua/keymaps.lua`
- `lua/autocommands.lua`
- `lua/lazy-config.lua`

## 0.12 breaking changes that could touch this area

| Change | Impact on this config |
|--------|-----------------------|
| `vim.diff` renamed to `vim.text.diff` | Not used here, but note for future scripts. |
| `'shelltemp'` now defaults to `false` | No config change; just be aware. |
| Default `'statusline'` now renders `vim.diagnostic.status()` + progress | `mini.statusline` overrides it (step 07), so no effect. |
| `diagnostic-signs` can't be configured via `sign_define()` | This config never did that; no change. |
| `gr`/`grt`/`grx` now default LSP maps | Might collide with our `<leader>` maps; see keymaps note below. |

## 1. `init.lua`

Keep this file tiny and purely a bootstrap. Today it is already 4 `require` lines,
which is good. Two small improvements:

```lua
-- init.lua
require 'opts'
require 'keymaps'
require 'autocommands'
require 'lazy-config'
```

- No functional change required. Optionally add a guard so editor state configs
  run first. Leave as-is unless a step needs an extra require.

## 2. `lua/opts.lua`

Mostly correct for 0.12. Changes to make:

1. Add `vim.g.loaded_netrw = 1` / `vim.g.loaded_netrwPlugin = 1` **only if** you
   decide to rely fully on `neo-tree` (step 06). Otherwise skip.

2. Treesitter folds are currently set globally here:
   ```lua
   vim.opt.foldmethod = 'expr'
   vim.opt.foldexpr = 'v:lua.vim.treesitter.foldexpr()'
   ```
   With the nvim-treesitter rewrite (step 03), folding is enabled per-filetype
   (or via a `FileType` autocommand), not globally. **Move these fold lines out
   of `opts.lua`** and into a `FileType` autocmd (see step 03). Keeping them
   global can error on buffers with no treesitter parser.

3. `vim.o.winborder = 'rounded'` — this is still valid in 0.12 (0.12 even added
   a `"bold"` style). Keep it.

4. Optional 0.12 additions, enabled only if desired:
   ```lua
   -- completion popup border (new 0.12 'pumborder')
   vim.opt.pumblend = 10
   vim.opt.completeopt = 'menu,menuone,noinsert' -- confirm matches cmp below
   ```
   Note: `completeopt` is already set in `nvim-cmp.lua`; keep it in exactly one
   place. Prefer setting it in `opts.lua` and removing from cmp (step 05).

Everything else (`number`, `relativenumber`, `undofile`, `listchars`, `inccommand`,
`scrolloff`, `signcolumn`, etc.) is unchanged in 0.12.

## 3. `lua/keymaps.lua`

No 0.12 breaking changes here. Two notes:

- The `<leader>q` diagnostic setloclist map is fine. In 0.12, `vim.diagnostic.setloclist()`
  gained an optional `format` function — optional enhancement only.
- 0.12 ships default normal-mode `gr`, `grt`, `grx` LSP maps. This config maps
  `gd`, `gr`, `gI` in `LspAttach` (step 04), which is fine, but double-check
  there are no duplicate/conflicting `gr*` definitions across `keymaps.lua` and
  the LSP attach.

No edits strictly required.

## 4. `lua/autocommands.lua`

Only a `TextYankPost` highlight au exists. It is unaffected by 0.12. Leave it.

(Optional) Consider adding the shared augroup pattern used in this codebase:
```lua
local group = vim.api.nvim_create_augroup('user', { clear = true })
```
so future autocmds reuse one group.

## 5. `lua/lazy-config.lua`

This is the biggest cleanup in this step. Today it:

1. Bootstraps lazy.nvim (fine).
2. Maintains a manual `local lazy_plugins = { require 'plugins.X', ... }` list.
3. Passes that list to `lazy.setup`.

**Problem:** every new plugin file must be added to this list by hand, and it can
get out of sync. lazy.nvim supports folder-based import.

**Target end state:**

```lua
local lazypath = vim.fn.stdpath 'data' .. '/lazy/lazy.nvim'
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  local lazyrepo = 'https://github.com/folke/lazy.nvim.git'
  local out = vim.fn.system { 'git', 'clone', '--filter=blob:none', '--branch=stable', lazyrepo, lazypath }
  if vim.v.shell_error ~= 0 then
    error('Error cloning lazy.nvim:\n' .. out)
  end
end
vim.opt.rtp:prepend(lazypath)

require('lazy').setup {
  spec = {
    { import = 'plugins' },
  },
  checker = { enabled = true, notify = false },   -- optional: auto-check updates
  ui = {
    icons = vim.g.have_nerd_font and {} or {
      cmd = '⌘', config = '🛠', event = '📅', ft = '📂',
      init = '⚙', keys = '🗝', plugin = '🔌', runtime = '💻',
      require = '🌙', source = '📄', start = '🚀', task = '📌', lazy = '💤 ',
    },
  },
}
```

Notes:
- `{ import = 'plugins' }` recursively loads every file under `lua/plugins/`.
- The `my-nvim-theme.lua` file returns a **table of specs** (not a single spec),
  which is why the old code did the unusual `require('plugins.my-nvim-theme').catppuccin`.
  If you switch to `import = 'plugins'`, `lazy` will see a module that returns a
  table where each key is a spec — **this will not auto-register**.
  Fix in step 08: convert `my-nvim-theme.lua` to return a **list** of specs, or
  split it into one file per theme. Do not switch to `import = 'plugins'` until
  step 08 is done (or keep the explicit `require` list for the theme file only).

**Interim target (safe):** keep the explicit list, but drop the redundancy by
importing the folder and only special-casing the theme module. The plan order
matters — finishing step 08 before the `import` switch avoids breakage.

## Acceptance checklist

- [ ] `:Lazy` shows all plugins discovered with no "missing spec" errors.
- [ ] `nvim --headless "+Lazy! sync" +qa` exits 0.
- [ ] Startup is not slower than before (check `:Lazy profile`).
- [ ] Treesitter folds no longer error in non-parser buffers (after step 03).