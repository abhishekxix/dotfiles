# Reconcile apt install history into packages.json

| Field | Value |
|---|---|
| Status | Done |
| Component | ANSIBLE |
| Created | 2026-09-08 |

## Goal

Fold the packages the user has manually `apt install`ed over time (dumped in
`packages.txt`, 115 names) into the declarative installer, so a fresh machine
reproduces the current workstation without manual fix-ups. Plus `vim` (user
request, committed standalone before this spec).

## Context & Research

- Source: `packages.txt` at repo root (untracked scratch dump of apt history;
  NOT committed). Classification ran on Debian trixie, 2026-09-08.
- **Already covered — no action (34):**
  - in `packages.json` (14): alacritty, bat, curl, dunst, flameshot, fzf,
    lxsession, python3-pip, python3-venv, qtile, rofi, tmux, xbindkeys,
    xscreensaver
  - in `package-deps.json` (20): picom build deps (libconfig-dev,
    libdbus-1-dev, libegl-dev, libepoxy-dev, libev-dev, libgl-dev,
    libpcre2-dev, libpixman-1-dev, libx11-xcb-dev, libxcb*-dev ×12, meson,
    ninja-build, uthash-dev) + qtile deps (python3-dbus-fast, python3-psutil,
    python3-xdg)
- **Not installable / intentionally skipped — no entry (18):**
  - `compinit` (zsh function, not a package), `wish` (no such binary package),
    `python3-pydxg` (typo of python3-xdg)
  - `libappindicator`, `libappindicator3-1`, `gir1.2-appindicator3-0.1`
    (removed from Debian; the ayatana replacements are added in step 04)
  - `fonts-noto-emoji` (dropped from trixie; fonts-noto-color-emoji added)
  - `xbindkeys-config` (dropped from trixie)
  - `python3-dbus-next` (superseded by python3-dbus-fast), `python3-dbus`
    (apt Recommends of python3-qtile; pulled when needed), `lm-sensors` →
    handled as qtile dep in package-deps.json (step 09)
  - `python3-qtile-extras`, `qtile-extras` (not packaged in trixie; per
    qtile-python-deps spec decision)
  - `ansible-core` (the `install` wrapper bootstraps it; must not be a
    manifest entry)
  - `cursor`, `intellij-ide` (not Debian packages; user decision: skip)
  - GNOME suite: `gnome`, `gnome-core`, `gnome-session`,
    `gnome-session-xsession`, `gnome-software-plugin-flatpak`,
    `gnome-tweaks`, `task-gnome-desktop`, `nautilus-dropbox` (user decision:
    skip — qtile is the WM; `xdg-desktop-portal-gtk` stays)
- **Available in trixie and being added (grouped in steps 01–10).**
  apt components `main contrib non-free non-free-firmware` are all enabled on
  this machine (verified in /etc/apt/sources.list.d/debian.sources).
- **`packages1.txt` check (user follow-up, 2026-09-08):** ca-certificates and
  curl already tracked; docker-ce tracked with `repo: docker`; containerd.io
  and docker-ce-cli are hard Depends of docker-ce (implicit, skip);
  docker-buildx-plugin and docker-compose-plugin are only Recommends of
  docker-ce-cli → explicit entries in step 10; java-21-amazon-corretto-jdk →
  new `corretto` repo + entry in step 10 (repo auto-selected via
  playbook.yml:24; keyring path converges with the machine's existing
  corretto.list).
- **User decisions (2026-09-08):** hardware group → workstation profile;
  GNOME suite → skip; ttf-mscorefonts-installer → add WITH debconf EULA
  preseed; cursor/intellij-ide → skip; libappindicator family → install the
  ayatana replacements (step 04); fonts-noto*/fonts-indic confirmed already
  in step 03.
- Preseed pattern: `ansible.builtin.debconf` (builtin) setting
  `msttcorefonts/accepted-mscorefonts-eula=true`, gated the same way as the
  existing docker-group task (`'ttf-mscorefonts-installer' in dotfiles_pkgs_apt
  | map(attribute='value.package')`, cf. packages.yml:34-42), placed
  immediately before "Install apt packages". Without it, the postinst EULA
  prompt hangs/fails the non-interactive apt run. Note: the postinst downloads
  fonts from SourceForge at install time (network + sourceforge reachability
  required).
- `lxlock`/`lxpolkit` are LXDE session helpers in the same family as the
  already-tracked lxsession (lxpolkit is an lxsession Depends alternative).

## Non-goals

- No GNOME-suite entries (see Context); no cursor/intellij-ide.
- No `packages.txt` commit (scratch file, stays untracked).
- No changes to existing entries; lexical ordering of both vars files is
  preserved (AGENTS.md convention).
- No third-party repo additions (everything is in the Debian archive).

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

- [x] 01 — CLI/dev tools, workstation+server (01-cli-dev-tools.md)
- [x] 02 — audio stack, workstation (02-audio-stack.md)
- [x] 03 — fonts & themes, workstation (03-fonts-themes.md)
- [x] 04 — tray/network/indicator, workstation (04-tray-network.md)
- [x] 05 — desktop utilities & session bits, workstation (05-desktop-utilities.md)
- [x] 06 — media apps, workstation (06-media-apps.md)
- [x] 07 — hardware/driver stack, workstation (07-hardware-stack.md)
- [x] 08 — ttf-mscorefonts-installer + EULA preseed (08-mscorefonts-preseed.md)
- [x] 09 — lm-sensors as qtile dep (09-lm-sensors-qtile-deps.md)
- [x] 10 — docker buildx/compose plugins + Corretto JDK 21 (10-docker-plugins-corretto.md)

## Risks & Rollback

- All additions are plain apt entries — revert is `git revert` of the step.
- mscorefonts postinst fetches from SourceForge: flaky network fails the apt
  task; retry the run. EULA preseed must land before the apt transaction
  (step 08 handles both in one commit).
- nvidia/DKMS stack on a non-NVIDIA machine installs but is inert (headers +
  dkms build only when kernel modules are built); harmless on the localhost
  inventory this repo targets.
- Package-name typos fail loudly at the apt task; every name above was
  verified via `apt-cache policy` on trixie.
