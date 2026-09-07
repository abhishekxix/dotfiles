# 09 — Fix round for PR #4 biased-review findings (third round)

| Field | Value |
|---|---|
| Status | Done (verified 2026-09-07; deviation + follow-up decisions recorded below) |
| Component | INSTALLER |
| Created | 2026-09-07 |
| PR | #4 `installer/debian-fresh-setup` → `main` |
| Fixes | 28 inline review comments on PR #4 (biased review, sections 3–5 only) |

## Goal

Fix every safe, locally verifiable finding from the 28 inline review comments on
PR #4, and record a verdict + follow-up for every remaining item (spec-conflict
policy calls, checksum enforcement, untestable-without-fresh-host claims).

## Context & Research

- Review source: 28 `pulls/4/comments` (all by `abhishekxix`, biased review).
  Full bodies saved during triage; each item below cites its file:line.
- Prior rounds: `06-review-attestation.md` (first adversarial round),
  `07-review-attestation.md` (second), `08-fix-round.md` (AI-21…AI-32 fixes).
- Live probes run 2026-09-07 on this host (Debian trixie, ansible-core 2.19.4,
  `community.general` 13.3.0):
  - `apt-cache policy`: trixie ships `ansible 12.0.0` (core 2.19.4),
    `neovim 0.10.4-8`, `pipx 1.7.1-1`. The "bookworm-era ansible-core"
    worry (`install:144`) is stale for trixie; `community.general 10.7.0`
    declares `requires_ansible: '>=2.15.0'` (upstream `runtime.yml`), so the
    floor resolves on trixie. Verdict: keep the floor, add preflight asserts.
  - `ansible-galaxy collection list --format json` works and returns
    `{path: {collection: {version}}}` (probed live); missing collection
    returns `{}` rc=0. Wrapper switches to it (no more `awk` on human output).
  - `lookup('community.general.collection_version', 'community.general')`
    returns `13.3.0` live; `is version('10.7.0', '>=')` works on core 2.19.
    In-playbook preflight assert is therefore viable.
  - `ansible_playbook_pid` is MISSING (no such magic var); `ansible_user_id`
    is `abhi` under a play (undefined for ad-hoc `ansible -m debug`).
    Backup-dir uniqueness uses `ansible_date_time.iso8601_basic_micro` (microsecond
    resolution, e.g. `20260907T112850205990`) instead of a pid.
  - Starship prebuilt musl tarballs for **both** arches return HTTP 200 and
    the x86_64 binary was downloaded, extracted (`tar -tzf` shows a single
    top-level `starship` file, no strip needed), and runs (`starship 1.22.1`).
    `starship_*_amd64.deb` does **not** exist (HTTP 404) — archive, not deb.
  - `sort -V -c` proves floor comparison in isolation (ordered input rc=0,
    `9.4.0`-below-floor rc=1).
- Conflict with standing spec: `04-installer-ux.md:18-19` mandates always
  prompting for the become password, and `06/AR-02` explicitly rejected
  conditional-become as a defect. Item `install:177` (conditional become)
  therefore needs a maintainer spec decision first — deferred, not fixed here.
- Standing deferrals reused: checksum enforcement is follow-up 3 in
  `00-overview.md:41` (covers `sha256`-wiring and key-fingerprint items);
  VG-01/VG-02 (fresh-host proof) stay open.

## Non-goals

- No conditional `--ask-become-pass` (spec 04 + AR-02 conflict; maintainer call).
- No checksum/`sha256` enforcement (follow-up 3); no `deb`-path removal or
  new deb fixture (no suitable fixture; path stays dormant but intact).
- No backport/appimage resourcing for stable-lagging GUI packages (maintainer
  packaging call); neovim expectation pinned in docs only.
- No fresh-host VM run (VG-01/VG-02 stay open).
- One commit per step per repo convention; no history rewrite.

## Triage verdicts (all 28)

| # | Item | Verdict |
|---|---|---|
| 1 | `install:165` fragile galaxy `awk` check + floor only in wrapper | FIX (wrapper → `--format json`; playbook preflight assert) |
| 2 | `install:168` version-compare one-liner | FIX (`sort -V -c`, same edit as 1) |
| 3 | `install:177` always `--ask-become-pass` | DEFER (conflicts spec 04 + AR-02; maintainer decision) |
| 4 | `install:144` old ansible-core vs CG floor | FIX as preflight asserts (core `>=2.15`, CG `>=10.7.0`); trixie probe shows no real conflict |
| 5 | `install:90` `-e @file.yml` / false-positive sniffing | FIX as documented limitation (wrapper usage text); later `-e` wins on the CLI so no silent corruption |
| 6 | `playbook.yml:7` no in-playbook profile validation | FIX (preflight assert) |
| 7 | `playbook.yml:242` `pipx ensurepath` before pipx installed (Blocker) | FIX (move after apt installs) |
| 8 | `playbook.yml:282` hardcoded cargo `executable:` | FIX (drop it; cargo resolves via PATH with `~/.cargo/bin` prepended, covers apt + rustup) |
| 9 | `playbook.yml:299` hardcoded fnm paths vs PATH probe | FIX (invoke `fnm` via PATH incl. `~/.cargo/bin`; alias/npm data dir `~/.local/share/fnm` is stable regardless of binary origin — observed live) |
| 10 | `packages.json:141` fnm twice (script entry + bootstrap) | FIX (drop manifest entry; bootstrap is the single source) |
| 11 | `playbook.yml:114` `creates:` blocks key rotation | DEFER (needs checksum/fingerprint = follow-up 3; removing `creates` would rearmor every run) |
| 12 | `playbook.yml:146` `replace('{{ ansible_architecture }}')` templating | FIX (`@ARCH@`/`@RELEASE@` placeholders in `repos.json`) |
| 13 | `playbook.yml:380` per-arch fallback fetches wrong binary | FIX (fail fast when arch ≠ amd64 and `url_<arch>` missing) |
| 14 | `playbook.yml:386` zip guard tests base URL | FIX (test the resolved per-arch URL) |
| 15 | `playbook.yml:412` git `update:` polarity backwards | FIX (`update: version is not defined`) |
| 16 | `packages.json:153` `build: []` required by schema | FIX (`build` optional in schema; drop empty arrays) |
| 17 | `playbook.yml:344` `deb` source is dead code | DEFER (no fixture available; dropping the path removes future coverage — revisit when first deb entry lands) |
| 18 | `packages.schema.json:45` `sha256` never wired | DEFER (follow-up 3; schema already marks it NOT enforced) |
| 19 | `link.yml:62` copy-pasted `when` + synthetic check predictions | FIX as no-behavior refactor (single `dotfiles_link_conflict` fact; predictions kept — AI-09 behavior unchanged) |
| 20 | `playbook.yml:13` 1-second backup-root collisions, no retention doc | FIX (microsecond `iso8601_basic_micro` root + README retention note; initially shipped `iso8601_basic` by mistake — corrected in e4e18e1) |
| 21 | `playbook.yml:12` no root guard | FIX (fail fast when `ansible_user_id == 'root'`) |
| 22 | `playbook.yml:288` stale `ansible_facts.env.PATH` stitching | FIX (prepend `~/.cargo/bin` on fnm/npm tasks so cargo-installed fnm is found post-bootstrap) |
| 23 | `playbook.yml:257` triple `apt-get update` | REJECT with evidence (all three carry `cache_valid_time: 3600`; at most one real update per run — same as AR-11) |
| 24 | `playbook.yml:142` repos never purged on profile switch | FIX as docs (README manual-cleanup note; auto-purge could delete user-added repos) |
| 25 | `packages.json:23` stable neovim/qtile staleness | DEFER packaging call (trixie has neovim 0.10.4, not 0.7; resourcing backports needs maintainer decision — tracked as follow-up) |
| 26 | `packages.json:103` docker usable only after group+relogin | FIX (playbook adds invoking user to `docker` group + README relogin note; daemon enablement stays out per v1 scope) |
| 27 | `packages.json:115` starship via cargo = 5-min compile, pins rot | FIX (starship → `archive` with x86_64+aarch64 musl URLs, both HTTP 200 + binary verified; cargo path kept in code for future crates) |
| 28 | `README.md:36` no in-playbook collection-floor enforcement | FIX (preflight assert via `collection_version` lookup) |

## Steps

Each step maps to exactly one commit, named `INSTALLER(<NN>): <summary>`.

### 15 — Wrapper galaxy check via `--format json` + `-e` limitation docs

- **Files:** `install` (EDIT)
- **Changes:** replace `awk`-on-human-output with
  `ansible-galaxy collection list community.general --format json` parsed for
  all installed versions (max wins; empty → install). Compare floor with
  `sort -V -c` (`floor,have` ordered ⇒ at/above floor ⇒ skip; disorder ⇒
  `--upgrade`). Document in usage text that `-e @file.yml` indirection is not
  detected and that an undetected explicit `-e` still wins (later `-e` wins on
  the ansible CLI, after the injected default).
- **Acceptance:**
  - [x] `shellcheck install` clean; `bash -n install` passes.
  - [x] Floor logic probe: have `13.3.0` ⇒ skip; have `9.4.0` ⇒ upgrade;
    missing ⇒ fresh install.

### 16 — Playbook preflights: profile, root, collection + core floors

- **Files:** `ansible/playbook.yml` (EDIT)
- **Changes:** first tasks in the play (tags `packages,dotfiles` except the
  collection check which is `packages`-only): assert
  `dotfiles_profile in ['workstation','server']`; assert
  `ansible_user_id != 'root'`; assert
  `lookup('community.general.collection_version', 'community.general') is
  version('10.7.0', '>=')`; assert `ansible_version.full is version('2.15',
  '>=')` (CG 10.7 needs `>=2.15.0` per upstream `runtime.yml`).
- **Acceptance:**
  - [x] `ansible-playbook --syntax-check ansible/playbook.yml` passes.
  - [x] `-e dotfiles_profile=bogus --check` fails with the profile message.

### 17 — `pipx ensurepath` after apt installs (Blocker)

- **Files:** `ansible/playbook.yml` (EDIT — move task, no logic change)
- **Changes:** move `Ensure pipx path is configured` to immediately after
  `Install apt packages`, so the `pipx` binary (manifest apt entry or
  bootstrap task) exists before `ensurepath` runs with `failed_when: rc != 0`.
- **Acceptance:**
  - [x] `--syntax-check` passes; task order in file is apt-installs →
    ensurepath → pipx-installs.

### 18 — Dynamic cargo/fnm resolution

- **Files:** `ansible/playbook.yml` (EDIT)
- **Changes:** drop hardcoded `executable: ~/.cargo/bin/cargo` (module
  resolves `cargo` via PATH; task PATH already prepends `~/.cargo/bin`, which
  covers rustup installs while apt `/usr/bin/cargo` stays on inherited PATH).
  `Install Node LTS` invokes `fnm` via PATH (PATH gains `~/.cargo/bin` so a
  cargo-installed fnm is found); npm task PATH also gains `~/.cargo/bin`.
  Keep the fnm *data* path (`~/.local/share/fnm/aliases/default`) — it is
  stable regardless of binary origin.
- **Acceptance:**
  - [x] `--syntax-check` passes; no `~/.cargo/bin/cargo` or
    `~/.local/share/fnm/fnm` *binary* references remain in install commands.

### 19 — Single-source fnm (drop manifest script entry)

- **Files:** `ansible/vars/packages.json` (EDIT — delete `fnm` entry),
  `.specs/.../03-multi-source-install.md` (EDIT — bootstrap is the source)
- **Changes:** remove the `fnm` `script` entry (URL/flags/`creates` drift
  source). Bootstrap installs fnm whenever an npm package is selected
  (`prettier` is selected on both profiles, so coverage is unchanged).
- **Acceptance:**
  - [x] `python3 -m json.tool` passes; profile filter still selects `prettier`.

### 20 — `@ARCH@`/`@RELEASE@` repo placeholders

- **Files:** `ansible/vars/repos.json` (EDIT), `ansible/playbook.yml` (EDIT —
  replace targets), `.specs/.../02-apt-repos.md` (EDIT — placeholder docs)
- **Changes:** repo lines use `@ARCH@`/`@RELEASE@`; the playbook replaces
  those literals with `dotfiles_deb_arch` / `distribution_release` (no more
  string-replacing Jinja delimiters; whitespace variants impossible).
- **Acceptance:**
  - [x] `json.tool` passes; `--syntax-check` passes; rendered line still
    contains `arch=amd64` on this host (debug probe).

### 21 — Archive arch fail-fast + resolved-URL zip guard

- **Files:** `ansible/playbook.yml` (EDIT),
  `.specs/.../01-package-manifest-schema.md` (EDIT — base `url` is the amd64
  default; non-amd64 hosts require `url_<arch>`)
- **Changes:** new assert before extraction: when `dotfiles_deb_arch !=
  'amd64'`, every selected archive entry must define `url_<arch>` (no silent
  x86_64 fallback on armhf/i386). `extra_opts` zip test inspects the same
  resolved `url_<arch>|default(url)` expression as `src:`.
- **Acceptance:**
  - [x] `--syntax-check` passes; synthetic armhf selection without
    `url_armhf` fails with the message.

### 22 — Git `update:` polarity + optional `build`

- **Files:** `ansible/playbook.yml` (EDIT — `update: version is not
  defined`; drop build-required assert line, keep type check),
  `ansible/vars/packages.json` (EDIT — drop three `"build": []`),
  `ansible/vars/packages.schema.json` (EDIT — `build` optional for `git`),
  `.specs/.../01-package-manifest-schema.md` (EDIT — `build` optional wording)
- **Changes:** pinned clones set `update: false` (no per-run fetch);
  floating clones update. Schema no longer forces `build`; clone-only repos
  are legitimate and `subelements(..., skip_missing=True)` already handles
  the missing key.
- **Acceptance:**
  - [x] `json.tool` on both JSON files; `--syntax-check` passes.

### 23 — Starship via prebuilt archive

- **Files:** `ansible/vars/packages.json` (EDIT — starship entry)
- **Changes:** `starship 1.22.1` becomes `archive` with x86_64 + arm64 musl
  tarball URLs (both HTTP 200; x86_64 binary executed live), `dest:
  ~/.local/bin`, `creates: ~/.local/bin/starship` (single-file tarball, no
  `strip`). Cargo toolchain tasks stay for future crates.
- **Acceptance:**
  - [x] `json.tool` passes; resolved URL downloads + extracts to a working
    `starship` (probed live for x86_64).

### 24 — Docker group + link fact + backup uniqueness + README notes

- **Files:** `ansible/playbook.yml` (EDIT — docker-group task after apt
  installs; `iso8601_basic` backup root), `ansible/tasks/link.yml` (EDIT —
  `dotfiles_link_conflict` fact replacing the 6× repeated `when`),
  `README.md` (EDIT — docker relogin post-step, repo manual-cleanup,
  backup-retention note), `.specs/.../05-dotfile-linking.md` (EDIT —
  microsecond root + fact wording)
- **Changes:** `user: name={{ ansible_user_id }} groups=[docker] append=true`
  (become, gated on docker-ce selected). Backup root gains microsecond
  resolution (no same-second `mv` collisions; retention stays manual —
  documented). Link logic byte-identical, deduplicated; check-mode predicts
  unchanged (AI-09 behavior kept).
- **Acceptance:**
  - [x] `--syntax-check` passes; dotfiles `--check` on the linked host stays
    `changed=0`; synthetic-conflict `--check` still predicts backup + link.

## Risks & Rollback

- Per-step commits keep `git revert`/`git bisect` effective; verify each
  step's acceptance before committing.
- Deferred items (3, 11, 17, 18, 25) each name their follow-up: 3 needs a
  spec-04 amendment decision; 11/18 need follow-up 3 (checksum enforcement);
  17 needs the first real deb entry; 25 needs a packaging decision.
- VG-01/VG-02 still require a fresh Debian host and stay open.

## Deviations

- **Commit granularity:** steps 16–24 landed condensed into commits
  `9767b86 INSTALLER(16)`, `d267463 INSTALLER(17)`, `a8cdfce INSTALLER(18)`
  (bundling several steps each) instead of one commit per step as planned.
  History was left untouched (no rewrite); the per-step mapping above still
  documents which commit carries which step.
- **Verification (2026-09-07, this host):** `--syntax-check` clean, all three
  JSON files valid, `shellcheck install` + `bash -n install` clean; bogus
  profile `--check` fails with the profile message; `sort -V -c` floor probes
  (13.3.0 skip / 9.4.0 upgrade) pass; synthetic `dotfiles_deb_arch=armhf`
  fails fast on `url_armhf`; `--tags dotfiles --check` on the linked host is
  `changed=0`; synthetic `~/.gitconfig` conflict predicts the microsecond
  backup root + backup + link (symlink restored afterwards); preflight
  floor asserts pass live; rendered docker repo line contains `arch=amd64`.

## Follow-up decisions (2026-09-07, maintainer)

4. **Conditional become prompt:** **keep always-ask** — spec 04 and AR-02
   stand; `install:177` item closed without change.
5. **Stable-lagging GUI/editor packages:** switch stale stable packages to
   upstream **archive/appimage** sources in `packages.json` (not backports).
   Requires a new spec before implementing (multi-file manifest + playbook
   surface).
