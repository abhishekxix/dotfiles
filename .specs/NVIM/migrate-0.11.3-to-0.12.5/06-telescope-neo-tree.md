# Step 06 — telescope & neo-tree

Files touched:
- `lua/plugins/telescope.lua`   (minor updates)
- `lua/plugins/neo-tree.lua`    (v3 migration — verify opts schema)

## telescope.nvim

### Current state vs. current requirements

- telescope now requires **Neovim >= 0.11.7** (you're on 0.12.5 ✓).
- Recommended to pin with `version = '*'` (stable release). Your spec doesn't pin;
  it follows `master`. Consider adding `version = '*'` for stability.

### Notes on the current spec

1. `find_files = { hidden = 'true' }` — `hidden` should be a boolean, not the
   string `'true'`. Fix to `hidden = true`.
2. `live_grep.additional_args` returns `{ '--hidden' }` — fine. (Optional: use
   `vim.fn.systemlist`-style, but current works for ripgrep.)
3. `file_ignore_patterns = { '^.git/' }` in `defaults` — fine.
4. `telescope-fzf-native` build via `make` with a `cond` guard — fine; keep.
5. `extensions.ui-select` via `get_dropdown()` — fine.

### No 0.12 breaking changes for telescope

telescope is unaffected by the 0.12 core renames. Only cosmetic/API drift above.

### Target `telescope.lua` (normalized)

```lua
return {
  'nvim-telescope/telescope.nvim',
  version = '*',
  event = 'VimEnter',
  dependencies = {
    'nvim-lua/plenary.nvim',
    {
      'nvim-telescope/telescope-fzf-native.nvim',
      build = 'make',
      cond = function()
        return vim.fn.executable 'make' == 1
      end,
    },
    { 'nvim-telescope/telescope-ui-select.nvim' },
    { 'nvim-tree/nvim-web-devicons', enabled = vim.g.have_nerd_font },
  },
  config = function()
    require('telescope').setup {
      extensions = {
        ['ui-select'] = { require('telescope.themes').get_dropdown() },
      },
      defaults = {
        file_ignore_patterns = { '^.git/' },
      },
      pickers = {
        buffers = {
          mappings = {
            i = { ['<C-d>'] = 'delete_buffer' },
            n = { ['dd'] = 'delete_buffer' },
          },
          initial_mode = 'normal',
        },
        find_files = { hidden = true },
        diagnostics = { initial_mode = 'normal' },
        live_grep = {
          additional_args = function()
            return { '--hidden' }
          end,
        },
      },
    }

    pcall(require('telescope').load_extension, 'fzf')
    pcall(require('telescope').load_extension, 'ui-select')

    -- ... keep all existing keymap definitions unchanged ...
  end,
}
```

Keep every existing `vim.keymap.set` exactly as-is (all `<leader>s*`, `<leader>/`,
`<leader><leader>`, etc.). They are unaffected.

## neo-tree.nvim

### ⚠️ Version 3.0 is a new major with breaking changes

- Neo-tree is now on **v3.x** (the `v3.x` branch / 3.0 tags).
- Your current spec uses `version = '*'` which resolves to the **latest tagged
  release** — that may now be 2.x or 3.x depending on tagging. The config's
  `opts` table uses the v2-era schema.
- The project's philosophy: breaking changes only land in new branches; the 3.0
  changelog lists deprecations.

### Decide: stay on 2.x or migrate to 3.x

**Option A (low-effort, recommended first): pin to 2.x** by using a compat branch/tag
so your current `opts` keep working unchanged:

```lua
return {
  'nvim-neo-tree/neo-tree.nvim',
  branch = 'v2.x',          -- or version = '2.*'
  ...
}
```

**Option B (modernize): migrate to v3.x** and update the config schema. This is
the "modernize" path. Key things to verify against the [3.0 changelog](https://github.com/nvim-neo-tree/neo-tree.nvim/wiki/Changelog#30):

1. **Spec pinning** — use `branch = 'v3.x'` (or `version = vim.version.range('3')`).
2. **`opts.window`** — `window.position = 'right'` is still valid in v3, but
   confirm the object shape. (`window.width`, `window.popup`, etc. exist.)
3. **`filesystem.filtered_items`** — the v3 canonical config uses
   `filtered_items = { hide_dotfiles = ..., hide_gitignored = ..., visible = ... }`.
   Confirm `visible = true` is still supported; in v3 there's also
   `always_show_by_pattern` and `never_show_by_pattern`.
4. **`filesystem.follow_current_file`** — v3 reworked "follow current file".
   Replace any 2.x `follow_current_file` tables with
   `filesystem = { follow_current_file = { enabled = true } }` shape (verify).
5. **Mappings** — v3 may have changed default mapping names for window actions.
   Your custom `['\\'] = 'close_window'` and `keys` map `\\` → `:Neotree reveal<CR>`
   should still work, but confirm the command form. v3 recommends
   `:Neotree source=filesystem reveal=true position=right` style, or use the
   `toggle` command.

### Recommended target `neo-tree.lua` (v3, normalized)

```lua
return {
  'nvim-neo-tree/neo-tree.nvim',
  branch = 'v3.x',
  dependencies = {
    'nvim-lua/plenary.nvim',
    'MunifTanjim/nui.nvim',
    'nvim-tree/nvim-web-devicons', -- optional but recommended
  },
  lazy = false,
  keys = {
    { '\\', ':Neotree reveal<CR>', desc = 'NeoTree reveal', silent = true },
  },
  opts = {
    window = {
      position = 'right',
    },
    filesystem = {
      follow_current_file = { enabled = true },
      use_libuv_file_watcher = true,
      filtered_items = {
        hide_dotfiles = false,
        hide_gitignored = false,
        visible = true,
      },
      window = {
        mappings = {
          ['\\'] = 'close_window',
        },
      },
    },
  },
}
```

> Verify `use_libuv_file_watcher` and `follow_current_file.enabled` are valid in
> your installed v3 version via `:h neo-tree-filesystem` (`:checkhealth neo-tree`).

### Migration sequence

1. Roughly pin the current spec to `v2.x` to ensure a working baseline before
   touching anything else (avoids 3.0 breakage mid-migration).
2. Later (or in a dedicated commit) switch to `v3.x` and update opts per the
   changelog, verifying each key via `:help`.
3. Toggle: test `\\` opens, `\\` closes, reveal follows the current file.

## Acceptance checklist

- [ ] telescope: `:Telescope find_files` shows hidden files, no `'true'` string bug.
- [ ] telescope: `:Telescope live_grep` searches hidden files.
- [ ] `<leader>/` fuzzy search in buffer works.
- [ ] neo-tree: `\\` toggles tree on the right and reveals current file.
- [ ] neo-tree: no startup error about unknown `opts` keys (`:checkhealth neo-tree`).
- [ ] Decide pinned v2.x vs v3.x and document the choice in the plan.