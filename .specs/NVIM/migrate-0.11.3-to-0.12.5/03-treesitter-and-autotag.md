# Step 03 — nvim-treesitter (MAJOR rewrite) + nvim-ts-autotag

Files touched:
- `lua/plugins/nvim-treesitter.lua`  (REWRITE — old schema is obsolete)
- `lua/plugins/nvim-ts-autotag.lua`   (verify against current plugin API)
- `lua/opts.lua`                      (remove global fold settings — see step 01)

## ⚠️ The big one

`nvim-treesitter` on the `main` branch is a **full, incompatible rewrite**. The
author states: *"Treat this as a different plugin you need to set up from
scratch."*

Your current spec uses the OLD pattern that no longer exists:

```lua
return {
  'nvim-treesitter/nvim-treesitter',
  build = ':TSUpdate',
  main = 'nvim-treesitter',
  opts = {
    ensure_installed = { ... },
    auto_install = true,
    highlight = { enable = true, additional_vim_regex_highlighting = { 'ruby' } },
    indent = { enable = true, disable = { 'ruby' } },
  },
}
```

**None of `opts.highlight`, `opts.indent`, `opts.ensure_installed`, `opts.auto_install`
work anymore.** This is not a deprecation; it's a different API.

## New model

The rewritten plugin:
1. Installs/keeps parsers (functions: `require('nvim-treesitter').install { ... }`).
2. Ships queries for highlighting/folds/indent/injections/locals.
3. Does **NOT** auto-enable any feature. Highlighting/folding/indentation are now
   enabled via **Neovim core** treesitter APIs per-filetype.

### Requirements (new)

- Neovim 0.12.0+ ✓ (you're on 0.12.5)
- `tar` + `curl` in PATH
- `tree-sitter-cli` 0.26.1+ installed via a package manager (**not npm**)
- A C compiler in PATH

Check before migrating:
```bash
which tar curl tree-sitter cc
tree-sitter --version   # must be >= 0.26.1
```

## New spec

```lua
return {
  'nvim-treesitter/nvim-treesitter',
  lazy = false,            -- plugin does NOT support lazy-loading
  build = ':TSUpdate',
  config = function()
    require('nvim-treesitter').setup {
      install_dir = vim.fn.stdpath 'data' .. '/site',
    }
    -- Install parsers (async). `:wait()` for bootstrap sync if desired.
    require('nvim-treesitter').install {
      'bash', 'c', 'cpp', 'css', 'diff', 'html', 'javascript', 'jsdoc',
      'json', 'lua', 'luadoc', 'markdown', 'markdown_inline', 'php',
      'python', 'query', 'scss', 'toml', 'tsx', 'typescript', 'vim', 'vimdoc',
    }
  end,
}
```

Notes:
- `lazy = false` is mandatory (plugin explicitly doesn't support lazy-loading).
- Parsers can also be bootstrapped synchronously: `require('nvim-treesitter').install({...}):wait(300000)`.

## Enabling features per-filetype

The plugin no longer flips `highlight`/`indent` globals. You enable core features
yourself. Recommended: move tree-sitter feature enablement into a single
`FileType` autocommand.

Create (or add to) a config such as `lua/autocommands.lua` or a dedicated
`lua/treesitter.lua`:

```lua
-- Folding (replaces the global opts.lua fold settings)
vim.api.nvim_create_autocmd('FileType', {
  callback = function()
    -- enable folding
    vim.wo.foldexpr = 'v:lua.vim.treesitter.foldexpr()'
    vim.wo.foldmethod = 'expr'
    -- optional: keep folds open by default
    -- vim.wo.foldlevel = 99
  end,
})

-- Highlighting: enable for all filetypes that have a parser
vim.api.nvim_create_autocmd('FileType', {
  callback = function(args)
    if require('nvim-treesitter').is_enabled(args.buf) then
      vim.treesitter.start(args.buf)
    end
  end,
})
```

> Wait to confirm exact helper names against the installed plugin (`:h nvim-treesitter`,
> and tab-complete `require('nvim-treesitter').`). The key point is: highlight +
> fold are now driven by `vim.treesitter.*` (core), not plugin `opts`.

### Indentation (experimental, optional)

Treesitter indentation is now **experimental** and off by default. Enable per-filetype:

```lua
vim.bo.indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
```

Enable only for filetypes you trust (it can be glitchy). Consider keeping
`vim-sleuth` for indentation and skipping this.

## Important `opts.lua` cleanup

Because folds are now filetype-scoped, REMOVE these from `opts.lua` (also noted in step 01):

```lua
vim.opt.foldmethod = 'expr'
vim.opt.foldexpr = 'v:lua.vim.treesitter.foldexpr()'
vim.opt.foldtext = ''
vim.opt.foldlevel = 99
vim.opt.foldlevelstart = 4
vim.opt.foldnestmax = 8
```

Keep the fold-level defaults you care about; set them in the `FileType` autocmd
instead (or set safe global defaults like `foldlevelstart = 99`, `foldnestmax = 10`
as pure vim options without the `expr` method).

## 0.12 core changes affecting treesitter

- `vim.treesitter.get_parser()` now returns `nil` on failure instead of throwing.
  Guard calls accordingly.
- The `ft-query-plugin` no longer enables `query.lint()` by default — no action.
- `Query:iter_matches()` `"all"` option removed — only matters if you hand-write queries.
- `vim.diff` → `vim.text.diff` — unrelated to this plugin but relevant if any snippet uses diffing.

## nvim-ts-autotag

Current spec:
```lua
return {
  'windwp/nvim-ts-autotag',
  config = function() require('nvim-ts-autotag').setup() end,
}
```

- `nvim-ts-autotag` still works, but note it depends on the treesitter HTML/JSX
  parsers being installed (they are, above).
- Confirm the plugin still receives updates. Given the treesitter rewrite, test
  autotag closing/renaming in `.html`/`.jsx`/`.tsx` after migration. If it
  misbehaves, note that newer alternatives (e.g. cookie-pairs handled by other
  plugins) can replace it, but keep it first and validate.

## Migration sequence (do in this order)

1. Install `tree-sitter-cli` >= 0.26.1 via your system package manager.
2. Replace `nvim-treesitter.lua` with the new spec.
3. Remove the global fold lines from `opts.lua`.
4. Add the `FileType` autocommands for fold + highlight.
5. Restart nvim, run `:TSUpdate` (or let build run), then `:checkhealth nvim-treesitter`.
6. Verify `:TSInstall` no longer needed — parsers auto-installed by `install {}`.
7. Test each filetype (`.lua`, `.py`, `.tsx`, `.php`, `.html`, `.sh`, `.json`, `.toml`).

## Acceptance checklist

- [ ] `:checkhealth nvim-treesitter` reports parsers installed, no missing `tree-sitter` CLI.
- [ ] Highlighting works on a fresh `.lua` file.
- [ ] Folding works (`zm`/`zr`) on a `.py` and `.tsx` file.
- [ ] No startup error referencing removed fields (`ensure_installed`, `highlight`, `indent`).
- [ ] Autotag closes/renames tags in `.html` and `.tsx`.
- [ ] `opts.lua` no longer sets `foldmethod = 'expr'` globally.