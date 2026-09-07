# 06 — media apps, workstation

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** Add five workstation apt entries: `ffmpeg`,
  `libavcodec-extra`, `obs-studio`, `okular`, `flatpak`.
- **Acceptance:**
  - [x] `jq -e 'keys == (keys | sort)' ansible/vars/packages.json` passes.
  - [x] All five keys present with `profiles: ["workstation"]`.
  - [x] Playbook check-mode parse clean (manifest validation green).
