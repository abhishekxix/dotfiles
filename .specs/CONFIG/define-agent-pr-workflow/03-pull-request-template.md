# 03 - add pull-request conventions

- **Files:** `.github/pull_request_template.md` (CREATE), `AGENTS.md` (EDIT)
- **Changes:** add a concise template covering summary, spec or approved quick
  change, validation, manual verification, and risks; define PR titles as
  `<COMPONENT>: <imperative summary>` without spec step numbers; require the
  template to be completed; and retain explicit per-action approval before PR
  creation.
- **Test:** `git diff --check -- .github/pull_request_template.md AGENTS.md`
- **Acceptance:**
  - [x] New pull requests receive a concise, useful default body.
  - [x] The template records the governing spec or approved quick-change path.
  - [x] Validation, pending manual checks, and material risks are visible.
  - [x] PR titles follow `<COMPONENT>: <imperative summary>` with no step number.
  - [x] Creating a PR still requires explicit user approval and is not performed
    by this step.
