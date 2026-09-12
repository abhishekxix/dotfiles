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

## Operating workflow

Start by reading this file, checking the current branch and worktree, and then
reading only the matching spec overview and files relevant to the request. Do
not scan completed specs, component trees, or unrelated documentation unless
the task requires it.

Read-only investigation, reviews, planning, and typo-only documentation changes
do not require a spec. Before any behavioral code or configuration edit,
including a one-line change, present the user with a choice:

1. **Full spec** — recommend this for risky, cross-component, dependency,
   installer, Ansible, schema, or otherwise non-trivial work.
2. **Quick change** — a lightweight path that still requires a branch,
   verification, and a focused commit.
3. **Cancel** — make no change.

The user's selection is the required approval to begin. Do not infer approval
from the original request.

Before writing approved changes, ensure the work is on a feature branch. If the
current branch is `main`, create and switch to
`feature/<component>/<verb-subject>` automatically, using a lowercase component
and a short verb-led slug. Ask the user only when the component or slug is
uncertain. Never commit on `main`.

## Spec-driven development

This repo is spec-driven for work that takes the Full spec path:

1. Search `.specs/` for a spec matching the requested change.
2. If one exists, follow it: implement one step at a time, one commit per step,
   and tick off acceptance criteria as they pass.
3. If none exists, read `.specs/README.md` and draft a new spec from
   `.specs/TEMPLATE.md` under `.specs/<COMPONENT>/<slug>/`, then get approval
   **before** implementing. Flip the spec's Status to `Approved` on sign-off —
   its scope and requirements are frozen from there; changes to them need
   re-approval.

Commit the newly approved spec before implementation. During implementation,
automatically check acceptance criteria proven by successful automated tests.
Leave hardware, visual, and other manual criteria unchecked until the user
confirms them. Keep subsequent status and checklist bookkeeping uncommitted,
then ask the user whether to make a final `SPECS` commit after implementation.

This repository's `.specs/` format and location override assistant-specific
spec formats. Do not create a duplicate spec or plan unless an active workflow
explicitly requires one.

## Components

Use these exact prefixes in commit messages. A component maps to a directory
under `.config/` (or a top-level concern):

| Prefix | Scope |
|--------|-------|
| `NVIM` | `.config/nvim/` |
| `QTILE` | `.config/qtile/` |
| `TMUX` | `.config/tmux/` |
| `ALACRITTY` | `.config/alacritty/` |
| `ROFI` | `.config/rofi/` |
| `DUNST` | `.config/dunst/` |
| `PICOM` | `.config/picom.conf` |
| `STARSHIP` | `.config/starship.toml` |
| `CONFIG` | cross-cutting config, unlisted `.config/` tools (including Flameshot and LXSession), or changes spanning multiple config components |
| `HOME` | dotfiles under `home/` (`.zshrc`, `.bashrc`, `.gitconfig`, …) |
| `INSTALLER` | `install`, `.bin/` |
| `ANSIBLE` | `ansible/` |
| `SPECS` | `.specs/` scaffolding |
| `REFACTOR` | restructuring without behavior change |
| `DOCS` | `README.md` and documentation |

Prefer the most specific path-owning component. Use `CONFIG` for changes that
span multiple configuration components, `REFACTOR` only for cross-component
restructuring, `DOCS` for standalone documentation, and `SPECS` for spec-only
lifecycle changes.

## Commit conventions

- Message format: `<COMPONENT>: <summary>` or `<COMPONENT>(<NN>): <summary>`,
  where `<NN>` matches the step number of the spec file being implemented
  (e.g. `NVIM(04): migrate LSP to vim.lsp.config/enable`).
- One commit per logical change / spec step — keeps `git bisect` and `git revert`
  effective.
- Do not mix unrelated changes in one commit.
- After approval, agents may commit automatically on a non-`main` branch. Never
  commit on `main`, and never include unapproved spec bookkeeping or unrelated
  worktree changes in an implementation commit.

## Worktree & secrets

- Inspect relevant existing changes before editing. Preserve concurrent and
  unrelated work; never reset, revert, overwrite, stage, or commit it.
- Inspect the diff before each commit and stage only files for the current
  logical change.
- Never expose or commit credentials, tokens, private keys, machine-specific
  secrets, or unredacted command output containing them.

## Verification

- Run the narrowest relevant checks first and the commands named by an approved
  spec when one exists. Do not run broad, slow, privileged, or live-system
  checks unless needed and approved.
- This repository targets Debian stable, but the execution host may not. Do not
  attempt incompatible platform or hardware checks; perform available static
  validation and report what still needs target-machine confirmation.
- Final reports should concisely list changed files, checks run, unresolved
  risks, pending manual verification, and any uncommitted spec bookkeeping.

## Neovim specifics

- Config lives under `.config/nvim/`.
- Plugin specs are one file each under `.config/nvim/lua/plugins/` and are
  auto-imported by folder — do **not** maintain a manual `require` list.
- `lazy-lock.json` is generated; regenerate with `:Lazy sync` after plugin
  changes and commit the result.

## Pull requests

- Title pull requests `<COMPONENT>: <imperative summary>`, using the component
  rules above and omitting spec step numbers.
- Complete `.github/pull_request_template.md`; use `N/A` rather than removing a
  section that does not apply.
- Creating a pull request requires explicit approval, separate from approval to
  commit or push. Preparing the branch and template is not approval to open it.

## Approval-gated actions

Each of the following requires explicit, per-action approval. Approval for one
action is not consent for the next:

- Running `sudo` or another privilege-escalation command.
- Installing, upgrading, or removing packages.
- Restarting services or the desktop/session.
- Running Ansible outside check mode.
- Creating or replacing live symlinks.
- Pushing commits or creating a pull request.

- **Never** merge PRs (via `gh pr merge` or the GitHub UI/API) unless the user
  asks for that exact action in that moment.
- **Never** push to `main` or any shared branch without being told to.
- Force-pushes, branch protection edits, `gh api` mutations, and deleting
  branches/releases all count as destructive — ask first, every time.
- When in doubt after finishing a step, stop and report what is pending
  instead of completing the workflow end-to-end.

## Working with the installer

- `install` and `ansible/` manage symlinks, packages, and backed-up conflicts.
- `ansible/vars/packages.json` and `ansible/vars/package-deps.json` are kept
  in lexical order — top-level keys, and the fields inside each
  `packages.json` entry, are alphabetized. Insert new entries in sorted
  position instead of appending, and preserve field ordering.
- Changes to already-linked files under `home/` or `.config/` are live
  immediately. Relink only after adding/removing an immediate child or when
  repairing links, and preview that operation with
  `ansible-playbook --check --diff --skip-tags packages ansible/playbook.yml`
  before applying it.
