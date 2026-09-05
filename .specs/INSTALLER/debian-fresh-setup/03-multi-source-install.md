# 03 — Multi-source install

| Field | Value |
|---|---|
| Status | Done |
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
   - If any selected entry has `source == "npm"` and node is missing:
     install `fnm` (probed via the stock path *and* `command -v fnm`, so a
     cargo-installed fnm is not reinstalled) then the LTS node via
     `fnm install --lts`, exposing node/npm from the fnm default alias to
     later tasks. The LTS alias is a converge-once marker: an existing
     `aliases/default` is never auto-upgraded to a newer LTS.
   - If any selected entry has `source == "pipx"` and `pipx` is missing:
     `apt install pipx` then `pipx ensurepath` (fail on non-zero rc; changed
     when stdout+stderr lack "already in PATH").
   - The playbook needs the `community.general` collection (cargo/npm/pipx
     modules, minimum version 10.7.0 for `pipx: name: pkg==ver`); it is
     declared in `ansible/requirements.yml` and installed by `install`.
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
   - `script`: pipe `curl` into `bash` with `args`, guarded by `creates`.
     `sha256` is accepted by the schema but **not enforced** in v1.
   - `deb`: download to a per-user cache dir (`~/.cache/dotfiles-debs/`,
     created by a `file: state=directory` task first) +
     `apt: deb=<file>` (handles deps), `become: true` for the install only.
   - `archive`: `unarchive` (`remote_src: true`, `extra_opts: [--strip-components=N]`
     from numeric `strip`, tar-only — never passed for `.zip` URLs,
     case-insensitive and query-string tolerant) into `dest` under
     `~/.local`, guarded by `creates`. `url_<deb arch>` (e.g. `url_arm64`)
     overrides `url` on non-amd64 hosts.
   - `git`: `git` clone (pinned `version` when given — Ansible coerces the
     templated `update` flag to bool, so unpinned entries do not track on
     re-runs; skipped entirely when the entry `creates` marker already exists
     — `ansible.builtin.git` takes no `creates` param, hence the stat guard) +
     ordered `build` commands run via `shell` in `dest`, guarded by
     `creates` (per-step `{cmd, creates}` overrides the entry default).
   - The playbook validates the manifest first: unknown `source`, bad
     `profile`, empty `profiles`, missing per-source fields, bad `args`/`build`
     (`sequence`) / `strip` (`number`) types, unknown `repo` ids, and unknown
     host arches fail fast instead of silently skipping. (`version`/`features`
     stay quoted `default(omit, true)` — a bare `{{ }}` mapping value is a YAML
     parse error, so unquoting is not an option.)
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
