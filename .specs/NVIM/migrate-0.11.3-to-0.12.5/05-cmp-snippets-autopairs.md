# Step 05 — nvim-cmp, LuaSnip, nvim-autopairs

Files touched:
- `lua/plugins/nvim-cmp.lua`     (minor updates + note `lazydev` source requirement)
- `lua/plugins/lazydev.lua`      (ensure loaded before cmp — it is the `lazydev` source)
- `lua/plugins/autopairs.lua`    (validate API)
- `lua/opts.lua`                 (single source of truth for `completeopt`)

## No breaking changes from 0.12, but a few cleanups

nvim-cmp is unaffected by the 0.12 core changes, but this section has drifted from
the README and has one subtle coupling.

## 1. `completeopt` — single source of truth

Currently `completeopt` is set in `nvim-cmp.lua`:
```lua
completion = { completeopt = 'menu,menuone,noinsert' },
```

Recommendation: move it to `opts.lua` and let cmp read the option. Either is valid,
but only ONE should set it (setting via cmp and via `vim.opt` can conflict/duplicate).
0.12 adds `'pumborder'` and `'completeopt'` `"nearest"` flag — optional enrichment if you want:

```lua
vim.opt.completeopt = 'menu,menuone,noinsert'
```

Leave the cmp `completion` table for other settings only.

## 2. LuaSnip setup

Current:
```lua
local luasnip = require 'luasnip'
luasnip.config.setup {}
```

This is fine but redundant (LuaSnip auto-configures). You can remove
`luasnip.config.setup {}` and just `require 'luasnip'` for the mappings. No harm
keeping it, but modern LuaSnip uses `lua_ls` square-root config via `lazydev`.

## 3. The `lazydev` source requires `lazydev.nvim`

`nvim-cmp.lua` lists:
```lua
sources = {
  { name = 'lazydev', group_index = 0 },
  { name = 'nvim_lsp' },
  { name = 'luasnip' },
  { name = 'path' },
}
```

The `lazydev` source is provided by `folke/lazydev.nvim`, which your config loads
with `ft = 'lua'`. This means the `lazydev` completion source is only active for
Lua files — which is correct and intended (lazydev is Lua-API completion). Keep it.

But note: `lazydev` must be **loaded** before nvim-cmp sources are evaluated.
Current `lazydev.lua` uses `ft = 'lua'`, so it lazy-loads on first Lua buffer.
That's fine because cmp source lookups are lazy. No change needed, but verify
`<C-l>`/`<C-h>` snippet jump maps don't clash after step 01 (they are `i`/`s` mode).

## 4. nvim-autopairs API

Current:
```lua
require('nvim-autopairs').setup {}
local cmp_autopairs = require 'nvim-autopairs.completion.cmp'
local cmp = require 'cmp'
cmp.event:on('confirm_done', cmp_autopairs.on_confirm_done())
```

This is still the current API. Minor: ensure `cmp` is available at config time —
since `config` runs when the plugin loads (event `InsertEnter`) and nvim-cmp also
loads on `InsertEnter`, ordering is race-prone. Safer to use lazy.nvim dependency
ordering: in `autopairs.lua`, the `dependencies = { 'hrsh7th/nvim-cmp' }` is
already present. Recommend wrapping the confirm_done wiring so it only runs when
cmp module exists:

```lua
config = function()
  require('nvim-autopairs').setup {}
  local ok, cmp = pcall(require, 'cmp')
  if ok then
    local cmp_autopairs = require 'nvim-autopairs.completion.cmp'
    cmp.event:on('confirm_done', cmp_autopairs.on_confirm_done())
  end
end,
```

## 5. Optional modern enrichment (not required)

- **Native snippet engine**: 0.10+ supports `vim.snippet.expand`. You could drop
  LuaSnip in favor of native snippets, but LuaSnip is more powerful and already
  configured. **Keep LuaSnip** unless you want to simplify.
- **`blink.cmp`** is a popular newer alternative to nvim-cmp; not a drop-in. Out
  of scope — stick with nvim-cmp for this migration.

## Target `nvim-cmp.lua` (normalized)

```lua
return {
  'hrsh7th/nvim-cmp',
  event = 'InsertEnter',
  dependencies = {
    {
      'L3MON4D3/LuaSnip',
      build = (function()
        if vim.fn.has 'win32' == 1 or vim.fn.executable 'make' == 0 then
          return
        end
        return 'make install_jsregexp'
      end)(),
    },
    'saadparwaiz1/cmp_luasnip',
    'hrsh7th/cmp-nvim-lsp',
    'hrsh7th/cmp-path',
  },
  config = function()
    local cmp = require 'cmp'
    local luasnip = require 'luasnip'

    cmp.setup {
      snippet = {
        expand = function(args)
          luasnip.lsp_expand(args.body)
        end,
      },
      mapping = cmp.mapping.preset.insert {
        ['<C-b>'] = cmp.mapping.scroll_docs(-4),
        ['<C-f>'] = cmp.mapping.scroll_docs(4),
        ['<CR>'] = cmp.mapping.confirm { select = true },
        ['<Tab>'] = cmp.mapping.select_next_item(),
        ['<S-Tab>'] = cmp.mapping.select_prev_item(),
        ['<C-Space>'] = cmp.mapping.complete {},  -- replaces '<C-_>' (see note)
        ['<C-l>'] = cmp.mapping(function()
          if luasnip.expand_or_locally_jumpable() then
            luasnip.expand_or_jump()
          end
        end, { 'i', 's' }),
        ['<C-h>'] = cmp.mapping(function()
          if luasnip.locally_jumpable(-1) then
            luasnip.jump(-1)
          end
        end, { 'i', 's' }),
      },
      sources = {
        { name = 'lazydev', group_index = 0 },
        { name = 'nvim_lsp' },
        { name = 'luasnip' },
        { name = 'path' },
      },
    }
  end,
}
```

**Note on `<C-_>`**: `<C-_>` is a non-portable key. The README uses `<C-Space>`
for `complete()`. Either work on most terminals, but `<C-Space>` is more
consistent. Change only if your terminal sends `<C-Space>` reliably; otherwise
keep `<C-_>`.

## Acceptance checklist

- [ ] Autocompletion appears in `.lua` (with `lazydev` source) and `.py`/`.ts`.
- [ ] `<Tab>`/`<S-Tab>` cycle, `<CR>` confirms, `<C-b>`/`<C-f>` scroll docs.
- [ ] `<C-l>`/`<C-h>` jump snippet placeholders in LuaSnip snippets.
- [ ] Auto-pairing `()[]{}""''` works, and selecting a function inserts `(`.
- [ ] `completeopt` is set in exactly one place.
- [ ] No "lazydev source not found" startup warning.