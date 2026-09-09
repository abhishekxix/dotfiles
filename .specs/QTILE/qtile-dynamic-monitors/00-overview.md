# Qtile Dynamic Monitors

| Field | Value |
|---|---|
| Status | Done |
| Component | QTILE |
| Created | 2026-09-09 |

## Goal

Qtile follows monitor hotplug: connecting/disconnecting the external display
reconfigures outputs via xrandr automatically, the internal panel always runs
at 120Hz, and the `a/s/d/f/g` groups live on the external display when
present, collapsing onto the internal display when it is the only screen.

## Context & Research

User request (2026-09-09), supersedes the static xrandr guard from
`qtile-robustness` step 02. Decisions confirmed with user:

1. **Main = internal panel.** `eDP-1-1` (laptop) is always primary at 120Hz;
   the external extends it (current geometry: external left, internal right).
2. **Auto = preferred resolution at max refresh.** Each output gets its
   preferred mode (`+` marker) at the highest rate that mode offers —
   parsed from `xrandr --query`, applied as `--mode <pref> --rate <max>`.
   (`--auto` alone picks preferred mode but not necessarily max rate, so
   explicit mode+rate it is.) No hardcoded resolutions or rates anywhere.
3. **Generic outputs.** Detect any internal (`eDP-*`, `LVDS-*`) vs any
   external (`HDMI-*`, `DP-*`, `DisplayPort-*`) — not hardcoded names.

Key facts (verified 2026-09-09 on this host):

1. **`reconfigure_screens = True` already set** (`config.py:51`) — Qtile
   rebuilds its screen objects on RandR changes by itself. What is missing
   is (a) applying output modes via xrandr, and (b) moving the secondary
   groups when the screen count changes.
2. **Groups already handle single-screen.** `go_to_group` / `move_window_to_group`
   (`groups.py:21-52`) call `toscreen()` when `len(screens) == 1`, so with one
   monitor every group is reachable — but `screen_affinity=1` on the
   secondary groups fights this: affinity pulls them back to a nonexistent
   screen. Fix: drop `screen_affinity` from the secondary groups (or set at
   runtime in the screen-change hook) so single-screen `toscreen()` sticks.
3. **Hook point: `screen_change`.** libqtile fires `screen_change` on RandR
   events — the hook runs xrandr auto-config, then reassigns secondary
   groups to screen 1 (if two screens) or screen 0 (if one). Must be
   idempotent and fast (xrandr round-trip per hotplug is fine).
4. **Current modes on this host** (`xrandr --query`): HDMI-0 preferred
   2560x1440@74.96; eDP-1-1 preferred 1920x1080@120.04. Auto-config
   reproduces today's setup: external `--auto` left, internal preferred
   mode @120 primary right.
5. **Second `Screen` only when external connected.** `build_screens` returns
   one `Screen` (all 10 groups visible) when solo, two Screens (5+5 split)
   when an external is connected. Determined at config-load via
   `xrandr --query`; `reconfigure_screens = True` rebuilds on hotplug, but
   a config reload (`mod+ctrl+r`) after dock/undock converges to the right
   count — the `screen_change` hook (step 02) triggers `qtile.reload_config()`
   when the screen count changes so the bar layout follows automatically.
6. **Max-rate parsing.** For each connected output, take the preferred mode
   (the resolution line with the `+` marker) and the highest rate listed on
   that line. On this host: HDMI-0 → 2560x1440@74.96, eDP-1-1 →
   1920x1080@120.04 — reproduces today's setup with zero hardcoded numbers.
   If parsing fails for an output, fall back to `--auto` for that output.

## Non-goals

- Do **not** change bar content, layouts, keybindings, or widgets (slice 4).
- Do **not** persist multi-dock profiles (per-dock geometry memory) — one
  generic layout: external left of internal.
- Do **not** touch autostart tray daemons, echo-cancel, Net/Backlight
  (slice 3, done).
- Do **not** rename outputs or change group names/bindings.

## Steps

Each step maps to exactly one commit, named `QTILE(<NN>): <summary>`.

### 01 — xrandr auto-config helper script

- **Files:** `.config/qtile/config_parts/monitors.py` (CREATE — shell out to xrandr from Python)
- **Changes:** `configure_monitors()` + query helpers (`connected_outputs()`,
  `preferred_mode_and_max_rate()`, all pure over `xrandr --query` text).
  Logic: internal → `--primary` + preferred mode @ max rate; external →
  preferred mode @ max rate positioned left of internal; solo internal →
  preferred mode @ max rate. `--auto` fallback per-output if parsing fails.
  Compares current state before applying (no-op when already correct —
  avoids `screen_change` loops).
- **Test:** run with both connected (reproduces current layout: 1440p@75 +
  1080p@120), simulate single-screen by feeding a canned `xrandr --query`
  with external disconnected (unit-test the parsing, not the hardware)
- **Acceptance:**
  - [x] dual setup matches today's geometry with zero hardcoded modes; script idempotent (no-op on second run)

### 02 — screen_change hook + conditional second Screen + groups

- **Files:** `.config/qtile/config_parts/hooks.py` (EDIT), `.config/qtile/config_parts/groups.py` (EDIT), `.config/qtile/config_parts/screens.py` (EDIT)
- **Changes:** `build_screens` returns one `Screen` (all 10 groups in one
  GroupBox) when no external is connected, two Screens (5+5 split) when one
  is — decided at config-load from `xrandr --query`. `@hook.subscribe.screen_change`
  → call `configure_monitors()`, then: two screens → secondary groups
  (`a/s/d/f/g`) to screen 1; one screen → all groups to screen 0. If the
  screen count changed, `qtile.reload_config()` so the bar layout converges.
  Drop static `screen_affinity=1` from secondary groups (it fights
  single-screen `toscreen()`); the hook owns placement instead.
- **Test:** `python3 -m py_compile` all three files; live: unplug external,
  confirm single bar with all 10 groups on internal; replug, confirm two
  bars (5+5) without manual sorting
- **Acceptance:**
  - [x] unplug → one Screen, all 10 groups visible on internal; replug → two Screens, 1-5 internal, a-g external; no manual `toscreen()` needed (confirmed 2026-09-09 live; hook re-shows 1/a after placement)

### 03 — Replace static xrandr guard in autostart

- **Files:** `.config/qtile/autostart.sh` (EDIT)
- **Changes:** replace the slice-3 connected-outputs `xrandr` block with a
  call to the step-01 helper (same generic logic at login as on hotplug —
  one code path, not two).
- **Test:** `bash -n autostart.sh`; logout/login with and without external, confirm layout correct both ways
- **Acceptance:**
  - [x] login-time layout identical to hotplug layout; no duplicated xrandr logic (confirmed 2026-09-09 live: dual login, solo login, disconnect, reconnect, solo→dual — all converge; wallpaper race fixed by foreground monitor layout in 8f255c0)

### 04 — hotplug hardening: stale framebuffer + hook convergence guards

- **Files:** `.config/qtile/config_parts/monitors.py` (EDIT), `.config/qtile/config_parts/hooks.py` (EDIT)
- **Changes:** NVIDIA keeps stale geometry on the unplugged output's
  `disconnected` line and rejects `--off` (driver re-adds the output ~1s
  later; a second `--off` corrupts the panning domain) — so never emit
  `--off`; instead shrink the framebuffer (`--fb` to the internal panel's
  preferred mode) when a stale-geometry output keeps it wide, skipping when
  already solo-sized. `configure_monitors()` returns True only if an xrandr
  command actually succeeded (a rejected `--fb` reports False so the hook
  falls through to group placement instead of early-returning every event).
  Hook: re-entry lock only — no cooldown (the earlier 5s cooldown ate the
  follow-up RandR event our own xrandr fires in the same second, so
  placement + reload never ran after replug) and no per-plug-state reload
  guard (reload fires only on screen-count change, which already converges).
  If our own xrandr change succeeded, return early — placement + reload
  happen on the follow-up event against qtile's rebuilt screen list —
  except when the screen count already matches (driver applied geometry
  synchronously), in which case fall through instead of waiting for an
  event that may never come. Group placement is by geometry, not index:
  new `current_rects()` helper parses `xrandr --listmonitors` output
  (CRTC order — panel first on this host — which matches qtile's own
  screen enumeration; a left-to-right sort would put the external first
  and swap the bars). The hook maps each rect to its `qtile.screens`
  index by geometry and sends primary groups to the panel index,
  secondary groups to the external index. `build_screens` keeps panel
  first for the same reason (comment-only change in `screens.py`).
  Canned-query `_selfcheck()` (`--selfcheck`): dual/fixed-solo no-op,
  broken-solo → fb-only and never `--off`, rc-aware configure.
- **Test:** `python3 .config/qtile/config_parts/monitors.py --selfcheck`;
  `python3 -m py_compile` both files; live: unplug/replug, confirm no
  reload loop and single bar converges
- **Acceptance:**
  - [x] selfcheck passes (dual/fixed no-op, broken→fb-only, rc-aware);
    no `--off` emitted in any plan
  - [x] live unplug → one Screen converges without a reload loop; replug → two Screens (confirmed 2026-09-09 live)

## Risks & Rollback

- **screen_change loops:** if `configure_monitors()` itself triggers RandR
  events, the hook refires — and step 02 adds `reload_config()` on count
  change, which refires everything. Mitigation: `configure_monitors()` is a
  no-op when state already matches; reload only when the count actually
  changed. Revert restores static behavior.
- **reload_config on hotplug:** a full config reload re-runs autostart? No —
  `startup_once` fires once per Qtile process, reloads don't retrigger it.
  But reload does rebuild all bars (visible flicker, ~1s). Accepted cost of
  converging the Screen count; alternative (static 2 Screens, hide one) left
  as fallback if flicker annoys.
- **Explicit mode+rate vs `--auto`:** `--auto` picks the preferred mode but
  the driver chooses the rate (not always max). Explicit
  `--mode <pref> --rate <max>` guarantees max refresh; per-output `--auto`
  fallback covers unparsable outputs.
- **Group affinity removal:** dropping `screen_affinity=1` changes initial
  placement at first start before any hotplug event — mitigated because
  `startup_once` (or the first `screen_change`) runs placement immediately.
- **External-left assumption:** docks/projectors get the same
  left-of-internal layout; acceptable per Non-goals (no profiles).

Each step is its own commit, so `git revert` or `git bisect` localizes any
regression.
