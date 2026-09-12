# <Title>

| Field | Value |
|---|---|
| Status | Planning |
| Component | NVIM \| QTILE \| TMUX \| ALACRITTY \| ROFI \| DUNST \| PICOM \| STARSHIP \| CONFIG \| HOME \| INSTALLER \| ANSIBLE \| SPECS \| REFACTOR \| DOCS |
| Created | YYYY-MM-DD |
| Verification notes | None |

> Use exactly one status: `Planning`, `Approved`, `In progress`, or `Done`.
> After approval, the Goal, Context, Non-goals, step text, acceptance text, and
> Risks are frozen; changes need re-approval. Status, checkbox state, and
> Verification notes remain mutable. Keep that implementation bookkeeping
> uncommitted until the user approves a final `SPECS` commit.

## Goal

One or two sentences — the outcome this spec delivers, and why now.

## Context & Research

Upstream changelogs, breaking changes, relevant links, and key facts that
informed the plan. Capture anything a reviewer (or future-you) would need to
verify an assumption.

## Non-goals

What we explicitly will **NOT** do (keeps scope tight, prevents creep).

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

Describe *what* changes and *why* — files, behavior, rationale. Keep exact
code out of the spec; verbatim snippets belong in implementation notes only
when they are needed.
When spec and implementation planning disagree, the spec wins for intent and
scope; resolve any conflict before writing code.

### 01 — <topic>

- **Files:** `path/to/file` (CREATE | EDIT | DELETE)
- **Changes:** what changes and why.
- **Test:** the command that proves it (e.g. `pytest tests/x -v`, `shellcheck f.sh`)
- **Acceptance:**
  - [ ] verifiable assertion (a behavior check that the Test command must show)
  - [ ] manual assertion (leave unchecked until the user confirms it)

### 02 — <topic>

- **Files:** `path/to/file` (CREATE | EDIT | DELETE)
- **Changes:** what changes and why.
- **Test:** the command that proves it
- **Acceptance:**
  - [ ] verifiable assertion

## Risks & Rollback

What might break, and how to bisect/revert. Because each step is its own commit,
`git revert` or `git bisect` should localize any regression.
