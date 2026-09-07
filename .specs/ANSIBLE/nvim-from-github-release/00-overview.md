# Install neovim from the GitHub release instead of apt

| Field | Value |
|---|---|
| Status | Planning |
| Component | ANSIBLE |
| Created | 2026-09-07 |

## Goal

Install neovim from the latest GitHub release tarball (`v0.12.5` at time of
writing) into `~/.local/opt/neovim`, exposed as `~/.local/bin/nvim`, replacing
the apt entry. Ubuntu's apt neovim is far behind upstream (0.10-era on stable
releases), which starves the nvim config of new features.

## Context & Research

- Latest upstream release: **v0.12.5**; assets include
  `nvim-linux-x86_64.tar.gz` and `nvim-linux-arm64.tar.gz` (verified via the
  GitHub releases API on 2026-09-07).
- Tarball layout: a single root dir (`nvim-linux-x86_64/` / `nvim-linux-arm64/`)
  containing `bin/nvim`, `lib/`, `share/`, `man/` — i.e. `strip=1` into
  `~/.local/opt/neovim` yields `~/.local/opt/neovim/bin/nvim`.
- The `archive` source (playbook.yml:456) only extracts and is guarded by
  `creates`; it cannot expose a nested binary on `PATH`.
  `starship` works because its tarball contains a bare binary extracted
  directly into `~/.local/bin`; `lazygit` (`~/.local/opt/lazygit/lazygit`) is
  **not** reachable via the dotfiles alone — this spec adds the generic
  mechanism that also fixes lazygit.
- `~/.local/bin` is prepended to `PATH` in `home/.profile:15`, so
  `~/.local/bin/nvim` will shadow any leftover `/usr/bin/nvim`.

## Non-goals

- No auto-updating / `releases/latest/download` tracking — version bumps are
  manual edits to `packages.json` (decided: pinned).
- No auto-removal of a pre-existing apt-installed neovim (see Risks); the
  `~/.local/bin` shim shadows it regardless.
- No changes to other packages or the nvim config itself.

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

- [x] 01 — Archive `link` support (01-archive-link-support.md)
- [ ] 02 — Swap neovim to the GitHub tarball (02-neovim-archive-entry.md)

## Risks & Rollback

- Machines that deliberately installed apt neovim will keep it (shadowed, not
  removed) — safe default; removal is left as a manual `sudo apt remove neovim`.
- If the `link` task misbehaves, it only creates symlinks in `~/.local/bin`,
  trivially reversible. Each step is its own commit, so `git revert` localizes
  any regression; the neovim entry swap alone can be reverted without touching
  the `link` mechanism.
