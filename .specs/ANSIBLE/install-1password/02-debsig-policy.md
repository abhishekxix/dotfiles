# 02 — debsig-verify policy support in repos pipeline

- **Files:** `ansible/vars/repos.json` (EDIT), `ansible/tasks/repos.yml` (EDIT)
- **Changes:** 1Password's install requires a debsig-verify policy and keyring
  outside the normal apt signed-by flow, so extend the repo pipeline
  generically: optional per-repo `debsig` fields (policy URL, policy dir, and
  keyring path reusing the repo `key_url`) drive new tasks that create the
  policy/keyring directories, fetch the `.pol` file, and dearmor the same key
  into the debsig keyring. Ensure the `debsig-verify` binary is installed when
  any selected repo declares debsig fields. Populate the fields for
  `1password` (policy id `AC2D62742012EA22`).
- **Test:** `.bin/validate-manifest.py` and
  `ansible-playbook --check --diff --skip-tags packages ansible/playbook.yml`
- **Acceptance:**
  - [ ] Validator accepts the new optional debsig fields and rejects malformed
    ones.
  - [ ] Check-mode diff shows the debsig policy dir, `.pol` file, and dearmored
    keyring planned for the 1password repo.
  - [ ] After a real run on x86_64: `dpkg-sig`/`debsig-verify` policy files
    exist and `apt install 1password` succeeds.
  - [ ] Re-run is idempotent: policy and keyring tasks report no change.
