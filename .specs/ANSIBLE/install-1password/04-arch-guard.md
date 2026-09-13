# 04 — amd64-only arch guard for 1password

- **Files:** `ansible/vars/packages.json` (EDIT),
  `ansible/vars/packages.schema.json` (EDIT), `.bin/validate-manifest.py`
  (EDIT), `ansible/playbook.yml` (EDIT)
- **Changes:** Step 01 specified an arch guard so ARM hosts skip the amd64-only
  1password entry, but no such manifest mechanism exists (archive entries use
  per-arch URL overrides, not a skip guard). Add an optional `arches` list to
  the apt entry model (Debian arch names, e.g. `amd64`), validated by the
  schema and manifest validator, enforced when deriving the selected package
  list so non-matching hosts drop the entry (and its repo) before any apt
  task. Populate `arches: ["amd64"]` for `1password`.
- **Test:** `.bin/validate-manifest.py` and
  `ansible-playbook --check --diff --skip-tags packages ansible/playbook.yml`
- **Acceptance:**
  - [ ] Validator accepts `arches` and rejects malformed values.
  - [ ] On amd64, check-mode diff still plans the 1password repo and package.
  - [ ] On arm64 (verified by inspection or simulated vars), the 1password
    repo and package are excluded from selection.
