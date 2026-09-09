# 01 — drop indicator host, move client libs to qtile deps

- **Files:** `ansible/vars/packages.json` (EDIT), `ansible/vars/package-deps.json` (EDIT)
- **Changes:**
  - Delete the `ayatana-indicator-application` entry from `packages.json`
    (duplicate SNI host; qtile's own StatusNotifier/Systray widgets host the
    tray).
  - Delete the `libayatana-appindicator3-1` and
    `gir1.2-ayatanaappindicator3-0.1` entries from `packages.json` and declare
    them as `qtile` deps in `package-deps.json` instead (they are client-side
    libs needed by tray apps such as `pasystray` and `network-manager-applet`,
    not user-chosen tools).
  - Keep lexical order: remaining `packages.json` keys stay sorted, and the
    two new names are inserted at the head of the `qtile` dep list (before
    `lm-sensors`).
- **Test:** `jq` key-order checks on both files; `ansible-playbook --check
  --diff --skip-tags packages ansible/playbook.yml` parses cleanly with the
  "Validate package and build-deps manifests" task green.
- **Acceptance:**
  - [ ] `jq 'has("ayatana-indicator-application")' ansible/vars/packages.json`
        → `false`, and likewise for `libayatana-appindicator3-1` and
        `gir1.2-ayatanaappindicator3-0.1`.
  - [ ] `jq '.qtile' ansible/vars/package-deps.json` includes both
        `gir1.2-ayatanaappindicator3-0.1` and `libayatana-appindicator3-1`
        alongside the existing four entries.
  - [ ] Both files remain lexically ordered (top-level keys; `qtile` dep list
        sorted).
