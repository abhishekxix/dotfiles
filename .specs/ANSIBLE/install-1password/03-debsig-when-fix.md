# 03 — fix debsig-verify install condition

- **Files:** `ansible/tasks/repos.yml` (EDIT)
- **Changes:** The `Ensure debsig-verify is installed` condition misuses
  `select` with `in`/`extract` as Jinja tests, which fails templating when any
  repo is selected. Map the selected repo IDs to their manifest entries first
  (extract from `dotfiles_repos_manifest`), then filter on the `debsig`
  attribute. No behavior change on hosts without debsig repos.
- **Test:** `ansible-playbook --syntax-check ansible/playbook.yml` and
  `.bin/validate-manifest.py`
- **Acceptance:**
  - [ ] Syntax check passes and the condition templates without error when
    repos are selected (no unknown-test failure).
  - [ ] Check-mode diff still plans the debsig policy dir, `.pol` file, and
    dearmored keyring for the 1password repo.
