# 03 — lexical-order note in AGENTS.md

- **Files:** `AGENTS.md` (EDIT)
- **Changes:** Under "Working with the installer", add one bullet:

  ```markdown
  - `ansible/vars/packages.json` and `ansible/vars/package-deps.json` are kept
    in lexical order — top-level keys, and the fields inside each
    `packages.json` entry, are alphabetized. Insert new entries in sorted
    position instead of appending, and preserve field ordering.
  ```

- **Acceptance:**
  - [ ] `AGENTS.md` contains the note covering both vars files in the
        "Working with the installer" section.
  - [ ] No other AGENTS.md content is modified.
