# 05 — Lazy-load startup plugins

| Field | Value |
|---|---|
| Status | Planning |
| Step | 05 |
| Commit | `NVIM(05): lazy-load ts-autotag and vim-sleuth` |

## Files

- `lua/plugins/nvim-ts-autotag.lua` (EDIT)
- `lua/plugins/vim-sleuth.lua` (EDIT)

## Changes

Two plugins currently load at startup with no `event`/`cmd`/`keys` trigger,
adding to startup time without benefit. (`copilot.vim` is intentionally left
eager — see Non-goals.)

### `nvim-ts-autotag`

Add `event = 'InsertEnter'` — autotag only matters while typing.

```lua
return {
  'windwp/nvim-ts-autotag',
  event = 'InsertEnter',
  config = function()
    require('nvim-ts-autotag').setup()
  end,
}
```

### `vim-sleuth`

`vim-sleuth` adjusts buffer-local indent options on `BufReadPre`. Load it on
`BufReadPre` so it is present before the buffer is read:

```lua
return {
  'tpope/vim-sleuth',
  event = 'BufReadPre',
}
```

## Non-goals

- Do **not** lazy-load `copilot.vim`. It stays eager. The user explicitly chose
  to keep it loading at startup; the `<leader>tc` toggle and disabled-by-default
  behavior are unchanged.

## Acceptance

- [ ] `:Lazy profile` shows `nvim-ts-autotag` and `vim-sleuth` are **not** in
  the "loaded at startup" list; they appear under their respective `event`
  triggers.
- [ ] `copilot.vim` still appears in the "loaded at startup" list (unchanged).
- [ ] Startup time (`nvim --startuptime /tmp/st.txt` or `:Lazy profile`)
  decreases or stays flat (no regression).
- [ ] Open an HTML/JSX file, enter insert mode, type `<div>` — autotag still
  closes the tag.
- [ ] Open a file with a `.editorconfig` — `vim-sleuth` still adjusts
  `shiftwidth`/`expandtab` correctly (`:set shiftwidth?` reflects the file).
