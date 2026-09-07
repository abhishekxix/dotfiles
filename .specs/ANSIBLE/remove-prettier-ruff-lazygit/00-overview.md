# Remove prettier, ruff, and lazygit from the package manifest

| Field | Value |
|---|---|
| Status | Done |
| Component | ANSIBLE |
| Created | 2026-09-07 |

## Goal

Drop the three manifest entries with no playbook-level value: `prettier`
(already managed inside Neovim by mason-tool-installer), `ruff` (not wired
into any config), and `lazygit` (unreachable — its extracted binary at
`~/.local/opt/lazygit/lazygit` was never on PATH). The npm (fnm/Node) and
pipx **toolchain bootstrap stays** in the playbook.

## Context & Research

- `prettier`: consumed only by nvim, and only via mason — `.config/nvim/lua/langs.lua`
  declares it as conform formatter for 8 filetypes, and
  `nvim-lspconfig.lua:109` installs all `langs.get_formatters()` through
  mason-tool-installer. The npm manifest entry is redundant with mason and
  is in fact not installed globally on this machine (`npm ls -g` empty).
- `ruff`: zero references in `.config/`, `home/`, or `.bin/`. `langs.lua:75`
  formats Python with black; NVIM spec `migrate-0.11.3-to-0.12.5/04:235`
  explicitly declined wiring ruff. Not installed via pipx on this machine.
- `lazygit`: no references anywhere outside the manifest and point-in-time
  spec history. The archive entry has no `link` field, so
  `~/.local/opt/lazygit/lazygit` is not on `PATH` — unusable as shipped
  (noted during the nvim-from-github-release spec; user chose removal over
  wiring it up).
- Playbook impact: none. All per-source tasks are gated on selected entries;
  with zero `npm`/`pipx` entries the fnm/Node and pipx bootstrap tasks
  become auto-gated no-ops but stay in place (user decision: keep them).
- Selection counts: server 19 → 16, workstation 30 → 27.

## Non-goals

- Not adding ruff to nvim's `langs.lua` (mason-managed linters/formatters
  are an nvim-config concern, done there when wanted).
- No uninstall of previously playbook-installed copies on other machines
  (neither tool is present on this one); no deletion of the orphaned
  `~/.local/opt/lazygit/` directory here — manual cleanup if wanted.
- No changes to schema, validation, or playbook tasks.

## Steps

Single logical change, one commit.

- [x] 01 — Delete the `prettier`, `ruff`, and `lazygit` entries from
      `ansible/vars/packages.json`.
  - **Acceptance:**
    - [x] `python3 -m json.tool ansible/vars/packages.json` exits 0.
    - [x] `ansible-playbook --check --diff --skip-tags packages
          ansible/playbook.yml` passes (validation tasks green).
    - [x] Selection counts: server 16, workstation 27; no `prettier`/`ruff`/
          `lazygit` keys; `grep -rn 'prettier\|ruff\|lazygit' ansible` shows
          no manifest references (spec history excluded).

## Risks & Rollback

- Fresh machines no longer get Node via the npm bootstrap (it was only
  triggered by the prettier entry) — reintroduce by adding any `npm`-source
  entry. `git revert` of the commit restores all three entries.
