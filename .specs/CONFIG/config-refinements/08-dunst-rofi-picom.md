# 08 — dunst follow + timeouts, rofi modes, picom rounding/blur

| Field | Value |
|---|---|
| Status | Planning |
| Step | 08 |
| Commit | `CONFIG(08): dunst follow/timeouts, rofi modes, picom rounding + cheap blur` |

## Files

- `.config/dunst/dunstrc` (EDIT)
- `.config/rofi/config.rasi` (EDIT)
- `.config/picom.conf` (EDIT)

## Changes

1. dunst `follow = keyboard` (focused monitor — `follow = none` + `monitor =
   0` pins everything to monitor 0 on a 2-screen setup); per-urgency
   `timeout` (low ~3s / normal ~8s / critical sticky); lower
   `notification_limit` from 20 to ~5; font to a Nerd-patched family matching
   the bar (`Ubuntu 10` lacks the Nerd glyphs the format strings assume).
2. rofi (`config.rasi` is a one-line theme import today): set `modes`
   (drun,run,window,ssh), listview lines/columns, sidebar mode to kill the
   jitter and fix the ungrabbable scrollbar.
3. picom: remove `Dunst` from the `corner-radius = 0` rule (the compositor
   currently undoes dunstrc's 16px rounding); drop `dual_kawase` → cheaper
   `box`/`gaussian` blur or weaken strength (kawase cost on iGPU). If the
   look regresses, keep kawase and only fix the Dunst rule.

## Test

- `dunstify` low/normal/critical on each monitor — placement + timeout correct.
- `rofi -show drun` stable with a visible scrollbar; `picom --diagnostics`;
   notifications keep rounded corners.

## Acceptance

- [ ] notifications follow focus with sane timeouts; rofi stable; dunst corners round
