# Remove wezterm + add packages manifest schema

| Field | Value |
|---|---|
| Status | Done |
| Component | ANSIBLE (step 01 commits as WEZTERM per scope table) |
| Created | 2026-09-06 |

## Goal

Stop installing/linking wezterm (unused terminal) and give `ansible/vars/packages.json`
a JSON Schema so manifest edits get editor autocompletion and fail fast locally.

## Context & Research

- wezterm footprint today is exactly three places (verified `grep -rli wezterm`,
  excluding point-in-time review history under
  `.specs/INSTALLER/debian-fresh-setup/06|07|08-*`, which stays immutable):
  `ansible/vars/packages.json:220-226` (`deb` entry, workstation-only),
  `.config/wezterm/wezterm.lua` (whole dir), `AGENTS.md:39` (WEZTERM scope row).
  Nothing else references it: no qtile keybind, no shell rc, no `.bin/` script,
  no README mention. Alacritty (`alacritty` manifest entry +
  `.config/alacritty/alacritty.toml`) is the terminal in use.
- Prior decision superseded: `08-fix-round.md:88-90` closed the AI-18 wezterm
  half as "won't-fix, entry left as-is". This spec reverses that: entry deleted.
- Schema design constraints (all probed live):
  - In-file `"$schema"` key is honored by `jsonls` (already the configured json
    server in `.config/nvim/lua/langs.lua:56`) with zero editor-config changes.
    But a raw `$schema` key breaks the playbook: `dict2items |
    selectattr('value.profiles', ...)` throws
    `object of type 'str' has no attribute 'profiles'` on it. Fix: strip the
    key in `dotfiles_manifest` via `dict2items | rejectattr('key', 'equalto',
    '$schema') | items2dict` (probe: keys filtered, selection counts correct).
  - `community.general.cargo.features` is `type: list, elements: str`
    (ansible-doc) → schema `array[string]`.
  - Per-arch `url_<arch>` override is implemented **only** by the archive task
    (`playbook.yml:378`); the deb task reads `url` directly (`:344`), so a
    `url_arm64` on a `deb` entry would be silently ignored → schema allows the
    override keys on `archive` only.
  - `git.repo` must stay a plain string: SSH (`git@…`) clone URLs are legal.
    `script`/`deb`/`archive` urls are `^https://` (they are piped to curl).
  - `build` steps are `string | {cmd (required), creates?}` — matches the
    `item.1.cmd if item.1 is mapping` / `default(entry creates)` consumption.
    `build: []` (clone-only) stays valid.
  - `strip` is asserted `number` by the playbook; schema says `integer ≥ 0`
    (a fractional `--strip-components` is never meaningful).
  - `sha256` is spec-documented (script/deb) but playbook-unenforced (v1
    non-goal, follow-up 3): schema accepts it with a 64-hex shape so a malformed
    hash fails in the editor, description notes it is not verified at install.
  - Cross-file rule the schema *cannot* express: apt `repo` must be a key in
    `ansible/vars/repos.json` — stays a playbook assert, noted in the field
    description.
  - Draft-07 (`definitions`, not `$defs`): works with stock `ajv-cli` and every
    editor, no `--spec` flag needed. All keywords used (`oneOf`, `const`,
    `patternProperties`, `additionalProperties`) exist in draft-07.

## Non-goals

- No `repos.json` schema. No schemastore wiring (in-file `$schema` suffices).
- No checksum enforcement. No edits to done-spec history prose (06/07/08 keep
  mentioning wezterm as point-in-time record).
- No behavior change to linking, profiles, or any other manifest entry.

## Steps

Each step maps to exactly one commit. Verify acceptance before committing.

### 01 — Remove wezterm (WEZTERM)

- **Files:** `ansible/vars/packages.json` (EDIT — delete `wezterm` entry),
  `.config/wezterm/` (DELETE — dir), `AGENTS.md` (EDIT — drop WEZTERM row)
- **Changes:** single logical change (remove the terminal everywhere), one
  commit despite spanning scopes. Reverting restores all three together.
- **Acceptance:**
  - [ ] `grep -rli wezterm .config home .bin ansible README.md AGENTS.md`
    prints nothing.
  - [ ] `python3 -m json.tool ansible/vars/packages.json` exits 0.
  - [ ] Selection counts: server 20, workstation 30 (was 31); no `wezterm` key.

### 02 — Manifest JSON schema (ANSIBLE)

- **Files:** `ansible/vars/packages.schema.json` (CREATE, draft-07, prettier-formatted),
  `ansible/vars/packages.json` (EDIT — `"$schema": "./packages.schema.json"`
  as first key), `ansible/playbook.yml` (EDIT — strip `$schema` in
  `dotfiles_manifest`)
- **Changes:** `oneOf` per source (8 branches, `additionalProperties: false`
  each) sharing `$defs` for profiles/urls/paths; top-level allows only
  `$schema` (const) + entry keys (`^[^$].+$`). Mirrors the playbook assert
  block plus the AI-29 type rules.
- **Acceptance:**
  - [ ] `npx --yes ajv-cli validate -s ansible/vars/packages.schema.json -d ansible/vars/packages.json` passes.
  - [ ] Negative fixtures in /tmp each **fail**: bad `source`, empty `profiles`,
    bad profile value, apt without `package`, script with string `args`, archive
    with string `strip`, git with string `build`, cargo with string `features`,
    `deb` with `url_arm64`, typo'd key (`pakcage`), non-https `url`.
  - [ ] `ansible-playbook --syntax-check ansible/playbook.yml` passes;
    `--check --skip-tags packages` stays clean; selection counts unchanged
    (server 20 / workstation 30).

## Risks & Rollback

- **`$schema` key in manifest:** any consumer other than the playbook reading
  `packages.json` raw would see it. Verified sole consumer is
  `ansible/playbook.yml:14` (+ README prose). Rollback: `git revert` the step.
- **Already-provisioned hosts:** the playbook never deletes unmanaged links —
  remove a stale `~/.config/wezterm` symlink manually on this machine; fresh
  hosts are unaffected.
- **Strictness drift:** schema is intentionally stricter than the playbook
  (rejects unknown keys the playbook would ignore). If a future source needs a
  new field, update schema + playbook assert together.
