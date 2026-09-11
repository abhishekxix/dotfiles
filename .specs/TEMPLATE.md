# Spec Templates

Use both templates. A valid spec has one overview and at least one numbered
step file. Delete instructional comments and unused placeholders before review.

## `00-overview.md`

```markdown
# <Title>

| Field | Value |
|---|---|
| Status | Planning |
| Component | <COMPONENT> |
| Created | YYYY-MM-DD |

## Goal

<Outcome and reason for the change.>

## Context & Research

<Current-state evidence, upstream facts, prior decisions, and user choices.>

## Non-goals

- <Explicitly excluded behavior.>

## Steps

- [ ] [01 - <First step>](01-first-step.md)
- [ ] [02 - <Second step>](02-second-step.md)

## Risks & Rollback

<Cross-step risks, ordering constraints, and rollback strategy.>
```

## `01-first-step.md`

Copy once per step and increment every `01` consistently.

```markdown
# 01 - <Step title>

| Field | Value |
|---|---|
| Status | Planning |
| Step | 01 |
| Commit | `<COMPONENT>(01): <summary>` |

## Files

- `exact/path/to/file` (EDIT)
- `exact/path/to/new-file` (CREATE)

## Changes

<Behavior and rationale. Keep full implementation snippets in the later plan.>

## Test

Automated: `exact-command --with arguments`.

Manual: <Label a live/hardware/reboot check explicitly, or delete this line.>

## Acceptance

- [ ] <Finite observation produced by the test above.>

## Risks & Rollback

<Step-specific failure mode and how its commit can be reverted safely.>
```

## Mandatory Rules

- Overview checklists link child files; implementation details live in children.
- Every child number matches its filename, metadata, checklist, and commit.
- Files lists contain exact tracked paths and operations, never directory-only
  entries, broad globs, or placeholders.
- Runtime-generated fixtures are described under Test and owned by an exact
  test file; they are not listed as created directories.
- Tests provide exact repository-root commands and label manual checks.
- Acceptance is finite and bounded; avoid "never", "everything", and other
  claims a test cannot prove.
- Record prior user decisions and do not restore reverted behavior without new
  explicit approval.
- Keep all statuses `Planning` until explicit approval. A request to commit or
  push the draft is not approval to implement it.
- After approval, only lifecycle metadata and status/acceptance checkboxes may
  change without re-approval; body edits remain frozen.
- Existing approved/in-progress/done legacy specs are grandfathered and are not
  rewritten solely to adopt this template.
- Complete the author checklist in `.specs/README.md` before committing.
