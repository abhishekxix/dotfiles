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
  - [x] `jq '.qtile' ansible/vars/package-deps.json` lists exactly the three
        packages above.
  - [x] Keys remain lexically ordered: `jq 'keys' ansible/vars/package-deps.json`
        → `["$schema", "picom", "qtile"]`.
  - [x] `ansible-playbook --check --diff --skip-tags packages
        ansible/playbook.yml` parses cleanly — the "Validate package and
        build-deps manifests" task is green (later become tasks need an
        interactive sudo password, unrelated to this change). All three
        packages confirmed present in trixie via `apt-cache policy`.
