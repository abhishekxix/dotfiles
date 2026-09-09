# Installer hooks

Before/after scripts for package installs. Naming: `<key>.<pre|post>[.root].<sh|py>`.

- `<key>` is a `packages.json` key, or `global` (runs once per play: `global.pre` before everything, `global.post` after everything).
- `.pre` runs immediately before that package installs; `.post` immediately after. Ordering per package: pre-hook → install → post-hook.
- Looping sources (cargo, npm, script, deb, archive, git, flatpak) get true per-package hooks. Apt installs in one transaction, so all selected apt pre-hooks run before it and all apt post-hooks after it.
- `.root` runs with `become: true`; without it, runs as the invoking user. Global hooks cannot use `.root` (they run unprivileged).
- For apt packages the hook key must equal the entry's `package` field.
- Runner is `ansible.builtin.script` (shebang honored; `.sh` and `.py` both work).
- Env: `DOTFILES_USER` is the invoking user (never assume root or `$USER`).
- Hooks must be idempotent (check state before mutating) and executable (`chmod +x`).
- Non-zero exit fails the play. Hooks never report changes (`changed_when: false`).
