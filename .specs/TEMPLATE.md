# <Title>

| Field | Value |
|---|---|
| Status | Planning | In progress | Done |
| Component | NVIM \| QTILE \| WEZTERM \| CONFIG \| INSTALLER \| ANSIBLE |
| Created | YYYY-MM-DD |

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

### 01 — <topic>

- **Files:** `path/to/file` (CREATE | EDIT | DELETE)
- **Changes:** what changes and why.
- **Acceptance:**
  - [ ] verifiable assertion (a test command, a `:checkhealth`, a behavior check)

### 02 — <topic>

- **Files:** `path/to/file` (CREATE | EDIT | DELETE)
- **Changes:** what changes and why.
- **Acceptance:**
  - [ ] verifiable assertion

## Risks & Rollback

What might break, and how to bisect/revert. Because each step is its own commit,
`git revert` or `git bisect` should localize any regression.