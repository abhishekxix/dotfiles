# 08 — Fix round for 07-review-attestation findings (PR #4)

| Field | Value |
|---|---|
| Status | Done (steps 08–14 implemented + verified; VG-01/VG-02 still open — need a fresh host) |
| Component | INSTALLER |
| Created | 2026-09-05 |
| PR | #4 `installer/debian-fresh-setup` → `main` |
| Fixes | AI-21…AI-32 from `.specs/INSTALLER/debian-fresh-setup/07-review-attestation.md` |

## Goal

Fix every accepted finding from the 07 adversarial review (AI-21…AI-32) on branch
`installer/debian-fresh-setup`, one commit per step, verified before committing.

## Context & Research

- 07 round (finder F-01…F-41 → refuter → owner probes): ACCEPT AI-21 (Blocker,
  deb cache dir never created — live `get_url` "Destination … does not exist"
  reproduction), AI-22 (galaxy floor never enforced), AI-23 (lazygit x86_64-only
  URL + stale wezterm 2024 pin), AI-24 (`-e*` over-match, `-K` miss), AI-25
  (clone ignores `creates`), AI-28 (six `home/` files `0755`); PARTIAL AI-26
  (still-quoted `omit`), AI-27 (arch fallback), AI-29 (assert types), AI-30
  (fnm refresh/probe), AI-31 (ensurepath/script nits), AI-32 (docs drift);
  17 finder claims rejected with live proof (AR-08…AR-24).
- Live facts established during review: `default` rescues dict-miss (F-01);
  loop-register `is changed` aggregates correctly (F-08/09); `"False"` string
  coerces to bool False (F-12); quoted `omit` works but must stay quoted — YAML
  forbids a bare `{{ }}` mapping value (probe: "missing quotes around a template
  block"), so AI-26's fix is `default(omit, true)` + `^~/` tightening, NOT
  unquoting; `get_url` default `force:` is content-compare (no re-download
  churn); host fnm lives at `/home/abhi/.cargo/bin/fnm` while the playbook
  stats `~/.local/share/fnm/fnm` (probe gap for AI-30).
- Upstream versions verified 2026-09-05: latest wezterm release is still tag
  `20240203-110809-5046fc22` (Debian12 `.deb` + `.Debian12.arm64.deb` both HTTP
  200); `lazygit v0.55.1` ships both `Linux_x86_64` and `Linux_arm64` tarballs
  (HTTP 200); `starship 1.22.1` / `prettier 3.4.2` / `ruff 0.8.4` all real.
- `ansible-doc community.general.pipx`: `name` specifiers (`tox<4.0.0`) need
  collection ≥10.7.0 (`source:` is for URLs/dirs only). Installed collection
  here is 13.3.0 (`sort -V` floor checks work for AI-22).

## Non-goals

- No fresh-host VM run (VG-01/VG-02 stay open; needs sudo/network Debian host).
- No checksum enforcement (follow-up 3), no history rewrite (AI-13 waived),
  no Ubuntu support (strict `ID=debian` stays).
- No behavior change to linking semantics, profile split, or repo lines beyond
  what AI-21…AI-32 require.

## Steps

Each step maps to exactly one commit, named `INSTALLER(<NN>): <summary>`.
Verify each step's acceptance before committing. Do NOT mix steps in one commit.

### 08 — Create deb cache dir (AI-21, Blocker)

- **Files:** `ansible/playbook.yml` (EDIT — new task before `Download deb packages`)
- **Changes:** add `file: path="{{ dotfiles_home }}/.cache/dotfiles-debs"
  state=directory mode=0755` task (no `become`, tagged `packages`). Keep the
  per-user cache design (AI-12); just create it.
- **Acceptance:**
  - [ ] `ansible-playbook --syntax-check ansible/playbook.yml` passes.
  - [ ] `get_url` to a missing subdir still fails, but the new task creates the
    cache dir first: prove with `-e dotfiles_home=/tmp/opencode/…` override that
    the cache dir task reports `changed` then the download proceeds.

### 09 — Enforce galaxy floor (AI-22, Major)

- **Files:** `install` (EDIT — version-aware collection check)
- **Changes:** replace the presence-only grep with: query installed version
  (`ansible-galaxy collection list | awk '$1=="community.general"{print $2}'`),
  compare against floor `10.7.0` via `sort -V`, run
  `ansible-galaxy collection install -r …` fresh when missing and `--upgrade`
  when below floor. Keep `set -Eeuo pipefail`, shellcheck-clean.
- **Acceptance:**
  - [ ] `shellcheck install` clean; `bash -n install` passes.
  - [ ] Logic probe: floor > installed → upgrade path taken; floor ≤ installed →
    skipped (stub `ansible-galaxy` or unit-test the comparison in isolation).

### 10 — Arch-aware fixture URL (AI-23, lazygit only)

- **Files:** `ansible/vars/packages.json` (EDIT — `lazygit` `url_arm64`),
  `ansible/playbook.yml` (EDIT — resolve
  `item.value['url_' + dotfiles_deb_arch] | default(item.value.url, true)` in
  the `archive` extract task), `.specs/.../03-*` (EDIT — document per-arch URL
  override)
- **Changes:** keep `url` as the amd64 default; add `url_arm64` for lazygit
  (`…_Linux_arm64.tar.gz`, verified 200). `wezterm` is INTENTIONALLY untouched
  (maintainer decision 2026-09-05: no longer uses wezterm — entry left as-is,
  AI-18 wezterm half closed as won't-fix).
  Probe pattern `item.value['url_' + dotfiles_deb_arch] | default(item.value.url, true)`
  already validated live (lazygit→arm64 URL, default→amd64 URL). No assert change
  needed (extra keys already allowed).
- **Acceptance:**
  - [ ] `python3 -m json.tool` on both manifests passes.
  - [ ] Debug probe: `dotfiles_deb_arch=arm64` resolves lazygit to the arm64
    URL; `amd64` keeps the current URL.

### 11 — Precise `-e`/`-K` passthrough (AI-24)

- **Files:** `install` (EDIT), `.specs/.../04-installer-ux.md` (EDIT if wording drifts)
- **Changes:** only set `saw_profile_e` when the `-e`/`--extra-vars` *value*
  mentions `dotfiles_profile` (handle `-e VALUE`, `--extra-vars VALUE`,
  `-eVALUE`, `--extra-vars=VALUE` split/joined forms; bare dangling `-e` passes
  through to ansible-playbook's own error). Detect `-K`/`--ask-become-pass`/
  `--become-password-file` for `saw_become_pass` per spec 04:37. Keep error-path
  usage on stderr (AI-32: `usage >&2` for error call sites, stdout for `-h/--help`).
- **Acceptance:**
  - [ ] `shellcheck install` clean; `bash -n install` passes.
  - [ ] `./install --help` → stdout, exit 0; `./install --profile bogus` →
    non-zero with usage on stderr; `-e foo=1` no longer suppresses the default
    profile injection (verify via `--dry-run`-style arg echo or trace).

### 12 — Git `creates` decision + `omit` hardening (AI-25, AI-26)

> Probe result (must be designed around): `args: creates:` is **NOT supported**
> by `ansible.builtin.git` — live probe fails with "Unsupported parameters …
> module: creates". So the fix is a `stat`-guarded clone, not `args.creates`.

- **Files:** `ansible/playbook.yml` (EDIT — `stat` each git dest + `when: not exists`
  on `Clone git sources`; switch build-step guard default to
  `item.1.creates | default(item.0.value.creates, true)`; `default(omit, true)` +
  `^~/` tightening, quotes KEPT),
  `.specs/.../01-package-manifest-schema.md` (EDIT — document clone-`creates`
  semantics for `build: []`), `.specs/.../06-review-attestation.md` Resolution
  section (EDIT — correct "clone honors entry `creates`" / "unquoted `features`")
- **Changes:** decision: clone honors entry `creates` via a preceding `stat`
  (dest + marker) and `when: not exists` on the clone task — consistent with the
  schema "required `creates`" without touching `args` (unsupported by the module).
  `build: []` entries therefore skip both clone (when marker present) and builds
  (zero-iteration) deterministically. For AI-26:
  do NOT unquote (`{{ }}` bare value is a YAML parse error — proven); instead use
  `default(omit, true)` (rescues empty-string/falsy LHS too) and tighten `^~` →
  `^~/` where the intent is a home prefix (keeps behavior, kills the
  `~otheruser` shape). Add `creates`-absent-in-clone regression to the step's
  acceptance.
- **Acceptance:**
  - [ ] `ansible-playbook --syntax-check ansible/playbook.yml` passes.
  - [ ] `--check --skip-tags packages` still `ok` clean on linked host; quoted
    `default(omit, true)` probe renders omit correctly.

### 13 — Arch map, assert types, fnm probe (AI-27, AI-29, AI-30)

- **Files:** `ansible/playbook.yml` (EDIT — extended `dotfiles_deb_arch` map +
  unknown-arch fail-fast; assert additions for empty `profiles: []` and
  `script.args`/`git.build` list types + `archive.strip` int type),
  `.specs/.../01-*` + `03-*` (EDIT — document map + type rules)
- **Changes:** map `armv7l→armhf`, `i386/i686→i386` (keep `x86_64→amd64`,
  `aarch64→arm64`); unknown arch → explicit `assert` failure instead of a raw
  kernel name in `arch=`. Assert: reject `profiles: []`, non-list `args`/`build`,
  non-int `strip`. AI-30: probe `command -v fnm` (like the cargo check) in
  addition to the `~/.local/share/fnm/fnm` stat, so cargo-installed fnm
  (`/home/abhi/.cargo/bin/fnm` observed) skips redundant reinstall; document
  the aliases/default no-refresh trade-off in spec 03 (no auto-upgrade of LTS).
- **Acceptance:**
  - [ ] `ansible-playbook --syntax-check ansible/playbook.yml` passes.
  - [ ] Manifest validation rejects a synthetic bad entry (empty profiles /
    string `args`) with the fail-fast message.

### 14 — Modes, PATH/pipe nits, docs drift (AI-28, AI-31, AI-32)

- **Files:** mode bits via `git update-index --chmod=-x` (six `home/` text files);
  `ansible/playbook.yml` (EDIT — case-insensitive zip guard
  `is not search('(?i)\\.zip($|\\?)')` (probe-verified: `.ZIP`/query forms
  excluded, `.tar.gz` still stripped), `bash` consistently in script pipe or
  justified `sh`); `install` (EDIT — error-path `usage >&2`); specs 01/03
  (EDIT — script `curl|sh` wording, cargo `creates` scope, git `update`
  coercion note)
- **Changes:** keep behavior; docs must describe code as-shipped. `ensurepath`
  wording match: extend to `stdout+stderr` if cheap without restructuring,
  else record the cosmetic-only limitation in spec 03.
- **Acceptance:**
  - [ ] `git ls-files -s home/` shows `100644` for the six text files (scripts,
    images, `.gitignore`, `install` stay `100755`).
  - [ ] `shellcheck`/`bash -n`/`syntax-check`/`json.tool` all pass; final
    `--check --skip-tags packages` clean.

## Risks & Rollback

- Per-step commits (`INSTALLER(08)`…`INSTALLER(14)`) keep `git revert`/`git bisect`
  effective. Each step verifies before committing; VG-01 fresh-host proof stays a
  follow-up (no VM in this round).
