# 03 — Multi-source install

| Field | Value |
|---|---|
| Status | Planning |
| Step | 03 |
| Commit | `INSTALLER(03): install packages from all manifest sources` |

## Files

- `ansible/playbook.yml` (EDIT — package install tasks; repo tasks from step 02 stay)
- `ansible/vars/packages.json` (EDIT — resolve `TODO` sources, fill `creates`/`build` fields)

## Changes

Install every profile-selected `packages.json` entry according to its `source`,
tagged `packages`. Ordering matters: toolchains first, then everything else.

1. **Selection:** load `packages.json`, keep entries whose `profiles` contains
   the active profile (extra var `dotfiles_profile`, default `workstation` —
   step 04 wires the CLI flag; default here so the playbook runs standalone).
2. **Toolchain bootstrap (auto, gated):**
   - If any selected entry has `source == "cargo"` and `cargo` is missing:
     install `rustup` via its documented script entry pattern and ensure
     `~/.cargo/bin` on PATH for later tasks (no sudo for user-level cargo).
   - If any selected entry has `source == "npm"` and `npm`/`fnm` is missing:
     install `fnm` (script) then the LTS node via `fnm`, exposing node/npm to
     later tasks.
   - If any selected entry has `source == "pipx"` and `pipx` is missing:
     `apt install pipx` then `pipx ensurepath`.
   - Each bootstrap task is skipped when its toolchain already exists
     (`creates`-style guard) and when no selected package needs it.
3. **Per-source install:**
   - `apt`: `ansible.builtin.apt` (`update_cache` with `cache_valid_time`
     first, Debian stable only), `become: true`. Entries with `repo` assume
     step 02 already added it.
   - `cargo`: `community.general.cargo` or `command: cargo install` guarded by
     `creates: ~/.cargo/bin/<bin>`; no `become` (user-level).
   - `npm`: `community.general.npm -g`; needs node on PATH from bootstrap.
   - `pipx`: `community.general.pipx`; no `become`.
   - `script`: `get_url` to temp + execute with `args`, guarded by `creates`.
     `sha256` is accepted by the schema but **not enforced** in v1.
   - `deb`: `get_url` + `apt: deb=<file>` (handles deps), `become: true`.
   - `archive`: `unarchive` (`remote_src: true`, `extra_opts: [--strip-components=N]`
     from `strip`) into `dest` under `~/.local`, guarded by `creates`.
   - `git`: `git` clone (pinned `version` → `ref` when given) + ordered
     `build` commands run in `dest`, guarded by `creates`.
4. **Privilege rule:** `become: true` only for `apt`, key/repo (step 02), and
   `deb` installs. Everything user-level (cargo/npm/pipx/script/archive/git)
   runs without sudo and writes under `$HOME`/`~/.local`, expanding `~`
   against the target user.

## Acceptance

- [ ] `ansible-playbook --tags packages --check --diff` on a fresh Debian
  stable container/VM lists expected installs per profile with no errors.
- [ ] Profile split: `server` run installs dual-tagged entries only (spot-check
  `git curl tmux zsh neovim` present, `rofi dunst picom qtile` absent);
  `workstation` run installs both sets.
- [ ] Idempotency: second full run reports `ok` everywhere (`changed=0`),
  including `script`/`archive`/`git` entries via their `creates` markers.
- [ ] Toolchain gating: a profile selecting zero `cargo` entries skips rustup;
  selecting one bootstraps it exactly once before the crate install.
- [ ] No `become` on user-level tasks: `cargo/npm/pipx` artifacts are owned by
  the user, not root (spot-check `ls -l ~/.cargo/bin`).
