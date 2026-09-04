# AGENTS.md

Guidance for any AI coding assistant, agent, or automation working in this
dotfiles repository. It is deliberately tool-agnostic: the same rules apply
whether you are Copilot, Claude, Codex, an IDE agent, or a scripted bot.

## Repository layout

- `.config/<component>/` — one directory per tool (see component list below).
- `home/` — immediate children are dotfiles linked directly into `$HOME`.
- `ansible/` — Ansible playbook, inventory, tasks, and vars for installation.
- `install` — Python installer that bootstraps Ansible and creates symlinks.
- `.specs/` — spec-driven development plans (see below).
- `.bin/` — custom scripts.

## Spec-driven development

This repo is spec-driven. **Before writing any code:**

1. Search `.specs/` for a spec matching the requested change.
2. If one exists, follow it: implement one step at a time, one commit per step,
   and tick off acceptance criteria as they pass.
3. If none exists, read `.specs/README.md` and draft a new spec from
   `.specs/TEMPLATE.md` under `.specs/<COMPONENT>/<slug>/`, then get approval
   **before** implementing.

Do not skip the spec step for multi-file or non-trivial changes. If in doubt,
write a spec.

## Components

Use these exact prefixes in commit messages. A component maps to a directory
under `.config/` (or a top-level concern):

| Prefix | Scope |
|--------|-------|
| `NVIM` | `.config/nvim/` |
| `QTILE` | `.config/qtile/` |
| `WEZTERM` | `.config/wezterm/` |
| `TMUX` | `.config/tmux/` |
| `ALACRITTY` | `.config/alacritty/` |
| `ROFI` | `.config/rofi/` |
| `DUNST` | `.config/dunst/` |
| `PICOM` | `.config/picom.conf` |
| `STARSHIP` | `.config/starship.toml` |
| `CONFIG` | cross-cutting config or other config files |
| `HOME` | dotfiles under `home/` (`.zshrc`, `.bashrc`, `.gitconfig`, …) |
| `INSTALLER` | `install`, `.bin/` |
| `ANSIBLE` | `ansible/` |
| `SPECS` | `.specs/` scaffolding |
| `REFACTOR` | restructuring without behavior change |
| `DOCS` | `README.md` and documentation |

## Commit conventions

- Message format: `<COMPONENT>: <summary>` or `<COMPONENT>(<NN>): <summary>`,
  where `<NN>` matches the step number of the spec file being implemented
  (e.g. `NVIM(04): migrate LSP to vim.lsp.config/enable`).
- One commit per logical change / spec step — keeps `git bisect` and `git revert`
  effective.
- Do not mix unrelated changes in one commit.

## Neovim specifics

- Config lives under `.config/nvim/`.
- Plugin specs are one file each under `.config/nvim/lua/plugins/` and are
  auto-imported by folder — do **not** maintain a manual `require` list.
- `lazy-lock.json` is generated; regenerate with `:Lazy sync` after plugin
  changes and commit the result.

## Working with the installer

- `install` and `ansible/` manage symlinks, packages, and backed-up conflicts.
- After modifying `home/` or `.config/`, the change is live only after the
  symlinks are (re)created. Preview with
  `ansible-playbook --check --diff --skip-tags packages ansible/playbook.yml`
  before relying on it.