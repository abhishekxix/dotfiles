# Specs

Spec-driven development for this dotfiles repo. A **spec** is a scoped, planned
change: a goal, numbered steps, and acceptance criteria — written *before* code.

## Layout

```
.specs/
  README.md          # this file
  TEMPLATE.md        # canonical spec template (copy to start a new spec)
  <COMPONENT>/       # e.g. NVIM/, QTILE/, WEZTERM/, CONFIG/, INSTALLER/
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
   Do not write code in this stage.
2. **Approve** — get sign-off on the spec before implementing (a PR comment,
   a chat confirmation, whatever you normally do).
3. **Implement** — one commit per step, named `<COMPONENT>(<NN>): <summary>`
   (matching existing history, e.g. `NVIM(03): ...`, `QTILE: ...`).
4. **Verify** — check off each step's acceptance criteria *before* committing.
5. **Close** — flip the spec Status to `Done`.

## Commit conventions

See `AGENTS.md` for the full component-prefix table and one-commit-per-step rules.
The key constraint for specs:

- Prefix commits with the component (full table in `AGENTS.md`).
- When a commit maps to a spec step, include the step number: `NVIM(04): ...`.
- Step number in the commit **must** match the `NN` in the spec filename.

## For agents & automation

`AGENTS.md` at the repo root is the canonical, tool-agnostic entry point. In
short: check `.specs/` for an existing spec, and if none matches, draft one from
`TEMPLATE.md` and get approval before implementing.