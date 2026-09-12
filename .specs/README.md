# Specs

Spec-driven development for non-trivial work in this dotfiles repo. A **spec**
is a scoped, planned change: a goal, numbered steps, and acceptance criteria —
written *before* code.

Before behavioral code or configuration changes, `AGENTS.md` requires the user
to choose Full spec, Quick change, or Cancel. The Quick change path skips this
spec lifecycle but still requires a feature branch, targeted verification, and
a focused commit. Read-only work and typo-only documentation changes do not
require a spec.

## Layout

```
.specs/
  README.md          # this file
  TEMPLATE.md        # canonical spec template (copy to start a new spec)
  <COMPONENT>/       # e.g. NVIM/, QTILE/, ALACRITTY/, CONFIG/, INSTALLER/
    <slug>/          # one folder per spec, e.g. migrate-0.11.3-to-0.12.5/
      00-overview.md # spec summary + status checklist
      01-<topic>.md  # one file per step (in execution order)
      02-<topic>.md
      ...
```

Rules:

- **One folder per spec**, named with a `<verb>-<subject>` slug.
- Files are numbered to reflect execution order (`00` is the overview + status).
- The `00-*` file tracks overall status as a checklist (`[ ]` → `[x]`).

## Lifecycle

1. **Plan** — copy `TEMPLATE.md`, fill in Goal / Context / Non-goals / Steps.
   Do not write code in this stage. Keep exact code out of the spec; use
   implementation notes only when exact details are needed.
2. **Approve** — get sign-off on the spec before implementing, set Status to
   exactly `Approved`, and commit the approved spec. Scope and requirements are
   frozen from here; edits need re-approval. Status, checklist state, and
   verification notes remain mutable lifecycle bookkeeping.
3. **Implement** — set Status to exactly `In progress` and make one commit per
   step, named `<COMPONENT>(<NN>): <summary>`
   (matching existing history, e.g. `NVIM(03): ...`, `QTILE: ...`).
4. **Verify** — automatically check criteria proven by successful automated
   tests. Leave hardware, visual, and other manual criteria unchecked until the
   user confirms them.
5. **Close** — set Status to exactly `Done` after all criteria pass. Keep status,
   checklist, and verification-note changes uncommitted during implementation;
   ask the user whether to create a final `SPECS` bookkeeping commit.

Use only `Planning`, `Approved`, `In progress`, or `Done` in the Status field.
Put explanations such as pending manual checks in Verification notes instead of
creating custom status values.

## Commit conventions

See `AGENTS.md` for the full component-prefix table and one-commit-per-step rules.
The key constraint for specs:

- Prefix commits with the component (full table in `AGENTS.md`).
- When a commit maps to a spec step, include the step number: `NVIM(04): ...`.
- Step number in the commit **must** match the `NN` in the spec filename.

## For agents & automation

`AGENTS.md` at the repo root is the canonical, tool-agnostic entry point. For
the Full spec path, check `.specs/` for an existing spec and, if none matches,
draft one from `TEMPLATE.md` and get approval before implementing.
