# Declare qtile's tray client libraries as deps; drop standalone indicator host

| Field | Value |
|---|---|
| Status | Done |
| Component | ANSIBLE |
| Created | 2026-09-09 |

## Goal

Remove the redundant standalone `ayatana-indicator-application` host service
and declare the tray client libraries (`libayatana-appindicator3-1`,
`gir1.2-ayatanaappindicator3-0.1`) as `qtile` deps, so the qtile tray keeps
working while `packages.json` only lists tools the user chose.

## Context & Research

- `.config/qtile/config_parts/screens.py:91-92` hosts both
  `widget.StatusNotifier` and `widget.Systray`, so qtile already renders tray
  icons; `ayatana-indicator-application` is a duplicate SNI host for DEs that
  lack one.
- `apt-cache rdepends` (checked 2026-09-09): `pasystray` and
  `network-manager-applet` (both kept by the user) reverse-depend on
  `libayatana-appindicator3-1` — it's the client-side lib that lets tray apps
  *publish* icons. `gir1.2-ayatanaappindicator3-0.1` serves the same role for
  Python/GObject indicator clients.
- `ansible/vars/package-deps.json` is keyed by dependent package name; deps
  for key `K` install only when `K` is selected for the profile
  (`playbook.yml:22`). The lib/gir exist to serve the qtile tray, so `qtile`
  is the right key.
- Both vars files keep lexical order for top-level keys and fields within
  entries (`AGENTS.md`, "Working with the installer"). Within `qtile`'s dep
  list, existing entries are alphabetical; the new entries sort before
  `lm-sensors`.
- Manual pre-change test: stop the indicator service
  (`systemctl --user stop ayatana-indicator-application.service` or
  `pkill ayatana-indicator`), restart qtile, confirm `pasystray` /
  `nm-applet` icons still render.

## Non-goals

- No changes to `.config/qtile/` widget configuration.
- No removal of `pasystray` or `network-manager-applet` (both kept).
- No changes to the `picom` dep list or any other `package-deps.json` key.

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

- [x] 01 — drop indicator host, move client libs to qtile deps (01-tray-deps.md)

## Risks & Rollback

- If an app fails to publish its tray icon after the change, the cause is a
  missing client lib — re-adding a `packages.json` entry or a dep restores it.
  Each step is its own commit, so `git revert` localizes any regression.
