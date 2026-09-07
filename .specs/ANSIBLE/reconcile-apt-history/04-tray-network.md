# 04 — tray/network/indicator stack, workstation

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** Add five workstation apt entries — the ayatana replacements for
  the removed libappindicator family (user decision: "install what replaces
  them"), plus blueman and the nm applet:
  `ayatana-indicator-application`, `blueman`,
  `gir1.2-ayatanaappindicator3-0.1`, `libayatana-appindicator3-1`,
  `network-manager-applet`.
  (`libayatana-indicator3-7` arrives as a dependency of the appindicator lib.)
- **Acceptance:**
  - [ ] `jq -e 'keys == (keys | sort)' ansible/vars/packages.json` passes.
  - [ ] All five keys present with `profiles: ["workstation"]`.
  - [ ] Playbook check-mode parse clean (manifest validation green).
