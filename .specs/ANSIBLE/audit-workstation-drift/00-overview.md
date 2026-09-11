# Audit workstation drift into packages manifest

| Field | Value |
|---|---|
| Status | Done |
| Component | ANSIBLE |
| Created | 2026-09-11 |

## Goal

Fold packages this machine has but the manifest lacks — per the 2026-09-11
audit and the user's quiz answers — into `packages.json`, and decide the fate
of two manual installs (JetBrains Toolbox, pre-commit venv).

## Context & Research

- Audit method (2026-09-11): `apt-mark showmanual` minus manifest apt
  entries minus `package-deps.json` entries; `flatpak list --app`; zsh history
  for source builds; `/usr/local/bin`, `~/.local/bin`, `~/.cargo/bin`,
  `npm -g`, pip venvs.
- Flatpak apps: okular + obsidian — both tracked (flatpak source). Only
  runtimes otherwise. No gap.
- Source builds: picom (git+yashui, tracked), starship (script, tracked),
  zsh plugins (git, tracked), tree-sitter/fnm (cargo, tracked), neovim
  (archive, tracked), claude/opencode (script, tracked). No gap.
- User quiz answers: CLI core+diagnostics yes; gdm3+network-manager+printing
  +avahi yes; firmware+microcode yes; apps file-roller/seahorse/
  easyeffects+calf/loupe/shotwell/totem yes; gnome-terminal/tweaks no;
  toolbox track yes; pre-commit leave as-is.
- Full unaccounted-manual list (324 names) triaged in the audit; base-system,
  GNOME-shell, -dev/build-dep, lib*, locale, task-* and installer-managed
  entries skipped as non-manifest material.

## Non-goals

- No GNOME-shell suite entries (prior user decision, reconcile-apt-history).
- No base-system/libs/locales/tasks entries; no -dev/build-dep entries
  (those belong in package-deps.json only if a from-source build needs them).
- No pre-commit tracking (user decision: leave venv as-is).
- No changes to existing entries; lexical ordering preserved.

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

### 01 — CLI tools + diagnostics

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** add apt entries (workstation; server profile for the server-sensible subset): openssh-client, man-db, manpages, bash-completion, wget, lsof, pciutils, usbutils, bind9-dnsutils, netcat-traditional, traceroute, apt-listchanges, apt-utils.
- **Test:** `.bin/validate-manifest.py` (or pre-commit hook on the JSON edit)
- **Acceptance:**
  - [ ] validator passes; entries lexically ordered with correct fields

### 02 — desktop infra + printing + avahi

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** add workstation apt entries: gdm3 (running DM), network-manager (backend of tracked applet), cups, cups-pk-helper, system-config-printer-common, system-config-printer-udev, avahi-daemon.
- **Test:** `.bin/validate-manifest.py`
- **Acceptance:**
  - [ ] validator passes; entries lexically ordered

### 03 — firmware + microcode

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** add workstation apt entries: firmware-intel-graphics, firmware-iwlwifi, firmware-realtek, firmware-sof-signed, intel-microcode.
- **Test:** `.bin/validate-manifest.py`
- **Acceptance:**
  - [ ] validator passes; entries lexically ordered

### 04 — desktop apps

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** add workstation apt entries: file-roller, seahorse, easyeffects, calf-plugins, loupe, shotwell, totem, totem-plugins.
- **Test:** `.bin/validate-manifest.py`
- **Acceptance:**
  - [ ] validator passes; entries lexically ordered

### 05 — jetbrains toolbox (DROPPED)

- Dropped 2026-09-11: no stable download URL (versioned tarballs only) and
  the app self-updates in place — a pinned archive entry would rot. Toolbox
  stays a manual install.

## Risks & Rollback

- All steps except 05 are plain apt entries — revert is `git revert` of the step.
- gdm3 entry only reproduces the current DM; harmless on machines using another DM.
- Step 05 needs an install-source decision (archive vs script) at plan time; if no clean URL exists, drop the step with user sign-off.
- Firmware/microcode entries are inert on non-matching hardware.
