# 02 — Toolchain bootstrap runs unconditionally

## Files

- `ansible/tasks/toolchain.yml` (EDIT)
- `ansible/playbook.yml` (EDIT — comments only)

## Changes

The bootstrap section stops being "auto, gated on selected sources" and
becomes "always installed":

- Remove every source-size gate from the eight tasks:
  - `when: (dotfiles_pkgs_cargo | length) > 0` — "Check for cargo"
    (`:9`), "Install rustup" (`:19`)
  - `when: (dotfiles_pkgs_npm | length) > 0` — "Check for fnm" (`:28`),
    "Check PATH for fnm" (`:40`), "Install fnm" (`:52`),
    "Install Node LTS via fnm" (`:67`)
  - `when: (dotfiles_pkgs_flatpak | length) > 0` — "Check for flatpak"
    (`:77`), "Install flatpak CLI" (`:94`)
- Keep every idempotency guard exactly as is:
  - rc probes (`dotfiles_cargo_check`, `dotfiles_fnm_path_check`,
    `dotfiles_flatpak_check` with `!= 0` conditions)
  - stat check (`dotfiles_fnm_check`)
  - `creates:` markers (rustup, fnm, Node LTS `aliases/default`)
- Update the section header comment in `toolchain.yml` and the playbook
  import comment (`playbook.yml:66-67`): "auto, gated on selected sources"
  → "always installed". Task names and `tags: [packages]` unchanged.

Note: fnm is still installed via the curl script at this point — the
method switch is step 03. This step only changes *when* the tasks run,
keeping each commit independently green and revertible.

## Acceptance

- [x] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
- [x] `ansible-playbook --check --tags packages ansible/playbook.yml`:
  toolchain tasks are evaluated (not skipped for empty source sets); on
  this host each skips via its existing-install guard — cargo rc 0, fnm on
  PATH, `~/.local/share/fnm/aliases/default` exists, flatpak installed.
