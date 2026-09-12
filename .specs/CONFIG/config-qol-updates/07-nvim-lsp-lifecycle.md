# 07 - Correct Neovim LSP lifecycle

| Field | Value |
|---|---|
| Status | In progress |
| Step | 07 |
| Commit | `CONFIG(07): correct Neovim LSP lifecycle` |

## Files

- `.config/nvim/lua/plugins/nvim-lspconfig.lua` (EDIT)
- `.bin/tests/test_nvim_startup.py` (EDIT)

## Changes

Install document-highlight handlers once per buffer and remove them only after
the last capable client detaches; defer Telescope requires until an LSP picker
mapping is invoked; verify and use the current clangd offset-encoding
capability shape while preserving cmp capabilities. Keep the existing
diagnostic virtual-text policy and do not move or alter it in this step.

## Test

Automated: `python3 -m unittest discover -s .bin/tests -p
'test_nvim_startup.py'`. The test uses the tracked config with isolated
temporary XDG directories and asserts Telescope is absent before picker use.

Manual: use a disposable web project with multiple LSP clients, detach/reattach
clients, invoke an LSP picker, and open a C/C++ fixture with clangd while
inspecting the resolved client capabilities.

## Acceptance

- [ ] Multiple clients do not create duplicate highlight callbacks.
- [ ] Highlights survive until no capable client remains.
- [ ] LSP attach does not itself load Telescope.
- [ ] Clangd retains completion capabilities and negotiates UTF-8 cleanly.

## Risks & Rollback

Capability shapes vary by Neovim/clangd release. The resolved client capability
must be inspected before replacing the current value.
