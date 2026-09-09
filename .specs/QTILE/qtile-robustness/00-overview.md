# Qtile Robustness

| Field | Value |
|---|---|
| Status | Approved |
| Component | QTILE |
| Created | 2026-09-09 |

## Goal

Make Qtile boot and render safely on machines other than the author's
dual-monitor Intel + NVIDIA laptop — no hard failures from missing outputs,
audio devices, network interfaces, or backlight paths, and no WM startup
block on slow autostart lines.

## Context & Research

Third slice from the 2026-09-09 five-agent audit (qtile agent: 32 findings).
This spec covers robustness only (boot safely anywhere); look-and-feel
(clock tick, layout list, media keys, tray dedup, widgets) is slice 4.

Key facts (verified 2026-09-09 on this host):

1. **Net `interface=None` is combined mode.** `widget.Net` default
   `interface=None` means "all active NICs combined" (libqtile source,
   `ThreadPoolText` defaults). Dropping the hardcoded `wlo1` is the fix —
   no detection code needed.
2. **Backlight default is `acpi_video0`, also wrong here.** Widget default
   won't save us; `screens.py` needs a tiny helper picking the first entry
   of `/sys/class/backlight/` at config-load time, falling back to the
   current literal. This host has `intel_backlight`, so behavior here is
   unchanged.
3. **`startup_once` + `subprocess.run` blocks the WM.** `hooks.py:12` waits
   for the whole autostart script (xrandr + pactl + 10 tray apps) before
   Qtile finishes starting. `Popen` (fire-and-forget) is the standard
   pattern.
4. **Keyring line misses `&`.** `autostart.sh:9`
   `gnome-keyring-daemon --start ...` runs foreground, stalling every line
   below it on slow unlock.
5. **Echo-cancel is neither guarded nor idempotent.**
   `autostart.sh:29-30` loads `module-echo-cancel` with a hardcoded PCI
   path on every login — duplicates the module per login and kills audio
   setup on machines without that card. Guard: skip if a
   `module-echo-cancel` instance already exists (`pactl list modules`), and
   tolerate missing devices (`|| true` / device-exists check).
6. **`xrandr` single-layout line.** `autostart.sh:11` fails or mislays
   screens on any other dock/machine. Guard: only apply when both named
   outputs are connected (`xrandr --query` grep), else leave the server
   layout alone.
7. **`get_wm_class()` can return `None`.** `hooks.py:17`
   `"copyq" in window.get_wm_class()` raises `TypeError` on windows with no
   class. Guard with `or []`.
8. **Unguarded tray daemons + `xargs` without `-r`.** Any missing binary
   spams boot noise; `xargs xwallpaper < ~/.xwallpaper` runs bare
   `xwallpaper` on missing/empty file. Guards: `command -v` checks and
   `xargs -r` + file-exists check.

## Non-goals

- Do **not** change bar look, layouts, keybindings, or widgets (slice 4).
- Do **not** change the xrandr geometry values themselves — only guard when
  they apply.
- Do **not** remove echo-cancel on this machine — keep current audio behavior
  here, just make it safe elsewhere.
- Do **not** touch `settings.py` palette, `groups.py`, `layouts.py`,
  `keys.py`, `mouse.py`, `config.py` (except if a screens.py helper needs
  importing — prefer local helper in `screens.py`).
- Do **not** add new widgets or dependencies (`brightnessctl`, PulseVolume —
  slice 4 / desktop-consistency).

## Steps

Each step maps to exactly one commit, named `QTILE(<NN>): <summary>`.

### 01 — Non-blocking autostart + keyring background

- **Files:** `.config/qtile/config_parts/hooks.py` (EDIT), `.config/qtile/autostart.sh` (EDIT)
- **Changes:** `subprocess.run` → `Popen` (fire-and-forget, no wait);
  append `&` to the `gnome-keyring-daemon` line.
- **Test:** `python3 -m py_compile config_parts/hooks.py`; `bash -n autostart.sh`; restart Qtile, confirm desktop ready before tray apps finish
- **Acceptance:**
  - [ ] Qtile responsive immediately at login; keyring still unlocks (ssh/keyring works)

### 02 — Guard xrandr + tray daemons + xwallpaper

- **Files:** `.config/qtile/autostart.sh` (EDIT)
- **Changes:** run the `xrandr` line only when both `HDMI-0` and `eDP-1-1`
  are connected; guard each tray daemon with `command -v`; `xwallpaper`
  only when `~/.xwallpaper` exists and non-empty (`xargs -r`).
- **Test:** `bash -n autostart.sh`; run with a fake `PATH` missing one daemon, confirm no error spam; run on single-monitor, confirm xrandr skipped
- **Acceptance:**
  - [ ] clean boot log with missing binaries; single-monitor leaves server layout alone; dual-monitor applies current geometry unchanged

### 03 — Idempotent echo-cancel

- **Files:** `.config/qtile/autostart.sh` (EDIT)
- **Changes:** skip `pactl load-module module-echo-cancel` when an instance
  already exists; tolerate missing ALSA devices without failing the script;
  only `set-default-source` when the echo-cancel source exists.
- **Test:** run autostart twice, `pactl list modules | grep -c echo-cancel` stays 1; `bash -n autostart.sh`
- **Acceptance:**
  - [ ] no duplicate modules across logins; current audio behavior on this host unchanged

### 04 — Net all-interfaces + backlight autodetect

- **Files:** `.config/qtile/config_parts/screens.py` (EDIT)
- **Changes:** drop `interface="wlo1"` (falls back to combined mode);
  pick backlight name from first `/sys/class/backlight/*` entry, falling
  back to `"intel_backlight"`.
- **Test:** `python3 -m py_compile config_parts/screens.py`; `qtile check -c config.py` if available; on this host bar shows same Net totals and same brightness control
- **Acceptance:**
  - [ ] no widget errors in `~/.local/share/qtile/qtile.log`; Net + Backlight behave as before on this host, render something sane on other hardware

### 05 — None-safe copyq hook

- **Files:** `.config/qtile/config_parts/hooks.py` (EDIT)
- **Changes:** guard `window.get_wm_class()` against `None` before the
  `"copyq" in ...` test.
- **Test:** `python3 -m py_compile config_parts/hooks.py`; open a class-less window (e.g. xmessage), confirm no traceback in qtile log
- **Acceptance:**
  - [ ] no `TypeError` in log on any new window; copyq still pulled to current group

## Risks & Rollback

- **Popen autostart (step 01):** race — tray apps may start after bar
  widgets query them (e.g. Systray). Previous behavior had the same race
  window inverted (WM late instead). Low risk; revert restores blocking.
- **xrandr guard (step 02):** string-match on `xrandr --query` output is
  brittle across drivers; keep the match to `\<OUTPUT\> connected`.
  Revert restores unconditional (breaks elsewhere, works here).
- **Backlight helper (step 04):** runs at config-load; if
  `/sys/class/backlight` is empty (desktop), falls back to literal which
  errors as today — no worse. Could hide the widget instead; deferred to
  slice 4.
- **Net combined mode (step 04):** totals differ from wlo1-only on
  multi-NIC hosts (docker bridges add noise). Acceptable for robustness;
  slice 4 may add an interface picker.

Each step is its own commit, so `git revert` or `git bisect` localizes any
regression.
