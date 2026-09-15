# GH-29: rofi/dunst, hardware keys, session autostart

| Field | Value |
|---|---|
| Status | Approved |
| Component | CONFIG |
| Created | 2026-09-16 |
| Issue | GH-29 (part 4/8 of #25 split) |
| Verification notes | None |

> Use exactly one status: `Planning`, `Approved`, `In progress`, or `Done`.
> After approval, the Goal, Context, Non-goals, step text, acceptance text, and
> Risks are frozen; changes need re-approval. Status, checkbox state, and
> Verification notes remain mutable. Keep that implementation bookkeeping
> uncommitted until the user approves a final `SPECS` commit.

## Goal

Finish GH-29: wire dunst actions/idle/fullscreen policy, convert xbindkeys to
symbolic-only bindings, and give the login session a single coherent
ownership story (`.xsessionrc` env, keyring SSH, guarded dual autostart).

## Context & Research

Split of PR #25 (spec steps 08–10 of the former `config-qol-updates/` spec,
which no longer exists in `.specs/`). Verified against the tree on
2026-09-16:

1. **Rofi done already**: `config.rasi` sets `modes drun,run,window,ssh`,
   `sidebar-mode`, `lines: 12`, `scrollbar-width` — matches all 4 launchers
   in `settings.py`. Catppuccin theme is complete. Per user decision: no rofi
   changes in this spec.
2. **dunst pending**: `dmenu = /usr/bin/dmenu` (line 244) but the desktop uses
   rofi — no dmenu package installed. `idle_threshold` commented out (line
   132); `[transient_disable]` rule commented out (lines 408–410);
   `[fullscreen_delay_everything]` / `[fullscreen_show_critical]` commented
   out (lines 424–428). Per-urgency `timeout` (3/8/0) and
   `notification_limit = 5` already in place — not touched.
3. **xbindkeys pending**: every binding lists BOTH a raw `m:0x0 + c:NNN` line
   and a symbolic name (duplicate triggers, keycode fragility across
   keyboards). No `XF86AudioRaise/Lower/Mute` sink-volume bindings exist
   (only mic + player keys) — per user decision, volumeicon owns sink volume,
   so no new volume bindings are added.
4. **Session pending**: `home/.xsessionrc` missing (XDG vars live in
   `autostart.sh` lines 3–5 instead). `desktop.conf` sets
   `keyring/command=ssh-agent` while `autostart.sh` starts
   `gnome-keyring-daemon ... --components=pkcs11,secrets,ssh` — two SSH
   owners. `autostart.sh` launches 9 daemons AND lxsession autostarts with
   `disable_autostart=no` — double-start risk. Per user decisions: keyring
   owns SSH, and the dual launchers stay but each daemon gets a
   single-instance guard.

## Non-goals

- Do **not** touch rofi config or theme (already correct — user decision).
- Do **not** add sink-volume key bindings (volumeicon owns that — user decision).
- Do **not** change lock/suspend `&&` chains (already abort-safe — user decision).
- Do **not** change dunst timeouts, `notification_limit`, `follow`, fonts, or
  urgency colors (owned by the config-refinements spec / already set).
- Do **not** add new daemons or packages (no dmenu install — rofi covers it).
- Do **not** move daemons between autostart.sh and lxsession (both stay, guarded).

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

### 01 — dunst rofi-actions + idle/fullscreen policy

- **Files:** `.config/dunst/dunstrc` (EDIT)
- **Changes:** point `dmenu` at `rofi -dmenu -p dunst` so notification actions
  use the desktop's launcher; enable `idle_threshold` (120s) plus the
  `[transient_disable]` rule so idle users aren't interrupted and clients
  can't bypass the queue; enable `[fullscreen_delay_everything]` and
  `[fullscreen_show_critical]` so normal notifications wait out fullscreen
  while critical ones always show.
- **Test:** `dunst -print` parses clean on save; on Debian/X11 target:
  `dunstify` low/normal/critical, idle past threshold, action prompt,
  fullscreen video — placement, prompt, and deferral correct.
- **Acceptance:**
  - [ ] `dunst -print` (or config parse) shows no errors
  - [ ] actions invoke via rofi; idle holds non-critical; fullscreen delays normal, shows critical (manual, target machine)

### 02 — xbindkeys symbolic-only bindings

- **Files:** `home/.xbindkeysrc` (EDIT)
- **Changes:** delete every raw `m:0x0 + c:NNN` keycode line, keeping the
  symbolic `XF86*` / `Mod4` / `Control+Alt` names. No binding semantics
  change; no new volume bindings (volumeicon owns sink volume); lock/suspend
  `&&` chains untouched.
- **Test:** `xbindkeys --key` parses the file on target; each symbolic binding
  (brightness, mic, player, flameshot, lock, dunst) fires once per press.
- **Acceptance:**
  - [ ] file contains no `m:0x... + c:...` keycode lines
  - [ ] every binding fires exactly once on the target machine (manual)

### 03 — session env + keyring SSH + guarded autostart

- **Files:** `home/.xsessionrc` (CREATE), `.config/lxsession/qtile/desktop.conf` (EDIT), `.config/qtile/autostart.sh` (EDIT)
- **Changes:** create `.xsessionrc` owning the minimal login env (XDG_*
  vars); remove `keyring/command=ssh-agent` from `desktop.conf` so
  gnome-keyring (already started with the ssh component in `autostart.sh`)
  is the single SSH owner; add single-instance (`pgrep`-style) guards around
  each daemon launch in `autostart.sh` so the lxsession + autostart.sh dual
  ownership can't double-start daemons.
- **Test:** `shellcheck home/.xsessionrc .config/qtile/autostart.sh`;
  `bash -n home/.xsessionrc`; fresh login on Debian target:
  env present, single `SSH_AUTH_SOCK`, one instance per daemon.
- **Acceptance:**
  - [ ] `shellcheck` clean on `.xsessionrc` and `autostart.sh`
  - [ ] fresh login: XDG env set, one SSH agent, single daemon instances (manual, target machine)

## Risks & Rollback

- **rofi -dmenu (step 01):** action prompt styling follows the rofi theme;
  if it misbehaves, revert the one line to `/usr/bin/dmenu`.
- **idle_threshold (step 01):** notifications queue while idle up to history
  limits; `dunstctl history-pop` (already bound to Mod4+grave) drains them.
- **Symbolic-only keys (step 02):** if a keyboard reports different keysyms,
  `xbindkeys --key` reveals the right name; one-commit revert restores codes.
- **Guarded autostart (step 03):** an over-strict guard could skip a daemon
  that crashed and needs restart; guards check process name only, and a
  manual launch always works. Revert restores unguarded launches.
- **`.xsessionrc` (step 03):** sourced by X session startup; syntax errors
  could break login env — mitigated by `bash -n` + shellcheck before commit.

Each step is its own commit, so `git revert` or `git bisect` localizes any
regression.
