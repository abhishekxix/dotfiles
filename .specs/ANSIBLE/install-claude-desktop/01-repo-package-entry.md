# 01 — Claude Desktop repo + package manifest entries

- **Files:** `ansible/vars/repos.json` (EDIT), `ansible/vars/packages.json` (EDIT)
- **Changes:** Add a `claude-desktop` repo entry for the existing pipeline —
  upstream key URL, keyring `/usr/share/keyrings/claude-desktop-archive-keyring.gpg`,
  and the stable repo line with `arch=@ARCH@`. Add a `claude-desktop` apt
  package entry referencing that repo, workstation profile only, with
  `arches: [amd64, arm64]`. Insert both in lexical position and keep
  alphabetized field order per `AGENTS.md` installer rules.
- **Test:** `.bin/validate-manifest.py`, then
  `ansible-playbook --syntax-check ansible/playbook.yml`, then
  `ansible-playbook --check --diff --tags packages ansible/playbook.yml`
  (check mode only; may need become password).
- **Acceptance:**
  - [ ] Validator passes with the new `claude-desktop` repo id referenced by
    the new `claude-desktop` package entry.
  - [ ] Playbook syntax check passes.
  - [ ] Check-mode diff plans `claude-desktop.list` with the `.gpg`
    signed-by and `arch=amd64`, and touches no other repo or package.
  - [ ] Manual: after a real run, `apt-cache policy claude-desktop` still
    resolves from downloads.claude.ai and `apt update` reports no signing
    errors.
