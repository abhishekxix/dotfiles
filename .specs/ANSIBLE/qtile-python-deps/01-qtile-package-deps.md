# 01 — qtile runtime deps in package-deps.json

- **Files:** `ansible/vars/package-deps.json` (EDIT)
- **Changes:** Add a `"qtile"` key (after `"picom"`, keeping lexical order)
  mapping to the runtime Python deps that the apt `qtile` package does NOT
  already pull in:

  ```json
  "qtile": [
    "python3-dbus-fast",
    "python3-psutil",
    "python3-xdg"
  ]
  ```

  - `python3-dbus-fast` — notifications (docs / `optional_core` extra;
    successor of the legacy `dbus-next` the user previously installed).
  - `python3-psutil` — `qtile[widgets]` dependency.
  - `python3-xdg` — Debian binary name for `pyxdg` (widgets; also an apt
    Recommends, declared anyway so installs stay deterministic under
    `--no-install-recommends`).
- **Acceptance:**
  - [ ] `jq '.qtile' ansible/vars/package-deps.json` lists exactly the three
        packages above.
  - [ ] Keys remain lexically ordered: `jq 'keys' ansible/vars/package-deps.json`
        → `["picom", "qtile", "$schema"]` (jq's `keys` sorts `$schema` last is
        acceptable — file order is `"$schema"` first, then `picom`, `qtile`).
  - [ ] `ansible-playbook --check --diff --skip-tags packages
        ansible/playbook.yml` parses cleanly; with the workstation profile the
        "Install build dependencies" task would target the three packages
        (visible in check-mode output / `--list-tasks` dry inspection).
