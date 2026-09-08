# 01 — tree-sitter-cli: npm → cargo

## Files

- `ansible/vars/packages.json` (EDIT)

## Changes

Replace the npm entry with a cargo entry. The key stays `tree-sitter-cli`
(already in lexical position); the entry's fields stay alphabetized
(`crate`, `profiles`, `source`):

```json
"tree-sitter-cli": {
  "crate": "tree-sitter-cli",
  "profiles": [
    "workstation"
  ],
  "source": "cargo"
}
```

- `package` (npm-only, schema-required there) is dropped; `crate`
  (cargo-required) is added — `ansible/vars/packages.schema.json:68`
  requires `source`, `crate`, `profiles` for cargo entries.
- No `version` pin (matches the old npm entry and the manifest's optional
  `version` policy).
- After this change the manifest has zero `npm` entries; the
  "Install global npm packages" loop in `ansible/tasks/packages.yml` becomes
  a harmless no-op (the npm source stays supported — see overview
  non-goals). The npm *toolchain* gating fix lands in step 02.

## Acceptance

- [ ] `python3 -m json.tool ansible/vars/packages.json` exits 0.
- [ ] `ansible-playbook --check --tags packages ansible/playbook.yml`
  passes preflight manifest/schema validation
  (`ansible/tasks/preflight.yml:56`).
- [ ] `--check` output shows `tree-sitter-cli` in the
  "Install cargo crates" task labels.
