# Installer hooks

Before/after scripts for package installs. Naming: `<key>.<pre|post>[.root].<sh|py>`.

- `<key>` is a `packages.json` key, or `global` (runs once per play, not per package).
- `.pre` runs before `packages.yml`; `.post` runs after.
- `.root` runs with `become: true`; without it, runs as the invoking user.
- Runner is `ansible.builtin.script` (shebang honored; `.sh` and `.py` both work).
- Env: `DOTFILES_USER` is the invoking user (never assume root or `$USER`).
- Hooks must be idempotent (check state before mutating) and executable (`chmod +x`).
- Non-zero exit fails the play. Hooks never report changes (`changed_when: false`).
