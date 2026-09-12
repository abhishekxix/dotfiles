# 02 - align the spec lifecycle

- **Files:** `.specs/README.md` (EDIT), `.specs/TEMPLATE.md` (EDIT)
- **Changes:** document the quiz-based quick-change path, define which approved
  spec content is frozen versus mutable bookkeeping, require exact status
  values, automatically check criteria proven by tests while retaining manual
  checks, keep post-implementation bookkeeping uncommitted pending approval,
  and align the template's component choices with `AGENTS.md`.
- **Test:** `git diff --check -- .specs/README.md .specs/TEMPLATE.md`
- **Acceptance:**
  - [ ] The spec documentation no longer contradicts the quick-change path.
  - [ ] Frozen intent and mutable lifecycle fields are clearly distinguished.
  - [ ] Exact statuses are used, with explanatory notes stored separately.
  - [ ] Automated and manual acceptance handling is explicit.
  - [ ] Final lifecycle/checklist changes require approval before commit.
  - [ ] The template lists every valid component and does not list `WEZTERM`.
