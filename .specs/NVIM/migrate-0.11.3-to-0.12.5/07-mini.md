# Step 07 — mini.nvim

Files touched:
- `lua/plugins/mini.lua`  (update repo URL + statusline override API)

## ⚠️ Repository moved

`echasnovski/mini.nvim` was transferred to a dedicated organization and is now
canonically **`nvim-mini/mini.nvim`**. The old URL still resolves via redirect,
but update the spec to the new org for long-term correctness.

```lua
'echasnovski/mini.nvim'  →  'nvim-mini/mini.nvim'
```

## Modules in use (all still current)

The config enables these modules, none are deprecated:

| Module | Purpose | Status |
|--------|---------|--------|
| `mini.ai` | `a`/`i` textobjects | current; `n_lines` option valid |
| `mini.surround` | brackets/quotes surround | current; `mappings` table valid |
| `mini.indentscope` | indent guides | current |
| `mini.move` | move lines | current |
| `mini.statusline` | statusline | current, but override API changed |

Verify each module's `setup()` is still correct (they are).

## ⚠️ `mini.statusline` override API changed

The OLD config does this, which no longer matches the current API:

```lua
local statusline = require 'mini.statusline'
statusline.setup { use_icons = vim.g.have_nerd_font }

---@diagnostic disable-next-line: duplicate-set-field
statusline.section_location = function()
  return '%2l:%-2v'
end
```

The modern API computes sections via `MiniStatusline.section_*` functions and
customizes output by setting `content.active` / `content.inactive` to a function
that composes them. `use_icons` remains valid.

**If you just want the default statusline**, drop the `section_location` override
entirely:

```lua
require('mini.statusline').setup { use_icons = vim.g.have_nerd_font }
```

**If you want LINE:COLUMN at the end**, replace the override with a custom
`content.active` function that reuses the built-in sections and swaps the location
section:

```lua
require('mini.statusline').setup {
  use_icons = vim.g.have_nerd_font,
  content = {
    active = function()
      local mode, mode_hl = MiniStatusline.section_mode { trunc_width = 120 }
      local git         = MiniStatusline.section_git { trunc_width = 40 }
      local diff        = MiniStatusline.section_diff { trunc_width = 75 }
      local diagnostics = MiniStatusline.section_diagnostics { trunc_width = 75 }
      local lsp         = MiniStatusline.section_lsp { trunc_width = 75 }
      local filename    = MiniStatusline.section_filename { trunc_width = 140 }
      local fileinfo    = MiniStatusline.section_fileinfo { trunc_width = 120 }
      local location    = '%2l:%-2v' -- custom LINE:COLUMN
      local search      = MiniStatusline.section_searchcount { trunc_width = 75 }

      -- Compose left/center/right using MiniStatusline.combine_groups
      -- (verify exact helper name in :h mini.statusline)
      return MiniStatusline.combine_groups {
        { hl = mode_hl,                  strings = { mode } },
        { hl = 'MiniStatuslineDevinfo',  strings = { git, diff, diagnostics, lsp } },
        '%<', -- Mark general truncate point
        { hl = 'MiniStatuslineFilename', strings = { filename } },
        '%=', -- End left alignment
        { hl = 'MiniStatuslineFileinfo', strings = { fileinfo } },
        { hl = mode_hl,                  strings = { location, search } },
      }
    end,
  },
}
```

> The exact `combine_groups` / highlight-group names must be confirmed against
> `:h mini.statusline` (`MiniStatusline-example-content`) for your installed
> version. The key takeaway: **the `section_location = function()` override is
> gone**; customize via `content.active` instead.

## Target `mini.lua` (normalized)

```lua
return {
  'nvim-mini/mini.nvim',
  version = false,           -- or 'stable' if you prefer tagged releases
  config = function()
    require('mini.ai').setup { n_lines = 500 }

    require('mini.surround').setup {
      mappings = {
        add = '<leader>asa',
        delete = '<leader>asd',
        find = '<leader>asf',
        find_left = '<leader>asF',
        highlight = '<leader>ash',
        replace = '<leader>asr',
      },
    }

    require('mini.indentscope').setup()
    require('mini.move').setup()

    require('mini.statusline').setup {
      use_icons = vim.g.have_nerd_font,
      -- optionally add custom `content.active` here
    }
  end,
}
```

## Notes on newer modules (optional, do NOT block migration)

- `mini.icons` is now the recommended icon provider; `mini.statusline` and
  `which-key` can consume it. If you adopt `mini.icons`, it can replace
  `nvim-web-devicons` usage (but keep `nvim-web-devicons` if other plugins need it).
- `mini.files` and `mini.pick` are newer favorites that could replace `neo-tree`
  and `telescope` respectively. **Out of scope** — keep your current choices.

## Acceptance checklist

- [ ] Spec uses `nvim-mini/mini.nvim`.
- [ ] Statusline renders (mode, filename, fileinfo, location).
- [ ] If custom LINE:COLUMN is desired, it appears (validated via `:h mini.statusline`).
- [ ] `mini.ai` (`va)`, `ci'`), `mini.surround` (`<leader>asa`), `mini.move`,
      `mini.indentscope` all still function.
- [ ] No deprecation warning from `section_location` override.