# Step 08 — Themes, which-key, todo-comments, misc, copilot

Files touched:
- `lua/plugins/my-nvim-theme.lua`  (restructure — see note)
- `lua/plugins/which-key.lua`      (v3 icon/spec schema)
- `lua/plugins/todo-comments.lua`  (validate)
- `lua/plugins/vim-sleuth.lua`     (no change)
- `lua/plugins/lazydev.lua`        (validate)
- `lua/plugins/luvit-meta.lua`     (no change)
- `lua/plugins/copilot.lua`        (validate)

## 1. Themes (`my-nvim-theme.lua`) — restructure required

### Problem A: the spec returns a table, not a list

`lazy.nvim`'s folder `import` expects each module to return a **list of specs**
(or a single spec). `my-nvim-theme.lua` returns a **map**:

```lua
return {
  github_theme = { ... },
  catppuccin   = { ... },
  tokyo_night  = { ... },
  rose_pine    = { ... },
}
```

This is why `lazy-config.lua` had to do the unusual
`require('plugins.my-nvim-theme').catppuccin`. This blocks the `import = 'plugins'`
cleanup in step 01.

### Problem B: only one theme is actually active

`lazy-config.lua` requires only `.catppuccin`, so the other three themes are
**dead config** (defined but never registered). All four have `lazy = false` +
`priority = 1000` and each calls `vim.cmd 'colorscheme ...'` — if they were all
registered they'd fight over the colorscheme.

### Problem C: misspelled plugin name

The catppuccin spec has `name = 'catpuccin'` (missing an `p`). `lazy-lock.json`
accordingly has key `"catpuccin"`. This works but is a latent hazard.

### Recommendation

Pick ONE active theme and put it in its own file `lua/plugins/colorscheme.lua`
(returning a single spec). Delete the other dead theme specs. This unblocks the
folder `import`.

```lua
-- lua/plugins/colorscheme.lua  (e.g. catppuccin)
return {
  'catppuccin/nvim',
  name = 'catppuccin',
  lazy = false,
  priority = 1000,
  config = function()
    require('catppuccin').setup {
      flavour = 'mocha',             -- auto|latte|frappe|macchiato|mocha
      transparent_background = true,
      float = { transparent = true },
      auto_integrations = true,
    }
    vim.cmd.colorscheme 'catppuccin'
  end,
}
```

> catppuccin v2 kept `flavour`, `transparent_background`, `float`, and
> `auto_integrations`. The old `float.solid = true` was dropped/renamed — confirm
> against the installed version. `vim.cmd.colorscheme` (function form) is
> preferred over `vim.cmd 'colorscheme ...'`.

If you instead want to keep **multiple installable themes** with easy switching
(via a helper), split each into its own file under `plugins/themes/*.lua` and add
a small command to pick one — but the simplest, most maintainable path is **one
active theme**.

### Correct map for the other three themes (if you keep them as separate files)

- `github-nvim-theme`: `github_dark_default` is current (not deprecated — the
  2023-12 changelog reimplemented the `*_default` variants). `options.transparent = true`
  is valid.
- `tokyonight`: `transparent = true` is valid (`style = 'night'` fine).
- `rose-pine`: `styles.transparency = true` is valid (its README default shows
  `transparency = false` under `styles`).

## 2. which-key.nvim (v3 schema drift)

Current `which-key.lua` uses v2-era icons:

```lua
icons = {
  mappings = vim.g.have_nerd_font,
  keys = vim.g.have_nerd_font and {} or { Up = '<Up> ', ... },
},
```

which-key v3 **removed `icons.keys`** in favor of `replace.key` (key-label
formatting) and `icons.rules` (icon assignment). The `icons.mappings` toggle
still exists. Update to:

```lua
opts = {
  preset = 'classic',          -- or 'modern' / 'helix'
  icons = {
    mappings = vim.g.have_nerd_font,
    -- (optional) rules = { ... },
  },
  spec = {
    { '<leader>c', group = '[C]ode', mode = { 'n', 'x' } },
    { '<leader>d', group = '[D]ocument' },
    { '<leader>r', group = '[R]ename' },
    { '<leader>s', group = '[S]earch' },
    { '<leader>w', group = '[W]orkspace' },
    { '<leader>t', group = '[T]oggle' },
    { '<leader>h', group = 'Git [H]unk', mode = { 'n', 'v' } },
    { '<leader>a', group = "Abhishek's Keymaps", mode = { 'n', 'v' }, icon = { icon = '' } },
  },
}
```

Notes:
- `event = 'VimEnter'` in the current spec is fine, but the README now recommends
  `event = 'VeryLazy'`. Either works; `VeryLazy` defers until after other plugins.
- The `spec`/`group` shape (`{ '<leader>c', group = ..., mode = ... }`) is still
  valid in v3. No change needed there.
- To keep your custom key labels when NOT using a Nerd Font, configure
  `replace.key` with the old table content instead of `icons.keys`.
- `delay`, `expand`, `sort`, `win`, `layout` are all new/default options; you only
  need to override what you want. Your current config only customizes `icons` and
  `spec`, so just drop `icons.keys`.

## 3. todo-comments.nvim

Current spec:
```lua
{ 'folke/todo-comments.nvim', event = 'VimEnter', dependencies = { 'nvim-lua/plenary.nvim' }, opts = { signs = false } }
```

todo-comments is current; `signs` option still exists (default `true`). Since you
already show gitsigns signs, `signs = false` for todo is a reasonable choice.
No change required. Optional: add `highlight = { ... }` or `keywords` customization
if desired.

## 4. vim-sleuth

`{ 'tpope/vim-sleuth' }` — no change; it implicitly detects indentation. Keep.
(Consider disabling treesitter **indent** (step 03) so vim-sleuth stays the
indentation authority.)

## 5. lazydev (validate)

Current:
```lua
{ 'folke/lazydev.nvim', ft = 'lua', opts = { library = { { path = 'luvit-meta/library', words = { 'vim%.uv' } } } } }
```

lazydev supports Neovim 0.12's `vim.uv`/`vim.async` natively now; the `luvit-meta`
library entry was a workaround for older versions. It is harmless to keep, but
verify against the installed lazydev docs whether the explicit `luvit-meta`
mapping is still needed. Keep `luvit-meta` only if other tooling relies on it.

## 6. copilot (validate)

`github/copilot.vim` — current. `vim.g.copilot_no_tab_map = true` + `Copilot disable`
at startup is a privacy-first setup; keep. The `<C-Y>` accept mapping is standard.
No 0.12 breakage. Optional: the plugin still supports `vim.cmd 'Copilot disable'`.
Leave as-is unless you want to switch to the newer `copilot.lua` rewrite (out of scope).

## Acceptance checklist

- [ ] `my-nvim-theme.lua` is replaced by a single `colorscheme.lua` (one active theme).
- [ ] `lazy-lock.json` key corrected to `"catppuccin"` (after `:Lazy sync`).
- [ ] The other three dead theme specs are removed or split into optional files.
- [ ] `lazy-config.lua` no longer does `require(...).catppuccin` (folder import works, step 01).
- [ ] which-key popup renders; no `icons.keys` warning; groups appear for `<leader>c/d/r/s/w/t/h/a`.
- [ ] `:checkhealth todo-comments` OK; `:checkhealth which-key` OK.
- [ ] Copilot disabled on startup, `<C-Y>` accepts, `<leader>ace`/`<leader>acd` work.
- [ ] `:checkhealth lazydev` OK; Lua completion still provides `vim.*`/`vim.uv` docs.