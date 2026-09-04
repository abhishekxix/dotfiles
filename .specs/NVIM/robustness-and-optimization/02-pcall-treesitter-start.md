# 02 — pcall-guard treesitter start

| Field | Value |
|---|---|
| Status | Planning |
| Step | 02 |
| Commit | `NVIM(02): guard treesitter start() with pcall` |

## Files

- `lua/autocommands.lua` (EDIT)

## Changes

The `FileType` autocmd in `autocommands.lua` calls `vim.treesitter.start()`
unconditionally for every filetype in `langs.get_filetypes()`. The list includes
filetypes like `javascriptreact` that have no `parser` of their own and rely on
Neovim's default ft→parser fallback. If any filetype in the list ever lacks both
a parser entry and a default fallback, `start()` raises on every open of that
filetype.

Wrap the `start()` call in a `pcall` and notify (once per filetype) on failure
so the error is discoverable but not fatal:

```lua
callback = function(args)
  local ok, err = pcall(vim.treesitter.start)
  if not ok then
    vim.schedule(function()
      vim.notify(
        ('treesitter: no parser for %s: %s'):format(args.match, err),
        vim.log.levels.ERROR
      )
    end)
  end
  vim.wo.foldexpr = 'v:lua.vim.treesitter.foldexpr()'
  vim.wo.foldmethod = 'expr'
end,
```

Notes:
- `args.match` is the matched filetype (the autocmd uses `pattern = get_filetypes()`,
  so `args.match` is the filetype string).
- Set `foldexpr`/`foldmethod` regardless — folds are cheap and harmless even
  without a parser; if a parser is missing the foldexpr simply yields no folds.
- Use `vim.schedule` for the notify so it does not interrupt the FileType
  autocmd chain. Notify at `ERROR` level so missing-parser issues are caught
  immediately rather than hidden.

## Acceptance

- [ ] Open a `javascriptreact` file (e.g. a `.jsx` file) — no error flash,
  highlighting works via the `javascript` parser fallback.
- [ ] Temporarily add a bogus filetype to `langs.get_filetypes()` (or open a
  filetype with no installed parser) and confirm a single `ERROR` notification
  appears instead of an error traceback, and the buffer still opens.
- [ ] Folds still work on a `lua` file (`zc`/`zo` behave).
