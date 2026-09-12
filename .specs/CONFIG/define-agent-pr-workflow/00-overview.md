# Define agent and pull-request workflow

| Field | Value |
|---|---|
| Status | Done |
| Component | CONFIG |
| Created | 2026-09-12 |
| Verification notes | All automated checks passed; no manual checks required. |

## Goal

Make agent behavior predictable and efficient by defining when approval, specs,
branches, commits, system changes, and pull requests are allowed, while keeping
the instructions concise enough to avoid unnecessary context use.

## Context & Research

- The repository currently requires specs for changes but gives conflicting
   guidance about whether trivial changes have a fast path.
- The user approved an explicit quiz-based quick-change path, while retaining
  mandatory approval for every behavioral code or configuration change.
- Agents may create a feature branch and commit automatically, but must never
  commit on `main`. The branch convention is
  `feature/<component>/<verb-subject>`.
- Privileged or live-system mutations and pull-request creation each require
  explicit user approval.
- Automated acceptance criteria should be checked when their validation passes;
  hardware and other manual criteria require user confirmation.
- Spec lifecycle updates should remain uncommitted after implementation until
  the user approves a final bookkeeping commit.
- `.specs/TEMPLATE.md` has drifted from the component list in `AGENTS.md`, and
  the repository has no pull-request template.

## Non-goals

- Do not add a spec linter or other workflow automation.
- Do not create, push, or merge a pull request as part of this change.
- Do not introduce dedicated `FLAMESHOT` or `LXSESSION` components; they and
  changes spanning multiple configurations use `CONFIG`.
- Do not change runtime dotfiles, Ansible behavior, or installer behavior.

## Steps

- [x] 01 - define agent approval, branch, commit, safety, and efficiency rules
- [x] 02 - align the spec lifecycle and template with those rules
- [x] 03 - add the pull-request template and title convention

## Risks & Rollback

- Excessive approval gates could slow routine work; the quiz-based quick-change
  path preserves an explicit but lightweight option.
- Automatic branch and commit behavior could surprise users; both are limited
  to approved work on non-`main` branches, with uncertainty routed back to the
  user.
- A verbose PR template could create busywork; keep it focused on scope,
  validation, manual checks, and risk.
- Each step is isolated so `git revert` can remove any rule independently.
