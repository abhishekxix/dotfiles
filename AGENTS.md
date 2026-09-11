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
   **before** implementing. Flip the spec's Status to `Approved` on sign-off.
   The approved body is frozen; implementation may update only lifecycle
   metadata and acceptance/status checkboxes. Other edits need re-approval.

Do not skip the spec step for multi-file or non-trivial changes. If in doubt,
write a spec.

### Required spec structure

- Apply this structure to new specs and substantively revised `Planning`
  drafts. Existing approved/in-progress/done legacy specs are grandfathered:
  follow their recorded structure and do not reorganize frozen text merely for
  compliance.
- `00-overview.md` contains the goal, current-state research, decisions,
  non-goals, risks, and a linked `[ ]` checklist of steps. Do not put the only
  copy of an implementation step in the overview.
- Every implementation step has its own numbered file (`01-*.md`, `02-*.md`,
  ...), and its number must match the overview link, metadata `Step`, and
  proposed commit prefix.
- Every step file uses the metadata table from `.specs/TEMPLATE.md` and lists
  concrete tracked file paths with `CREATE`, `EDIT`, or `DELETE`. Git does not
  track directories: do not list a directory as a created file. If tests create
  temporary fixtures, name the exact test file and state that fixtures are
  generated at runtime.
- Every `Test` section includes exact executable commands. Label live/manual
  checks explicitly; do not use vague prose such as "test this". Acceptance
  criteria must be finite and observable, not claims such as "never breaks".
- Record user decisions and prior accepted/reverted behavior before defining
  steps. A new audit is not permission to relitigate an earlier decision.
- Keep draft and child-step statuses `Planning` until explicit approval. Do not
  infer approval from a request to edit, commit, or push the draft.

Before committing a spec, perform the author checklist in `.specs/README.md`:
verify structure, links, numbering, exact paths, executable tests, bounded
acceptance, prior decisions, and placeholders. For a substantial spec, run a
fresh-context review and resolve its blockers before presenting the draft.

**Spec format precedence.** This repo's `.specs/` format (frontmatter table,
Goal / Context / Non-goals / Steps with Files + Changes + Test + Acceptance,
Risks & Rollback) is authoritative here. Generic plugin spec/skills formats
(e.g. superpowers brainstorming's `docs/superpowers/specs/` layout) do NOT
apply: when a plugin skill prescribes its own spec location or structure,
follow `.specs/README.md` + `.specs/TEMPLATE.md` instead, and treat the
plugin's spec-writing step as satisfied by the `.specs/` file. Implementation
plans still live where the executing skill expects them.

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
  before relying on it.
