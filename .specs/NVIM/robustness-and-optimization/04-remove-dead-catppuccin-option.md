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

## Outcome: REVERTED

**Post-implementation finding:** The user tested the removal and confirmed the
`float = { transparent = true }` option **does work** — it affects
float/panel transparency in catppuccin (visible on `:Lazy`, telescope dropdowns,
etc.). The original assessment that it was "silently ignored" was wrong.

The option was restored in a follow-up commit
(`NVIM: restore catppuccin float transparency option`). Step 04 is effectively
a no-op in the final state; the `float` block remains in `colorscheme.lua`.

## Acceptance

- [x] `:colorscheme catppuccin` applies without error (with `float` restored).
- [x] Floating windows render with the transparent background — confirmed by user.
- [x] No new warnings from catppuccin on startup.
