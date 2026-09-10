# Fix qtile startup + hotplug flicker

| Field | Value |
|---|---|
| Status | Approved |
| Component | QTILE |

> Supersedes nothing; hardens `qtile-dynamic-monitors` (Done). Its spec
> accepted "reload_config rebuilds all bars (~1s visible flicker)" as a cost —
> this spec attacks the flicker around that mechanism per user decisions
> (2026-09-10): apply layout at config load, keep reload_config but fire it at
> most once per transition, debounce the screen_change hook 200ms.

## Goal

Kill the 2-3s flicker at qtile startup and the multi-flash on display
hotplug (1↔2), without changing the monitor policy (max rate, bottom-align,
group placement) or the bar/group UX.

## Context & Research

Findings (measured on this host, 2026-09-10):

1. **Startup flash is a post-paint rate bump.** X's preferred mode for
   HDMI-0 is 59.95 (the `+` marker) while the layout helper enforces max
   rate 74.96. `configure_monitors()` runs from `autostart.sh`, which
   `startup_once` spawns *after* qtile has painted — so every login shows
   one visible mode-change blank plus a RandR event storm. Applying the
   same command during config load (before first paint) does the mode
   change while the screen is still black.
2. **Hotplug 1↔2 fires `qtile.reload_config()`** (`hooks.py`), rebuilding
   every widget on both bars and re-registering the systray — the ~1s
   flicker. The reload exists only because `build_screens()` builds 1
   Screen (solo) or 2 (dual); qtile's own RandR path (`_process_screens`)
   reuses existing bars and cannot mint a second configured Screen from a
   solo config. User chose to keep the reload (conservative), guarded so it
   can fire at most once per transition.
3. **A plug is a storm of RandR events** (driver connect events + our own
   apply's follow-ups). Each event currently runs the hook synchronously:
   one `xrandr --query` ≈ 100ms, `--verbose` ≈ 106ms (stale-fb path),
   `--listmonitors` ≈ 146ms — serialized in qtile's event loop. Hook
   subscribers run in subscription order: the user hook (subscribed during
   config import) runs *before* qtile's internal screen rebuilder on the
   same event, so `len(qtile.screens)` read inside the hook is always the
   pre-rebuild count — the existing early-return dance exists to wait for
   the next event. Debouncing coalesces the burst and keeps that dance
   only where it is still needed (right after our own apply).
4. **Reload guard.** The correct "at most once" test compares the *loaded
   config's* Screen count with what the hardware now implies
   (`len(qtile.config.screens) != want`), not qtile's live screen list:
   after a reload the config matches, so later events in the same burst
   cannot re-fire it; a config built solo converges to dual exactly once.

## Non-goals

- No change to monitor policy: modes, rates, positions, stale-fb handling
  (`monitors.py` plan logic untouched).
- No always-2-Screens or runtime `visible_groups` swapping (rejected
  option — reload stays).
- No autostart/picom/xwallpaper ordering changes; `autostart.sh` keeps its
  foreground `monitors.py` call (wallpaper ordering; becomes a no-op).
- No widget or bar content changes.
- No debouncing of qtile's internal `reconfigure_screens` subscriber.

## Steps

Each step maps to exactly one commit, named `QTILE(<NN>): <summary>`.

**Process per step (mandatory):**

1. **New chat.** Start each step's implementation in a fresh chat/session —
   the executing session reads this spec (and its own brainstorm) from
   scratch, so no context carries over between slices.
2. **Brainstorm first.** Before writing any code, re-run brainstorming for
   that step: re-verify the step's assumptions against the live system
   (e.g. re-time xrandr, re-read the touched files — they may have moved on
   since this spec), surface options, and confirm the approach with the
   user. Only then implement, one commit, and tick the acceptance boxes as
   they pass.

### 01 — Apply monitor layout at config load (pre-paint)

> Run in a **new chat**; brainstorm (re-verify assumptions live, confirm
> approach with user) before implementing.

- **Files:** `.config/qtile/config.py` (EDIT)
- **Changes:** before `build_screens()`, call
  `config_parts.monitors.configure_monitors()` guarded by try/except
  (fail open: qtile must still start). Idempotent — no-op when state
  matches (the stable case, incl. every `reload_config`); at fresh login it
  bumps HDMI 59.95→74.96 while the screen is still black. `build_screens()`
  then queries post-apply state, so the solo/dual decision is made on the
  settled layout. `autostart.sh` unchanged.
- **Test:** `python3 -m py_compile .config/qtile/config.py`;
  `python3 .config/qtile/config_parts/monitors.py --selfcheck`
- **Acceptance:**
  - [ ] fresh login: desktop's first visible frame is already at the final
        layout/rates — no post-paint mode-change blank on either output
  - [ ] mod+ctrl+r reload still works (config-load xrandr is a ~100ms no-op)

### 02 — Debounce screen_change + at-most-once reload

> Run in a **new chat**; brainstorm (re-verify assumptions live, confirm
> approach with user) before implementing.

- **Files:** `.config/qtile/config_parts/hooks.py` (EDIT)
- **Changes:** replace the `_HOTPLUG_BUSY` re-entry lock with a 200ms
  debounce: each `screen_change` event cancels the pending timer and
  re-schedules the body via `qtile.call_later`, so a plug storm coalesces
  into one run after 200ms of quiet (our own apply's follow-up events
  re-arm the timer, giving a second settled pass). Body = current inner
  logic with two changes: the reload condition becomes
  `len(qtile.config.screens) != want_screens` (want = 2 when an external is
  connected, else 1) replacing the `((after == 2) != dual or before !=
  after)` heuristic; the early-return-while-counts-differ wait stays (it is
  what bridges the gap until qtile's own screen rebuild lands on a
  follow-up event). The `screens_reconfigured`/cooldown behavior is
  unchanged otherwise; group placement stays geometry-based.
- **Test:** `python3 -m py_compile .config/qtile/config_parts/hooks.py`
- **Acceptance:**
  - [ ] unplug → one reload total, solo bar converges (all 10 groups);
        replug → one reload total, two bars 5+5; no reload loop
  - [ ] mid-storm: only one reload fires per 1↔2 transition even when the
        driver emits several RandR events
  - [ ] a replug within 200ms of an unplug does not drop the second
        transition (timer re-schedules, does not cancel pending work)

## Risks & Rollback

- **Startup latency:** config load gains ~100ms (no-op query) up to
  ~300-500ms (an apply) before first paint — spent while the screen is
  black; buys a flicker-free first frame.
- **Debounce blind spot:** if the last RandR event arrives >200ms after the
  previous one, two debounced runs happen — both idempotent/cheap (one
  no-op query each), no reload (guard compares config state, not events).
- **Pending timer vs reload:** `reload_config()` clears hook subscriptions;
  a timer that fires right after a reload re-runs an idempotent body
  against the fresh config — safe by construction.
- **xrandr unavailable mid-boot:** step 01's try/except fails open; qtile
  starts with whatever X initialized and the hook converges later.
- Each step is its own commit: `git revert` localizes a regression; step 01
  and step 02 are independently revertable.