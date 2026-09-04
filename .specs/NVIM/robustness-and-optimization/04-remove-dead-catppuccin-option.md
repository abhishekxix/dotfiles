# 04 — Remove dead catppuccin `float` option

| Field | Value |
|---|---|
| Status | Planning |
| Step | 04 |
| Commit | `NVIM(04): drop invalid catppuccin float option` |

## Files

- `lua/plugins/colorscheme.lua` (EDIT)

## Changes

`colorscheme.lua` passes `float = { transparent = true }` to `catppuccin.setup`.
This is not a valid catppuccin option — the real key is `transparent_background`
(which is already set to `true`). The `float` key is silently ignored and
misleads readers into thinking float transparency is configured separately.

Remove the `float` block:

```lua
require('catppuccin').setup {
  flavour = 'mocha',
  transparent_background = true,
  auto_integrations = true,
}
```

No behavior change (the option was already ignored). Float transparency is
governed by `transparent_background = true` plus Neovim's `winblend` /
per-window highlight groups.

## Acceptance

- [ ] `:colorscheme catppuccin` still applies without error.
- [ ] Floating windows (e.g. `:Lazy`, telescope dropdown) still render with the
  transparent background as before — visually identical to pre-change.
- [ ] No new warnings from catppuccin on startup (`:messages` clean).
