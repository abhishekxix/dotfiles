# 01 — Archive `link` support

- **Files:** `ansible/vars/packages.schema.json` (EDIT),
  `ansible/playbook.yml` (EDIT)
- **Changes:**
  - Add an optional `link` field to the `archive` subschema: a relative path
    (within the extracted tree at `dest`) pointing at a binary.
  - New playbook task after "Extract archives" (`playbook.yml`): for each
    archive entry with `link` defined, ensure a symlink
    `~/.local/bin/<basename of link>` → `dest/link`. Uses `state: link` /
    `force: true` so it survives version bumps (retargeting, not recreating).
    No `link` ⇒ task skips that entry (lazygit initially keeps its current,
    unchanged behavior; wiring it up is a separate concern).
- **Acceptance:**
  - [x] Schema accepts an archive entry with `link` and rejects `link` on
        non-archive sources (spot-check via a scratch fixture against
        `jsonschema` / `--check` validation task at `playbook.yml:92-116`).
  - [x] Dry run: `ansible-playbook --check --diff --skip-tags packages
        ansible/playbook.yml` still passes with the validation tasks.
