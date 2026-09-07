# Install picom from yshui/picom instead of apt

| Field | Value |
|---|---|
| Status | Planning |
| Component | ANSIBLE |
| Created | 2026-09-07 |

## Goal

Stop installing picom from apt and instead build/install it from the yshui/picom
git repo (pinned to **v12**), replicating how it is already installed on this
machine. Per-user install to `~/.local` so no sudo is needed for the build.

## Context & Research

- Current system: `/usr/local/bin/picom`, built from source
  (`picom --version` → `v12 (yshui/picom revision 69539ed)`), clone at
  `~/.local/src/picom` sitting at `v12-131-g69539edc` (an inter-release dev
  commit — **not** a tag, so exact pinning is impossible).
- Upstream tags: latest release is **v13**; user chose to pin **v12**.
- `git` manifest source already supports `build` steps (string or
  `{cmd, creates}`), executed with a `creates` guard (`playbook.yml:529`).
- Build deps live in a **separate `ansible/vars/package-deps.json`** (user
  decision): keyed by dependent package name → flat list of apt packages,
  installed in one apt task right after the apt-packages task and before any
  per-source install/build task. Deps for key `K` install only when `K` is
  selected for the current profile.
- Build step installs with `-Dprefix="$HOME/.local"` → `~/.local/bin/picom`;
  `~/.local/bin` is prepended to `PATH` in `home/.profile:15`, so it shadows
  the existing `/usr/local/bin/picom`.
- Upstream v12 README lists the Debian build deps; user chose one apt entry
  per package (v13's list is identical plus no new packages).
- `meson setup` refuses an already-configured build dir, so a fresh-machine
  run and a version bump both start from no `build/` dir (bump procedure:
  delete `~/.local/src/picom/build` and `~/.local/bin/picom`, then re-run).

## Non-goals

- Not removing the existing `/usr/local/bin/picom` (it is shadowed; manual
  `sudo rm` if wanted).
- Not building the man pages/docs (`asciidoctor` not installed).
- No auto-tracking of latest upstream.

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

- [ ] 01 — package-deps.json build-dependency manifest (01-build-deps.md)
- [ ] 02 — picom git source entry with build step (02-picom-git-entry.md)

## Risks & Rollback

- A failed build leaves partial artifacts under `~/.local/src/picom/build`;
  deleting that dir re-triggers a clean build. The `creates` guard
  (`~/.local/bin/picom`) keeps re-runs from rebuilding.
- Existing clone is at `v12-131`; the pinned `version: v12` checkout behavior
  with `update: false` leaves an existing tree untouched, so this machine
  keeps building its current dev commit (fresh machines get the v12 tag).
- Each step is its own commit; `git revert` of 02 restores apt picom.
