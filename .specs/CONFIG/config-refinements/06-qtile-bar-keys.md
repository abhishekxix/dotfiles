# 06 — Qtile bar + keys polish (slice-4 look-and-feel)

| Field | Value |
|---|---|
| Status | Planning |
| Step | 06 |
| Commit | `CONFIG(06): qtile minute clock, single tray, trimmed layouts, media keys` |

## Files

- `.config/qtile/config_parts/screens.py` (EDIT)
- `.config/qtile/config_parts/keys.py` (EDIT)
- `.config/qtile/config_parts/layouts.py` (EDIT)

## Changes

1. Clock → minute precision (`%H:%M`, `update_interval=60`): today's
   `%H:%M:%S` (`screens.py:92`) redraws the whole bar 60×/min for a seconds
   display nobody reads.
2. Single tray backend: `StatusNotifier` + `Systray` both render
   (`screens.py:100-101`). Keep whichever renders this host's tray
   completely — census tray icons before/after, drop the other.
3. Trim the 9-layout list (`layouts.py`) to the 3–4 actually used (keep
   Columns/Max + one tiling + Floating) so Tab never lands on a focus-trap.
4. Add float rules for flameshot / nm-connection-editor / blueman (all
   missing from `build_floating_layout` today).
5. Add volume/brightness keys (`pactl`, sysfs backlight — no new deps; no
   brightnessctl per Non-goals) plus next-screen / window-to-screen /
   unminimize keys (`keys.py` ends at line 111 with none of these).

Out of scope: bar layout order, palette, mouse drag-hack, monitor logic
(dynamic-monitors owns that).

## Test

- `qtile check -c config.py`; reload, confirm the bar ticks once/min, single
  tray shows every icon, Tab cycles cleanly; press each new media/screen key.

## Acceptance

- [ ] bar redraws 1×/min; one tray backend with full icon census
- [ ] layouts cycle cleanly; media + screen keys work
