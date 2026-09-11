# Specs

Spec-driven development for this dotfiles repository. A spec is a reviewed,
testable contract written before implementation, not a loose list of ideas.

## Layout

```text
.specs/
  README.md
  TEMPLATE.md
  <COMPONENT>/
    <verb-subject>/
      00-overview.md
      01-first-step.md
      02-second-step.md
```

Rules:

- These rules apply to new specs and substantively revised `Planning` drafts.
  Existing `Approved`, `In progress`, and `Done` legacy specs are grandfathered;
  do not restructure frozen history solely to match the current template.
- Use one folder per spec, named with a `<verb>-<subject>` slug.
- `00-overview.md` owns goal, research, decisions, non-goals, risks, and the
  linked status checklist. It does not replace numbered step files.
- Every implementation step has one numbered file in execution order.
- Step numbers must match in the filename, overview link, metadata `Step`, and
  proposed commit message.
- Keep the overview and every child step at `Planning` while drafting.

## Lifecycle

1. **Research:** inspect the current tree, existing specs, recent history, and
   relevant upstream behavior. Record prior user decisions before proposing
   changes.
2. **Plan:** create `00-overview.md` and one numbered file per implementation
   step using `TEMPLATE.md`.
3. **Review:** run the author checklist below. Substantial specs also receive a
   fresh-context review for contradictions, missing files, and untestable
   acceptance criteria.
4. **Approve:** obtain explicit sign-off, then change overview and child-step
   statuses to `Approved`. Approval freezes body text. Lifecycle metadata,
   overview/acceptance checkboxes, and completion status remain editable during
   implementation; other edits require new approval.
5. **Implement:** execute one numbered step at a time and use its exact proposed
   commit prefix.
6. **Verify:** run the step's commands and complete its finite acceptance
   checks before committing.
7. **Close:** check the overview link as each step lands; mark the spec `Done`
   only after every step and live/manual gate has passed.

A request to edit, commit, or push a draft is not implementation approval and
does not change `Planning` to `Approved`.

## Overview Contract

`00-overview.md` must contain:

- The metadata table and `Planning` status.
- A concise outcome-oriented goal.
- Current-state research with concrete repository evidence.
- User decisions and prior accepted/reverted behavior that constrain scope.
- Explicit non-goals.
- A `[ ]` checklist linking every numbered step file.
- Cross-step risks, ordering constraints, and rollback strategy.

Do not duplicate the full Files/Changes/Test/Acceptance body of every child in
the overview. The links are the single status index; child files are the
implementation contracts.

## Step Contract

Every numbered step file must contain:

- A metadata table with `Status`, two-digit `Step`, and exact proposed `Commit`.
- `## Files` with every concrete tracked path and `CREATE`, `EDIT`, or `DELETE`.
- `## Changes` describing behavior and rationale without embedding a full code
  implementation.
- `## Test` containing exact executable commands.
- `## Acceptance` containing finite, observable checkboxes.
- `## Risks & Rollback` scoped to that step.

### File Paths

- Name files, not directories. Git cannot track an empty directory.
- Do not write placeholders such as `relevant files`, `tests/`, `*.yml`, or
  `manifest schemas` in a Files list.
- If a test creates temporary fixtures at runtime, list the exact test file and
  say so in the Test section. Do not list a fixture directory as `CREATE`.
- If a generated artifact will be committed, name that exact artifact. If the
  filename cannot yet be known, the spec is not ready for approval.
- Existing finite glob use is allowed only in executable commands, not as a
  substitute for the Files inventory.

### Tests

- Give commands exactly as they will be run from the repository root.
- Separate `Automated:` and `Manual:` checks. Label X11, hardware, reboot,
  network, and other live checks explicitly.
- A manual check may complement automation where behavior cannot be simulated,
  but vague prose such as "verify it works" is not a test.
- Tests must avoid destructive state: use disposable directories, temporary
  files, isolated tmux sockets, and non-production fixtures.
- Do not make an earlier step depend on a test file introduced by a later step.
- A CI workflow is not proof before it exists. Provide a locally runnable
  command or harness that CI will invoke.

### Acceptance

- Each checkbox must have a finite pass/fail observation.
- Avoid absolutes such as "never breaks", "all systems", or "no unexplained
  changes". Name the files, fixtures, profiles, commands, or hardware matrix
  that bound the claim.
- Acceptance cannot claim behavior for a toolkit/platform not configured by the
  listed files.
- Keep live/manual acceptance unchecked until the real check has run.

## Author Checklist

Run this before committing or requesting approval:

- [ ] The matching existing specs and recent commits were reviewed.
- [ ] User decisions, prior reverts, and retained behavior are recorded.
- [ ] `00-overview.md` contains a linked checklist, not embedded substitute steps.
- [ ] Every checklist link resolves to one numbered child file.
- [ ] Filename, heading, metadata `Step`, checklist number, and commit prefix match.
- [ ] Every child has the required metadata and all five required sections.
- [ ] Every Files entry is an exact tracked path with a valid operation.
- [ ] No directory-only entries, broad globs, placeholders, `TBD`, or `TODO` remain.
- [ ] Every Test section includes exact commands and labels manual/live checks.
- [ ] Tests are non-destructive and do not depend on later steps.
- [ ] Every acceptance criterion is bounded and observable.
- [ ] Cross-step dependencies and rollback risks are explicit.
- [ ] Overview and children remain `Planning` until explicit approval.
- [ ] `git diff --check` passes and only intended spec/documentation files changed.
- [ ] A fresh-context review found no unresolved blockers for substantial specs.

## Commit Conventions

See `AGENTS.md` for component prefixes. Implementation commits use
`<COMPONENT>(<NN>): <summary>`, where `<NN>` matches the child filename and its
metadata. The commit that drafts or revises planning documents uses the normal
`SPECS: <summary>` convention and does not count as an implementation step.

## For Agents

`AGENTS.md` is the canonical entry point. This file and `TEMPLATE.md` define the
required repository-specific spec shape. Generic skill/plugin spec layouts do
not override it.
