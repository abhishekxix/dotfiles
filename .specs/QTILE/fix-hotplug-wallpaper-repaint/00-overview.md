# Hotplug Wallpaper Repaint

| Field | Value |
|---|---|
| Status | In progress (code in; live plug/unplug check pending) |
| Component | QTILE |
| Created | 2026-09-11 |

## Goal

Repaint the wallpaper after a monitor hotplug reconfigures the framebuffer, so connecting the external display no longer leaves the image smeared.

## Context & Research

Report (2026-09-11): log in to qtile solo, then connect the external screen → wallpaper smeared.

Root cause (verified in-tree, no guessing):

1. `autostart.sh:44-52` paints per-output `--zoom` wallpaper once at login,
   after the foreground monitor layout — the login race was already fixed
   (spec `qtile-dynamic-monitors` step 03, commit `8f255c0`).
2. `config_parts/hooks.py:_reconfigure_on_hotplug_inner` calls
   `configure_monitors()` on every `screen_change` but never repaints the
   wallpaper. The replug resizes the framebuffer (1920x1080 → 4480x1440)
   under the old pixmap, so X stretches the stale image — the smear.
3. `monitors.py --selfcheck` passes; layout geometry itself is correct
   (live `xrandr --query` shows HDMI-0 2560x1440+0+0, eDP-1-1
   1920x1080+2560+360). Only the repaint is missing.

So the fix is one missing call on the hotplug path, not a layout bug.

## Non-goals

- Do **not** change monitor geometry, mode/rate selection, `--fb` shrink,
  group placement, or reload logic.
- Do **not** change login-time painting order in `autostart.sh` (it works).
- Do **not** add wallpaper daemons, timers, or new dependencies
  (`xwallpaper` stays; `-r`-style empty-file guard stays).

## Steps

Each step maps to exactly one commit, named `QTILE(<NN>): <summary>`.

### 01 — repaint wallpaper after hotplug xrandr

- **Files:** `.config/qtile/config_parts/hooks.py` (EDIT)
- **Changes:** after `configure_monitors()` reports a change (and on the
  follow-up event where the count already matched), re-run the same
  per-output `--zoom` repaint `autostart.sh` uses, reading
  `~/.xwallpaper`, skipping when the file is missing/empty. Fire-and-forget
  (`Popen`) so the hook never blocks on painting. Share one code path with
  autostart if cheap (tiny helper); otherwise duplicate the ~6-line loop —
  no new abstraction for one call site pair.
- **Test:** `python3 -m py_compile config_parts/hooks.py`; `bash -n autostart.sh` if touched; live: login solo → plug external → wallpaper crisp on both outputs; unplug → crisp solo
- **Acceptance:**
  - [ ] replug repaints per-output `--zoom` (no smear, no `--stretch`)
  - [ ] missing/empty `~/.xwallpaper` runs nothing, hook still converges bars/groups as today
  - [ ] hook stays non-blocking (no `run`/wait on the paint command)

## Risks & Rollback

- **Paint before framebuffer settles:** same race autostart already solved
  by painting after xrandr; hook paints only after `configure_monitors()`
  returns/applies, and the follow-up event repaints against settled geometry.
- **Extra paint on no-op events:** gate on actual change/count-match so
  routine RandR noise doesn't respawn painters; worst case is one redundant
  background repaint.
- One commit → `git revert` restores today's behavior.
