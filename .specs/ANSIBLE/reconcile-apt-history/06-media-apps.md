# 06 — media apps, workstation

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** Add five workstation apt entries: `ffmpeg`,
  `libavcodec-extra`, `obs-studio`, `okular`, `flatpak`.
- **Acceptance:**
  - [ ] `jq -e 'keys == (keys | sort)' ansible/vars/packages.json` passes.
  - [ ] All five keys present with `profiles: ["workstation"]`.
  - [ ] Playbook check-mode parse clean (manifest validation green).
