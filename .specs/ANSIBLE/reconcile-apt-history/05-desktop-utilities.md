# 05 — desktop utilities & session bits, workstation

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** Add seven workstation apt entries: `copyq`, `libnss3-tools`,
  `lxlock`, `lxpolkit`, `xclip`, `xdg-desktop-portal-gtk`, `xwallpaper`.
  (`xdg-desktop-portal-gtk` is the portal backend qtile needs for
  screenshots/file choosers; `lxlock`/`lxpolkit` complete the lxsession
  family already tracked.)
- **Acceptance:**
  - [ ] `jq -e 'keys == (keys | sort)' ansible/vars/packages.json` passes.
  - [ ] All seven keys present with `profiles: ["workstation"]`.
  - [ ] Playbook check-mode parse clean (manifest validation green).
