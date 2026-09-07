# 09 — lm-sensors as qtile dep

- **Files:** `ansible/vars/package-deps.json` (EDIT)
- **Changes:** Extend the existing `"qtile"` deps array with `lm-sensors`
  (it is an apt Recommends of `python3-qtile` and feeds the qtile sensors
  widget). Keep the array lexically sorted:

  ```json
  "qtile": [
    "lm-sensors",
    "python3-dbus-fast",
    "python3-psutil",
    "python3-xdg"
  ]
  ```
- **Acceptance:**
  - [ ] `jq '.qtile' ansible/vars/package-deps.json` lists exactly the four
        packages above.
  - [ ] Top-level keys remain sorted (`$schema`, `picom`, `qtile`).
  - [ ] Playbook check-mode parse clean (build-deps manifest validation green).
