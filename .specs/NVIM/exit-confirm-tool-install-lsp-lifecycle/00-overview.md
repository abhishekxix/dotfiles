# GH-28: Neovim Exit Confirm, Tool Install, LSP Lifecycle

| Field | Value |
|---|---|
| Status | Approved |
| Component | NVIM |
| Created | 2026-09-14 |
| GH issue | GH-28 (`NVIM: exit confirm, tool install, LSP lifecycle`) |
| Verification notes | None |

> GH-28 is part 3/8 of the PR #25 split. PR #25 was closed unmerged; its spec
> (`.specs/CONFIG/config-qol-updates/`, steps 05–07) no longer exists in the
> tree. This spec re-derives the GH-28 scope from the issue body plus the three
> original commit diffs (fetched via `gh api` from the closed PR: `72447a1`
> for exit confirm, `263e75f` for tool install, `dbeddaa` for LSP lifecycle),
> verified against the current tree on 2026-09-14.
>
> After approval, the Goal, Context, Non-goals, step text, acceptance text, and
> Risks are frozen; changes need re-approval. Status, checkbox state, and
> Verification notes remain mutable. Keep that implementation bookkeeping
> uncommitted until the user approves a final `SPECS` commit.

## Goal

Make quitting with unsaved changes safe (`confirm`), make Mason/treesitter
tool installation diagnosable instead of silently broken, and fix LSP attach
lifecycle bugs (per-buffer highlight refcount, eager Telescope loads, clangd
capability wipe).

## Context & Research

Key facts, verified against the tree on 2026-09-14:

1. **No exit confirm** (`lua/opts.lua` has no `confirm`): `:q` on a dirty
   buffer fails with E37 instead of offering save/discard/cancel. The
   original `72447a1` adds `vim.o.confirm = true` with no other change.
2. **Mason double-setup risk** (`lua/plugins/nvim-lspconfig.lua:108`):
   `require('mason').setup()` is called once today, but nothing says so —
   a second call silently re-initializes. Original `263e75f` annotates the
   single call site; the new `test_mason_setup_exactly_once` test pins it.
3. **Silent Mason reconciliation**: `mason-tool-installer.setup
   { ensure_installed }` with defaults reconciles noisily on every startup
   (original calls this "noisy automatic reconciliation"; the fix pins it to
   `run_on_start = true, debounce_hours = 24`) and offers no manual trigger.
   Original adds `MasonToolsInstallNow` user command calling
   `check_install(false)` for an immediate manual run. (The issue body
   mentions a "failed-tool report" but the fetched diff contains no such
   reporting code — spec'd as-is, no invented behavior.)
4. **Parser install errors without a compiler** (`lua/plugins/nvim-treesitter.lua`):
   `install(get_parsers())` runs unconditionally; on a box with neither
   `tree-sitter` CLI nor `cc`, every parser fails with one error each.
   Original guards with an `executable` check for both and returns early with
   one actionable WARN diagnostic.
5. **Treesitter alias/filetype mismatch** (`lua/autocommands.lua:31`):
   the FileType callback calls `pcall(vim.treesitter.start)` with no buffer
   or language, sets folds even on failure, and notifies at ERROR with the
   raw error string. Filetypes `zsh`, `yaml.docker-compose`,
   `javascriptreact`/`typescriptreact` have no same-named parser
   (`langs.lua` documents the javascriptreact→javascript sharing). Original
   adds a `parser_aliases` table (zsh→bash, yaml.docker-compose→yaml,
   javascriptreact→javascript, typescriptreact→tsx), resolves via
   `language.get_lang`, pre-checks with `language.add`, skips folds on both
   failure paths, and downgrades the notify to WARN with an actionable
   `:TSUpdate` hint.
6. **`langs.lua` comments go stale**: the javascriptreact and dockerfile
   comments describe the old no-alias behavior ("handled by the javascript
   parser", "omit its ft to avoid an autocmd error"). Original rewords both
   to point at `parser_aliases`. No schema or entry changes.
7. **Eager Telescope requires in LspAttach**
   (`nvim-lspconfig.lua:63-68`): six `map()` calls evaluate
   `require('telescope.builtin').lsp_*` at attach time, loading the picker
   on every LSP attach. Original wraps each in a function so the require
   runs only when the mapping fires.
8. **Highlight augroup without refcount** (`nvim-lspconfig.lua:79-98`):
   CursorHold/CursorMoved handlers install on every capable-client attach
   with no guard, and the LspDetach hook (`clear = true` group, recreated
   per attach — same leak pattern as the editing-workflow spec's deferred
   detach fix) clears the buffer's highlight group on *any* detach, killing
   highlights while a second capable client is still attached. Original
   guards install with an `nvim_get_autocmds` existing-check and clears only
   when no `remaining` capable client is still attached to the buffer.
9. **clangd offsetEncoding shape** (`nvim-lspconfig.lua:46`): the current
   tree (post editing-workflow step 02) merges `{ offsetEncoding = 'utf-8' }`
   over cmp defaults. Original `dbeddaa` changes this to the plural list
   `{ 'utf-8', 'utf-16' }`. Per user quiz decision 2026-09-14, that hunk is
   **rejected** — the scalar stays, no clangd change in this spec.
10. **No nvim test file** (`.bin/` has no `tests/` dir): the fetched diffs
    CREATE `.bin/tests/test_nvim_startup.py`, but the issue says "manual
    only, no automated tests". Per user quiz decision 2026-09-14, the
    issue text wins — **no test file is created**; steps 06–07 verify
    manually per the issue's test plan.

Decisions carried from prior specs (not relitigated):

- The `robustness-and-optimization` spec (Done) already pcall-guards
  `vim.treesitter.start()` at ERROR level; step 06's alias+WARN shape
  supersedes that callback body but keeps the pcall discipline.
- The `nvim-startup-polish` spec (Approved, steps 01–02, 04) lazy-loads
  telescope/todo-comments/mini. Step 07's deferred *requires* inside
  LspAttach callbacks are complementary (attach-time, not startup-time)
  and do not conflict.
- The `nvim-editing-workflow` spec (Approved) owns the clangd merge itself
  (step 02), virtual-text (reverted), and cmp confirm; step 07 only changes
  the offsetEncoding value shape.
- The `migrate-0.11.3-to-0.12.5` spec (Done, steps 03–04) owns the
  treesitter rewrite and LSP/mason baseline; this spec builds on those
  file shapes.

## Non-goals

- Do **not** touch shell startup, history, fzf/zoxide/direnv — GH-26 owns that.
- Do **not** touch gitconflict/tmux — GH-27 owns that; rofi/dunst,
  hardware keys, and later PR #25 parts belong to their own GH issues.
- Do **not** touch `keymaps.lua`, copilot, cmp sources, virtual text,
  which-key, neo-tree, mini, conform/lint — owned by the migration,
  editing-workflow, and startup-polish specs.
- Do **not** add a failed-tool report — the issue mentions one but the
  diffs contain none, and per user quiz decision 2026-09-14 it is omitted,
  not invented.
- Do **not** create `.bin/tests/test_nvim_startup.py` — per user quiz
  decision 2026-09-14 the issue's "manual only" wins over the diffs.
- Do **not** change the `langs.lua` spec schema or add/remove language
  entries — comment reword only.
- Do **not** regenerate `lazy-lock.json` — regenerated by `:Lazy sync`
  after plugin-spec edits if needed.

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

### 05 — Safe exit confirmation

- **Files:** `.config/nvim/lua/opts.lua` (EDIT)
- **Changes:** set `confirm` so quitting a dirty buffer offers
  save/discard/cancel instead of failing. One option, no other behavior change.
- **Test:** headless `nvim --headless --noplugin +luafile opts.lua +lua assert(vim.o.confirm) +qa` (also covered by the step-06 test file's `test_headless_opts_load`).
- **Acceptance:**
  - [ ] `:q` on a dirty buffer prompts (manual)
  - [ ] `:q` on a clean buffer quits immediately (manual)

### 06 — Diagnosable tool installation

- **Files:** `.config/nvim/lua/plugins/nvim-lspconfig.lua` (EDIT),
  `.config/nvim/lua/plugins/nvim-treesitter.lua` (EDIT),
  `.config/nvim/lua/autocommands.lua` (EDIT),
  `.config/nvim/lua/langs.lua` (EDIT — comments only)
- **Changes:** annotate the single `mason.setup()` call site; pin
  mason-tool-installer reconciliation to `run_on_start = true,
  debounce_hours = 24` and add the `MasonToolsInstallNow` manual command;
  guard treesitter parser installation when neither `tree-sitter` CLI nor
  `cc` exists (one WARN, early return); add `parser_aliases` + pre-check
  the parser before `start()`, set folds only on success, WARN (not ERROR)
  with a `:TSUpdate` hint; reword the two stale `langs.lua` comments to
  reference `parser_aliases`. Defer the telescope mapping requires (listed
  here because original `263e75f` contains that hunk; per user quiz
  decision 2026-09-14 it ships in this commit to match the source).
- **Test:** manual only, no automated tests (per issue + user quiz
  decision 2026-09-14 — the diffs' test file is not created).
- **Acceptance:**
  - [ ] `:MasonToolsInstallNow` installs on demand; no noisy reconcile spam
  - [ ] `:TSUpdate`, opening zsh/compose/lua/py/ts buffers with no error spam

### 07 — LSP lifecycle correctness

- **Files:** `.config/nvim/lua/plugins/nvim-lspconfig.lua` (EDIT)
- **Changes:** install document-highlight handlers once per buffer
  (existing-autocmd guard); on detach, clear the buffer-local group only
  after the last capable client detaches (`remaining` check). No clangd
  change — the scalar `offsetEncoding = 'utf-8'` stays per user quiz
  decision 2026-09-14.
- **Test:** manual only, no automated tests (per issue + user quiz
  decision 2026-09-14).
- **Acceptance:**
  - [ ] multi-client attach/detach keeps highlights until last detach
  - [ ] LSP pickers open on demand; clangd completions intact

## Risks & Rollback

- **`confirm = true`**: changes `:q`/`:x` UX globally (including scripts
  that expect E37 failure). Rollback: delete the line.
- **`debounce_hours = 24`**: tools install at most once/day automatically;
  a stale tool waits for `:MasonToolsInstallNow`. Rollback: revert step 06.
- **Treesitter CLI guard**: if the `executable` check misfires (e.g. `cc`
  present but broken), parsers silently never install — one WARN is the
  only signal. Rollback: revert the guard hunk.
- **Alias table**: a wrong alias maps a filetype to a missing parser and
  WARNs on every open of that type. Rollback: revert the callback hunk.
- **Highlight refcount**: if the `remaining` filter misidentifies a client
  (e.g. `attached_buffers` shape differs by version), highlights may linger
  or clear early. Verified on nvim 0.12.5 here. Rollback: revert step 07.

Each step is its own commit, so `git revert` or `git bisect` localizes any
regression.
