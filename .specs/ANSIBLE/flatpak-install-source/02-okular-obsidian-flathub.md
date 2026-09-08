# 02 — Okular and obsidian from flathub

| Field | Value |
|---|---|
| Status | Planning |
| Step | 02 |
| Commit | `ANSIBLE(02): install okular and obsidian from flathub` |

## Files

- `ansible/vars/packages.json` (EDIT — swap okular, add obsidian, drop the
  flatpak apt entry)

## Changes

All edits keep the manifest in lexical key order:

1. **Remove the `flatpak` apt entry.** Step 01's bootstrap is now the single
   source of truth for the flatpak CLI (fnm precedent). With the two new
   flatpak entries below, every workstation run selects at least one
   flatpak-source entry, so the CLI still installs on fresh hosts.
2. **Remove the `okular` apt entry** (`package: okular`) and add a flatpak
   entry under the same key:

   ```json
   "okular": {
     "package": "org.kde.okular",
     "profiles": ["workstation"],
     "remote": "flathub",
     "source": "flatpak"
   }
   ```

3. **Add `obsidian`** (Flathub app ID `md.obsidian.Obsidian`), placed between
   `obs-studio` and `okular` in lexical order:

   ```json
   "obsidian": {
     "package": "md.obsidian.Obsidian",
     "profiles": ["workstation"],
     "remote": "flathub",
     "source": "flatpak"
   }
   ```

`obs-studio` (OBS Studio — a different application) remains an apt entry.

## Acceptance

- [ ] `.bin/validate-manifest.py` and `pre-commit run --all-files` green.
- [ ] `ansible-playbook --check --diff --tags packages` lists: the
      `Install flatpak CLI` bootstrap (skipped — already present), the flathub
      remote task, and both `md.obsidian.Obsidian` and `org.kde.okular` in the
      `Install flatpak applications` loop; `okular` no longer appears in the
      apt transaction.
- [ ] Real run (no `--check`): `flatpak remotes` shows `flathub` (system) and
      `flatpak list` shows `org.kde.okular` and `md.obsidian.Obsidian`.
- [ ] Idempotency: a second `ansible-playbook --tags packages` run reports
      `changed=0` for the flatpak remote and application tasks.
