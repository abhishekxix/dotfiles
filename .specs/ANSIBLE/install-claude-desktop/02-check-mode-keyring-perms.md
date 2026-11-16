# 02 — Check-mode-safe keyring permissions task

- **Files:** `ansible/tasks/repos.yml` (EDIT)
- **Changes:** In check mode the `creates`-guarded dearmor task never runs
  (it only reports `changed`), so a keyring that does not exist yet is never
  created, and `Ensure third-party keyring permissions` (`state: file`)
  fails with "file … is absent". This blocks previewing any newly added repo,
  first seen with `claude-desktop`. Skip that permissions task for an item
  only when running in check mode *and* the dearmor result for that item is
  `changed` (i.e. the keyring would be created). Real runs and existing
  keyrings keep the current behavior. Add a short comment explaining why.
- **Test:** `ansible-playbook --syntax-check ansible/playbook.yml`, then the
  user runs `ansible-playbook --check --diff --tags packages -K ansible/playbook.yml`
  from a real terminal.
- **Acceptance:**
  - [ ] Playbook syntax check passes.
  - [ ] Manual: check mode completes without failing on the missing
    `claude-desktop` keyring, and the diff shows `claude-desktop.list` moving
    its signed-by to the `.gpg` keyring with no other repo changes.
  - [ ] Manual: existing keyrings (e.g. 1password, docker) still report `ok`
    on the permissions task in check mode.
