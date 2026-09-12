# 01 - define agent workflow rules

- **Files:** `AGENTS.md` (EDIT)
- **Changes:** clarify the quick-change quiz and mandatory approval boundary;
  automatically create `feature/<component>/<verb-subject>` when work starts on
  `main`, asking only when classification is uncertain; allow automatic commits
  only on non-`main` branches after approval; gate privileged/live-system
  mutations and PR creation; preserve unrelated work and secrets; correct the
  live-symlink guidance; define automatic versus manual acceptance checks; keep
  post-implementation spec bookkeeping uncommitted pending user approval; make
  `CONFIG` own unlisted and multi-config changes; and add concise exploration,
  verification, host-target, and completion-report rules.
- **Test:** `git diff --check -- AGENTS.md`
- **Acceptance:**
  - [x] Behavioral code/config changes cannot start without quiz-based user
    approval, including one-line changes.
  - [x] Agents automatically create a conventionally named feature branch from
    `main` and never commit on `main`.
  - [x] Approved work may be committed automatically on a non-`main` branch,
    one commit per logical change or spec step.
  - [x] `sudo`, package mutations, service/session changes, non-check Ansible,
    live symlink recreation, and PR creation have explicit approval gates.
  - [x] Automated acceptance criteria are checked after passing validation;
    manual/hardware criteria remain unchecked until user confirmation.
  - [x] Spec lifecycle bookkeeping stays uncommitted until the user approves a
    final commit.
  - [x] Dirty-worktree, secret, live-symlink, target-platform, targeted-test,
    concise-reporting, and relevant-files-only guidance is present.
  - [x] Unlisted and multi-config changes use `CONFIG`.
