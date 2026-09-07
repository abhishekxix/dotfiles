# 02 — audio stack, workstation

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** Add nine workstation apt entries: `calf-plugins`, `cava`,
  `easyeffects`, `pasystray`, `pavucontrol`, `playerctl`,
  `pulseaudio-equalizer`, `pulseaudio-utils`, `volumeicon-alsa`.
- **Acceptance:**
  - [x] `jq -e 'keys == (keys | sort)' ansible/vars/packages.json` passes.
  - [x] All nine keys present with `profiles: ["workstation"]`.
  - [x] Playbook check-mode parse clean (manifest validation green).
