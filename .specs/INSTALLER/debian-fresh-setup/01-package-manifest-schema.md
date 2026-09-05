# 01 — Package manifest schema

| Field | Value |
|---|---|
| Status | Done |
| Step | 01 |
| Commit | `INSTALLER(01): add packages.json manifest schema` |

## Files

- `ansible/vars/packages.json` (CREATE)

## Changes

Single JSON manifest. Logical name as key; value is always an object with at
least `source` and `profiles`. No bare-string entries.

```json
{
  "git": {
    "source": "apt",
    "package": "git",
    "profiles": ["workstation", "server"]
  },
  "rofi": {
    "source": "apt",
    "package": "rofi",
    "profiles": ["workstation"]
  },
  "docker-ce": {
    "source": "apt",
    "package": "docker-ce",
    "repo": "docker",
    "profiles": ["workstation", "server"]
  },
  "starship": {
    "source": "cargo",
    "crate": "starship",
    "profiles": ["workstation", "server"]
  }
}
```

Field rules:

- `source`: one of `apt | cargo | npm | pipx | script | deb | archive | git`.
- `profiles`: subset of `["workstation", "server"]`. Entry is installed when
  the selected `--profile` is in its list. Tools needed everywhere (git, curl,
  tmux, zsh, neovim) carry **both** tags; GUI-only tools (qtile, rofi, dunst,
  picom, alacritty, flameshot) carry `workstation` only.
- Per-source fields:
  - `apt`: `package` (Debian package name), optional `repo` (id in
    `repos.json`, step 02).
  - `cargo`: `crate`, optional `version`, optional `features`.
  - `npm`: `package`, optional `version`.
  - `pipx`: `package`, optional `version`.
  - `script`: `url`, optional `args` (must be a list when present), required
    `creates` (path whose existence means "already installed", used for
    idempotency), optional `sha256` (documented, **not enforced** in v1 — see
    follow-up 3).
  - `deb`: `url`, optional `sha256` (documented, not enforced in v1).
  - `archive`: `url`, optional per-arch override `url_<deb arch>` (e.g.
    `url_arm64`; falls back to `url`), `dest` (under `~/.local`, e.g.
    `~/.local/opt/<name>`), optional `strip` (strip-components, must be a
    number when present), required `creates`.
  - `git`: `repo` (clone URL), optional `dest`, optional `version` (pinned
    tag/branch/commit; default is the remote default branch without tracking
    updates on re-runs), required `build` (must be a list; each step is
    a string, or a `{cmd, creates}` mapping when only that step needs its own
    guard), required `creates` (default guard for build steps without one;
    the clone itself is skipped when this marker already exists).
- `profiles` must be non-empty (an empty list selects into no profile and is
  rejected by validation).
- Kernel-to-Debian arch map: `x86_64→amd64`, `aarch64→arm64`, `armv7l→armhf`,
  `i386/i686→i386`; any other arch fails validation instead of writing a
  broken `arch=` repo line.
- `creates`/`dest` paths may use `~` as a leading home shorthand; the
  playbook expands only that prefix against the target user's home, not
  root's (beware `become`).
- Seed content: start from the old `vars/main.yml` list (common: `curl git tmux
  zsh`; Debian extras: `alacritty dunst flameshot neovim picom rofi xbindkeys
  xscreensaver`) as plain `apt` entries with correct `profiles` tags, plus
  entries for every other tool the configs imply (qtile, wezterm, starship,
  fnm/node, fzf, bat). Anything whose source is unclear gets `apt` with a
  `TODO` comment-adjacent marker resolved in step 03.

## Acceptance

- [ ] `python3 -m json.tool ansible/vars/packages.json` exits 0 (valid JSON).
- [ ] A small filter check (python one-liner or `ansible localhost -m debug`)
  proves: profile `server` selects all dual-tagged entries and zero
  `workstation`-only entries; profile `workstation` selects dual-tagged plus
  workstation-only entries.
- [ ] Every immediate-child tool directory under `.config/` (qtile, wezterm,
  nvim, tmux, rofi, dunst, alacritty, flameshot) has at least one manifest
  entry covering it, or a recorded reason it needs none.
- [ ] No YAML package lists are created; `vars/main.yml` from the old
  implementation is not revived.
