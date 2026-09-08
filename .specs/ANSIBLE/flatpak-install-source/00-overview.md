# Add flatpak as an install source

| Field | Value |
|---|---|
| Status | In progress |
| Component | ANSIBLE (also touches `.bin/validate-manifest.py`, INSTALLER-adjacent) |
| Created | 2026-09-08 |

## Goal

Make `flatpak` a first-class `source` in `ansible/vars/packages.json` — with
manifest-managed remotes and fail-fast validation, like every other source —
then use it to install `okular` (migrated off apt) and `obsidian` from
Flathub.

## Context & Research

- Multi-source install machinery exists per
  `.specs/INSTALLER/debian-fresh-setup/03-multi-source-install.md`
  (apt/cargo/npm/script/deb/archive/git). Flatpak extends that list.
- `community.general` (already required at >=10.7.0, `ansible/requirements.yml`)
  ships the `flatpak` and `flatpak_remote` modules — no collection bump needed.
- `flatpak` is already an apt entry in `packages.json` (workstation), so the
  CLI exists today; this spec adopts the fnm precedent and makes a gated
  bootstrap task the single source of truth for the flatpak CLI, dropping the
  dedicated apt entry in step 02.
- Remotes follow the `repos.json` pattern: id-keyed definitions referenced by
  entries via a `remote` field; unknown ids fail in the validator, exactly like
  unknown apt `repo` ids. No JSON Schema for the remotes file (same as
  `repos.json` — validator-only, per the manifest-schema-gate spec).
- Privilege rule from the multi-source spec: system-level flatpak remote and
  app installs are the flatpak analogue of apt/deb, so they run with
  `become: true` and `method: system`. No user-level installs in v1.
- Flathub (https://flatpak.org/setup/): remote id `flathub`, remote file
  `https://dl.flathub.org/repo/flathub.flatpakrepo`. App IDs:
  `org.kde.okular` (okular), `md.obsidian.Obsidian` (obsidian).
- `obs-studio` in the manifest is OBS Studio, unrelated to Obsidian — it stays
  an apt entry, untouched.
- The pre-commit hook (`.pre-commit-config.yaml`) only triggers the manifest
  validator for `packages|package-deps|repos` JSON edits; the new remotes file
  must be added to that regex so it is validated too.
- First flatpak install pulls the `org.freedesktop.Platform` runtime
  (~1-2 GB) — slow on first run, fine afterwards. `xdg-desktop-portal-gtk` is
  already in the manifest for portal support under qtile.

## Non-goals

- No user-level (`method: user`) flatpak installs.
- No app version pinning and no `state: latest` auto-upgrades — `state: present`
  only; updates stay manual (`flatpak update`).
- No scheduled flatpak updates (cron/systemd timer).
- No `flatpak-remotes.schema.json` (repos.json precedent: validator-only).
- Not touching `obs-studio`, `xdg-desktop-portal-gtk`, or any other entry.

## Steps

- [x] 01 — `01-flatpak-source.md` — flatpak source plumbing (schema, validator, remotes manifest, bootstrap, tasks)
- [ ] 02 — `02-okular-obsidian-flathub.md` — migrate okular, add obsidian, drop the flatpak apt entry

## Risks & Rollback

- The bootstrap apt install could fail on a stale cache; it runs
  `update_cache: true` so a fresh host converges in one pass.
- `community.general.flatpak`/`flatpak_remote` invoke the flatpak CLI; the
  bootstrap guarantees it exists before those tasks run (toolchain.yml precedes
  packages.yml).
- System-level remote-add/install needs root; failures surface early with
  become errors, not silently.
- First-run runtime download is large but idempotent afterwards.
- Each step is one commit; `git revert` of step 02 restores the apt okular
  entry and step 01 removes the flatpak tasks entirely. User data under
  `~/.var/app/` is never touched by either step.
