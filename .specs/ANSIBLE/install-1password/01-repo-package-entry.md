# 01 — 1Password repo + package manifest entries

- **Files:** `ansible/vars/repos.json` (EDIT), `ansible/vars/packages.json` (EDIT)
- **Changes:** Add a `1password` repo entry keyed for the existing pipeline —
  upstream key URL, archive keyring path, and the amd64 repo line — plus a
  `1password` apt package entry pointing at that repo, workstation profile.
  Insert both in lexical position per `AGENTS.md` installer rules. The repo
  line keeps upstream's hardcoded `amd64` (no `@ARCH@` substitution; upstream
  ships no ARM build). The package entry carries an arch guard so ARM hosts
  skip it instead of failing on a missing amd64 package.
- **Test:** `.bin/validate-manifest.py`
- **Acceptance:**
  - [ ] Validator passes with the new `1password` repo id referenced by the
    new `1password` package entry.
  - [ ] `ansible-playbook --check --diff --skip-tags packages ansible/playbook.yml`
    shows the repo and package planned without touching other entries.
