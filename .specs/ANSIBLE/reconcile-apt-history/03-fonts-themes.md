# 03 — fonts & themes, workstation

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** Add ten workstation apt entries: `breeze`, `fonts-indic`,
  `fonts-noto-cjk`, `fonts-noto-cjk-extra`, `fonts-noto-color-emoji`,
  `fonts-ubuntu`, `lxappearance`, `papirus-icon-theme`, `qt6ct`,
  `yaru-theme-gtk`.
- **Acceptance:**
  - [ ] `jq -e 'keys == (keys | sort)' ansible/vars/packages.json` passes.
  - [ ] All ten keys present with `profiles: ["workstation"]`.
  - [ ] Playbook check-mode parse clean (manifest validation green).
