# Conditional Hardware Widgets + Picom Guard

| Field | Value |
|---|---|
| Status | Done |
| Component | QTILE |
| Created | 2026-09-10 |

## Goal

Qtile's bar and compositor degrade gracefully on hardware-poor machines:
widgets whose hardware is absent are omitted at config-load, and picom is
skipped at login inside VMs or when no GPU (`/dev/dri`) exists.

## Context & Research

Follow-up to `qtile-robustness` (slice 3, Approved) which made Net
interface-agnostic and backlight autodetected but left all widgets
unconditional, and to `config-refinements` step 08 (dunst/rofi/picom look
tweaks). Requested 2026-09-10; user confirmed: VM check via
`systemd-detect-virt` **plus** a `/dev/dri` GPU check for picom.

Key facts (verified 2026-09-10 in-tree):

1. `screens.py` builds one fixed widget list: `Net`, `Memory`,
   `ThermalSensor`, `NvidiaSensors`, `Battery`, `Backlight`, `Clock`,
   optional `Systray`, `CurrentLayoutIcon`. `_detect_backlight()` already
   probes `/sys/class/backlight/*` but falls back to a literal that errors
   on desktops with no backlight device.
2. `autostart.sh` launches picom via `try_launch picom` (binary-exists
   check only). `picom.conf` pins `backend = "glx"`, which needs a real
   GPU — in a VM or on DRI-less hardware picom either fails or falls back
   to CPU-burning software paths.
3. Probes run at Qtile config-load (Python, cheap `glob`/`shutil.which`)
   and at autostart (bash, `systemd-detect-virt --quiet` exit code +
   `/dev/dri/card*` glob). No new dependencies.

## Non-goals

- Do **not** change bar look, order, or formats on this host — every probe
  is true here, so the bar renders identically.
- Do **not** add an xrender/software fallback for picom — the request is
  disable-when-unrunnable, not degrade-the-backend.
- Do **not** touch monitor logic (`monitors.py`), hooks, keys, layouts,
  groups, or picom.conf rules.
- Do **not** probe Network/Memory/Clock/Systray — they are
  hardware-independent.

## Steps

Each step maps to exactly one commit, named `QTILE(<NN>): <summary>`.

### 01 — conditional hardware widgets

- **Files:** `.config/qtile/config_parts/screens.py` (EDIT)
- **Changes:** tiny `_has_*` probes (`BAT*` in `/sys/class/power_supply`,
  non-empty `/sys/class/backlight`, `nvidia-smi` on PATH,
  `thermal_zone*`/`hwmon*` present); append each widget plus its leading
  separator only when its probe passes. Reuse `_detect_backlight()` for
  the backlight name when present.
- **Test:** `python3 -m py_compile config_parts/screens.py`; mock the
  probes off/on and confirm the widget list shrinks/grows with no stray
  separators; `qtile check -c config.py` if available
- **Acceptance:**
  - [ ] this host: bar identical (all probes true, no log errors)
  - [ ] all probes false: bar renders Net/Memory/Clock/layout only, no
    traceback in `~/.local/share/qtile/qtile.log`

### 02 — skip picom in VMs / without DRI

- **Files:** `.config/qtile/autostart.sh` (EDIT)
- **Changes:** replace bare `try_launch picom` with a guard: skip when
  `systemd-detect-virt --quiet` succeeds (VM/container) or no
  `/dev/dri/card*` exists; otherwise `try_launch picom` as today. Fail
  open if `systemd-detect-virt` is missing (assume bare metal).
- **Test:** `bash -n autostart.sh`; fake `systemd-detect-virt` true/false
  and empty `/dev/dri` glob, confirm picom launched/skipped accordingly
- **Acceptance:**
  - [ ] this host: picom launches as before
  - [ ] forced-VM / no-DRI simulation: picom skipped, rest of autostart
    unaffected

## Risks & Rollback

- **Probe false-negative (step 01):** an exotic path (e.g. `BAT1` under a
  different sysfs class) hides a working widget. Probes use the canonical
  kernel paths; revert restores unconditional widgets.
- **`systemd-detect-virt` on non-systemd (step 02):** missing binary →
  fail open (launch picom), today's behavior. A bare-metal box without
  `/dev/dri` (headless X?) skips picom — intended, revert restores launch.
- Each step is its own commit, so `git revert` localizes any regression.
