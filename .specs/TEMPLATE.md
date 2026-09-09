# <Title>

| Field | Value |
|---|---|
| Status | Planning \| Approved \| In progress \| Done |
| Component | NVIM \| QTILE \| WEZTERM \| CONFIG \| INSTALLER \| ANSIBLE |

> Status lifecycle: `Planning` (draft, may still change) → `Approved`
> (reviewer signed off; spec text frozen — further changes need re-approval) →
> `In progress` → `Done`. The writing-plans skill reads the Approved spec and
> produces the implementation plan from it.

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
code out of the spec: for anything over ~3 files, verbatim snippets live in
the implementation plan (writing-plans demands exact values there), not here.
When spec and plan disagree on code, the plan wins for code, the spec wins
for intent.

### 01 — <topic>

- **Files:** `path/to/file` (CREATE | EDIT | DELETE)
- **Changes:** what changes and why.
- **Test:** the command that proves it (e.g. `pytest tests/x -v`, `shellcheck f.sh`)
- **Acceptance:**
  - [ ] verifiable assertion (a behavior check that the Test command must show)

### 02 — <topic>

- **Files:** `path/to/file` (CREATE | EDIT | DELETE)
- **Changes:** what changes and why.
- **Test:** the command that proves it
- **Acceptance:**
  - [ ] verifiable assertion

## Risks & Rollback

What might break, and how to bisect/revert. Because each step is its own commit,
`git revert` or `git bisect` should localize any regression.