# 06 - Make Neovim tool installation diagnosable

| Field | Value |
|---|---|
| Status | In progress |
| Step | 06 |
| Commit | `CONFIG(06): make Neovim tool installation diagnosable` |

## Files

- `.config/nvim/lua/plugins/nvim-lspconfig.lua` (EDIT)
- `.config/nvim/lua/plugins/nvim-treesitter.lua` (EDIT)
- `.config/nvim/lua/autocommands.lua` (EDIT)
- `.config/nvim/lua/langs.lua` (EDIT)
- `.bin/tests/test_nvim_startup.py` (CREATE)

## Changes

Initialize Mason exactly once; debounce/delay automatic tool reconciliation and
retain an immediate manual command; report failed tools once with actionable
context; do not launch parser installation when the required CLI is absent;
return before enabling Treesitter folds after parser-start failure; deduplicate
parser errors; explicitly resolve Zsh/Bash and Docker-Compose/YAML parser
aliases; correct stale language comments.

## Test

Automated: `python3 -m unittest discover -s .bin/tests -p
'test_nvim_startup.py'`. The test starts Neovim against the tracked config with
isolated temporary XDG data/state/cache directories and controlled tool stubs.

The unit test supplies a controlled PATH with required tools present and
absent. Manual network-dependent: run `:MasonToolsInstall` and `:TSUpdate`, then open
representative Zsh, YAML Compose, Lua, Python, and TypeScript buffers.

## Acceptance

- [ ] Each controlled startup records exactly one Mason initialization.
- [ ] The second missing-tool fixture start inside the debounce window repeats no installation failure for that tool.
- [ ] Missing Black/tree-sitter state produces one actionable diagnostic.
- [ ] Parser-backed buffers highlight/fold successfully.
- [ ] Failed/unsupported parsers do not install a broken fold expression.

## Risks & Rollback

Parser aliases and installer scheduling are version-sensitive. Keep manual
reconciliation available and revert aliases independently if a supported
filetype loses highlighting.
