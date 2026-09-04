# Robustness & Optimization Pass for `.config/nvim`

| Field | Value |
|---|---|
| Status | Done |
| Component | NVIM |
| Created | 2026-09-04 |

## Goal

Harden the Neovim config against silent failures and trim startup cost, with no
loss of functionality. Two robustness fixes (explicit LSP enable, pcall-guarded
treesitter start) close real failure modes; the remaining steps remove dead
config, add a missing language, and lazy-load plugins that currently start at
load time.

## Decisions (confirmed with user)

| Step | Decision |
|---|---|
| 01 | Keep both (additive): explicit `vim.lsp.enable()` + `mason-lspconfig` `automatic_enable` stays default. |
| 02 | Notify at `ERROR` level (not WARN) when `vim.treesitter.start()` fails. |
| 03 | yaml + `yaml.docker-compose` filetypes, parser `yaml`, server `yamlls`, formatter `prettier`. |
| 04 | Originally removed the `float` option as "invalid"; **reverted after user testing** — the option does work (affects float/panel transparency in catppuccin). Restored in a follow-up commit. |
| 05 | Lazy-load `nvim-ts-autotag` + `vim-sleuth` only. **`copilot.vim` stays eager** (no change). |
| 06 | Dropped — no `opts.lua` polish. |

## Context & Research

The config was reviewed top-to-bottom after the `migrate-0.11.3-to-0.12.5` spec
landed. It is well-structured (single source of truth in `langs.lua`, modern
0.12 APIs, one plugin per file). The issues below are real but narrow.

1. **LSP enable is implicit and Mason-only.**
   `lua/plugins/nvim-lspconfig.lua` calls `mason-lspconfig.setup()` and relies
   on its default `automatic_enable = true`. That default only calls
   `vim.lsp.enable()` for packages installed *via Mason*
   (`automatic_enable.lua` iterates `registry.get_installed_package_names()`).
   A server installed system-wide (system `clangd`, a Homebrew `lua-language-server`,
   etc.) is **never enabled**, so the LSP silently does not start for that
   language. Making the enable list explicit removes this footgun and makes the
   config reproducible without Mason.
   Ref: `~/.local/share/nvim/lazy/mason-lspconfig.nvim/lua/mason-lspconfig/features/automatic_enable.lua`

2. **`vim.treesitter.start()` is called unconditionally in a FileType autocmd.**
   `lua/autocommands.lua` registers a `FileType` autocmd whose pattern is
   `langs.get_filetypes()` and whose callback calls `vim.treesitter.start()`
   with no guard. `get_filetypes()` includes every spec with an `ft` field —
   including `javascriptreact`, which has **no `parser`** of its own (it relies
   on the `javascript` parser via Neovim's default ft→parser fallback). That
   fallback works today, but if any filetype in the list ever lacks both a parser
   entry and a default fallback, `start()` raises on every file of that type and
   the user sees an error flash on open. A `pcall` guard makes the failure
   logged once at `ERROR` level instead of fatal.

3. **`langs.lua` has no `yaml` entry**, yet the `dockerfile` spec comment
   references `yaml.docker-compose`. Docker Compose YAML currently gets no
   treesitter highlighting and no LSP. Adding a `yaml` spec (parser `yaml`,
   server `yamlls`, formatter `prettier`, covering both `yaml` and
   `yaml.docker-compose` filetypes) closes the gap and makes the docker-compose
   comment true.

4. **`colorscheme.lua` passes `float = { transparent = true }` to catppuccin.**
   This is not a valid catppuccin option (the real key is `transparent_background`,
   which is already set). It is silently ignored — dead config that misleads
   readers into thinking float transparency is configured.

5. **Two plugins load at startup unnecessarily.**
   - `nvim-ts-autotag` has no `event`.
   - `vim-sleuth` has no `event`.
   Lazy-loading these on `InsertEnter` / `BufReadPre` trims startup time without
   changing behavior. (`copilot.vim` is intentionally left eager per user
   decision — see Non-goals.)

## Non-goals

- Do **not** add new plugins (e.g. `blink.cmp`, `mini.files`).
- Do **not** prune plugins or replace them with 0.12 built-ins.
- Do **not** change keybindings, the `langs.lua` spec schema, or the
  `lazy-config.lua` recursive import.
- Do **not** lazy-load `copilot.vim` — it stays eager.
- Do **not** add `opts.lua` polish (shortmess / jumpoptions) — dropped.
- Do **not** regenerate `lazy-lock.json` as part of this spec — it is regenerated
  by `:Lazy sync` after plugin-spec edits and committed separately if needed.

## Steps

Each step maps to exactly one commit, named `NVIM(<NN>): <summary>`.

| # | File | Area |
|---|------|------|
| 00 | `00-overview.md` | This overview |
| 01 | `01-explicit-lsp-enable.md` | `lua/plugins/nvim-lspconfig.lua` |
| 02 | `02-pcall-treesitter-start.md` | `lua/autocommands.lua` |
| 03 | `03-add-yaml-language.md` | `lua/langs.lua` |
| 04 | `04-remove-dead-catppuccin-option.md` | `lua/plugins/colorscheme.lua` |
| 05 | `05-lazy-load-startup-plugins.md` | `nvim-ts-autotag.lua`, `vim-sleuth.lua` |

## Status checklist

- [ ] 01 — Explicit LSP enable
- [ ] 02 — pcall-guard treesitter start
- [ ] 03 — Add `yaml` language spec
- [ ] 04 — Remove dead catppuccin `float` option
- [ ] 05 — Lazy-load `nvim-ts-autotag` + `vim-sleuth`

## Risks & Rollback

- **Explicit `vim.lsp.enable` (step 01):** if a server name in `langs.get_servers()`
  has no `lsp/<name>.lua` on the runtimepath, `vim.lsp.enable` logs a warning
  but does not error. Risk is low; the names already match `mason-lspconfig`'s
  mapping. Rollback: `git revert` the commit; `automatic_enable` still works.
- **pcall-guard (step 02):** if a parser genuinely should exist but fails to
  load, the failure is now an `ERROR` notification (visible) rather than a fatal
  traceback. Mitigation: the notify is scheduled and fires once per open.
- **yaml addition (step 03):** requires `yaml` parser + `yamlls` to install via
  Mason on next launch; until then YAML files have no LSP (same as today).
- **Lazy-loading (step 05):** `nvim-ts-autotag` loads on `InsertEnter`,
  `vim-sleuth` on `BufReadPre`. `copilot.vim` is unchanged (stays eager).

Each step is its own commit, so `git revert` or `git bisect` localizes any
regression.
