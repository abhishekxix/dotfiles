# Nvim Editing Workflow

| Field | Value |
|---|---|
| Status | Approved |
| Component | NVIM |
| Created | 2026-09-09 |

## Goal

Close the highest-friction gaps in the daily Neovim editing loop — saving,
buffer management, diagnostic navigation, completion, and formatting — plus two
real subagent-found bugs (clangd capabilities wipe, LspDetach augroup leak).
Follow-up slices (lazy-loading, neo-tree, treesitter guards, autocmd polish)
land as separate specs/PRs on the epic.

## Context & Research

A 5-agent parallel audit (2026-09-09, `general-purpose` + Muse Spark model —
see session notes: `Explore` type hardcodes a nonexistent Opus model on this
OpenRouter setup) produced 28 nvim findings. The slice below is the
highest-payoff, lowest-risk subset: keymaps that don't exist yet, one-line
behavior fixes, and two correctness bugs. Lazy-loading changes
(telescope/todo-comments `VimEnter`, opencode/copilot eager) are deliberately
deferred — they change startup timing and deserve their own test cycle.

Key facts informing the plan:

1. **`clangd` capabilities wipe** (`lua/plugins/nvim-lspconfig.lua:40`):
   `vim.lsp.config('clangd', { capabilities = { offsetEncoding = 'utf-8' } })`
   *replaces* the `'*'` fallback set at line 14
   (`cmp_nvim_lsp.default_capabilities()`), because `vim.lsp.config` merges the
   named config over `'*'` — the nested `capabilities` table is replaced
   wholesale, not deep-merged at the leaf. Result: clangd loses snippet /
   completion-item-kind capabilities. Fix: merge explicitly
   (`vim.tbl_deep_extend`) or set `offsetEncoding` without touching the rest.
2. **LspDetach augroup leak** (`nvim-lspconfig.lua:87`): the `LspDetach`
   autocmd is created with `clear = true` *inside* the `LspAttach` callback,
   so every new attach wipes detach handlers registered by earlier attaches.
   Fix: create the detach augroup once, outside the callback.
3. **`vim.diagnostic.config` in LspAttach** (line 71): global effect
   (`virtual_text = false`) triggered per-buffer. Fix: call once at config
   time, not per attach.
4. **`<CR>` confirm + `<Tab>` select-next** (`nvim-cmp.lua:34-36`): with
   `select = true`, `<CR>` accepts the top item even when the user typed a
   newline intentionally; `<Tab>` as select-next removes Tab-indent in
   completion context. Standard fix: `select = false` on confirm and
   Tab/S-Tab that falls back when the menu is invisible.
5. **conform `keys.mode = ''`** (`conform.lua:3`): binds `<leader>f` in *all*
   modes including insert and operator-pending. Should be `n`/`x` (or `v`).

## Non-goals

- Do **not** lazy-load telescope, todo-comments, opencode, copilot, or mini
  (separate startup-perf spec).
- Do **not** add new plugins (bufferline, flash, cmp-buffer is borderline —
  decided below as step 04 since it's a source flag, not a plugin).
- Do **not** change `<C-h/j/k/l>` window moves, the `<leader>p` clipboard
  scheme, mini.surround mappings, or opencode `<C-a>` (muscle-memory calls
  needing explicit user decisions — flagged for a keymap-review spec).
- Do **not** touch `langs.lua` schema, `lazy-config.lua`, or `lazy-lock.json`
  beyond what `:Mason`/`:Lazy sync` regenerates.
- Do **not** add neo-tree `follow_current_file`, treesitter guards, or new
  autocmds (separate specs).

## Steps

Each step maps to exactly one commit, named `NVIM(<NN>): <summary>`.

### 01 — Core editing keymaps

- **Files:** `lua/keymaps.lua` (EDIT)
- **Changes:** add save (`<leader>w`, `<C-s>` in n/i/v), buffer delete
  (`<leader>bd`, `<leader>x`), diagnostic jumps (`[d`/`]d`), quickfix nav
  (`[q`/`]q`). Keep kickstart desc-style (`[W]rite`, `[B]uffer [D]elete`).
- **Test:** `nvim --headless -c 'verbose map <leader>w' -c 'verbose map [d' -c 'qa!'`
- **Acceptance:**
  - [ ] each new lhs resolves to the intended rhs, no collisions with existing maps

### 02 — Fix clangd capabilities wipe

- **Files:** `lua/plugins/nvim-lspconfig.lua` (EDIT)
- **Changes:** preserve `cmp_nvim_lsp` capabilities on clangd while keeping
  `offsetEncoding = 'utf-8'` (merge, don't replace).
- **Test:** `nvim --headless -c 'lua ...'` print resolved clangd config; confirm snippet support present alongside offsetEncoding
- **Acceptance:**
  - [ ] resolved clangd capabilities contain both cmp defaults and utf-8 offsetEncoding

### 03 — LspAttach/LspDetach cleanup

- **Files:** `lua/plugins/nvim-lspconfig.lua` (EDIT)
- **Changes:** hoist `vim.diagnostic.config { virtual_text = false }` to
  one-time config scope; create the `LspDetach` augroup once outside the
  attach callback.
- **Test:** open two LSP buffers, close one, confirm document-highlight cleared on the other; `:autocmd LspDetach` shows a single group
- **Acceptance:**
  - [ ] no per-attach global side effects; detach handlers survive multiple attaches

### 04 — cmp buffer source + saner confirm

- **Files:** `lua/plugins/nvim-cmp.lua` (EDIT)
- **Changes:** add `buffer` source after `nvim_lsp`; confirm uses
  `select = false`; Tab/S-Tab fall back when menu invisible.
- **Test:** manual: type partial word in prose buffer, confirm buffer-word suggestion appears; `<CR>` on empty menu inserts newline
- **Acceptance:**
  - [ ] buffer words complete; `<CR>` never inserts an uninvited item

### 05 — conform scope + format-on-save toggle

- **Files:** `lua/plugins/conform.lua` (EDIT)
- **Changes:** restrict `<leader>f` to normal/visual modes; add
  `format_on_save` default-off with a `<leader>tf` toggle (pattern matches
  existing `<leader>t*` toggles in gitsigns/copilot).
- **Test:** `:map <leader>f` shows n/x only; toggle flips behavior and persists per session
- **Acceptance:**
  - [ ] no insert-mode binding; toggle on formats on save, toggle off doesn't

## Risks & Rollback

- **Keymap collisions (step 01):** `[d`/`]d`/`[q`/`]q` are conventionally free
  but verify against plugin maps (gitsigns owns `[c`/`]c`). Rollback: `git
  revert` the commit.
- **clangd merge (step 02):** if the merge helper is wrong, clangd may fail to
  start — visible immediately on opening a C/C++ file. Rollback: revert; old
  behavior (degraded completions) returns.
- **cmp confirm `select = false` (step 04):** changes muscle memory — `<CR>`
  no longer accepts the top item; users must `<C-y>`/`<Tab>` first. This is
  the standard upstream recommendation but flag it in the PR body.
- **format_on_save default-off (step 05):** zero behavior change until toggled.

Each step is its own commit, so `git revert` or `git bisect` localizes any
regression.
