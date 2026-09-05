# 06 — Adversarial review attestation (PR #4)

| Field | Value |
|---|---|
| Status | Done (all accepted items fixed; see follow-ups below) |
| Step | 06 (review-only, no code change) |
| PR | #4 `installer/debian-fresh-setup` → `main` |
| Reviewed commits | `d8a65e0`, `fda9a72`, `272b3e9`, `6a2469c`, `361987c`, `3ef5e56`, `e2bc686`, `5c0aa7a` |
| Method | Biased adversarial finder subagent (fresh context, instructed to assume broken) → impartial refuter subagent (fresh context, ACCEPT/REJECT/PARTIAL per claim with file:line proof). Live checks were read-only: `syntax-check`, `--check --tags dotfiles`, `setup`, `dpkg`, `locale`, `shellcheck`. No sudo/apt writes. |
| Maintainer approvals recorded | `community.general` use approved; OS-level locale (`en_US.UTF-8`) approved; `5c0aa7a LXSESSION` cursor change intentional. |

## Accepted findings (fix-worthy)

### AI-01 — Wrong Debian arch in apt repo lines (Blocker)
- Verdict: ACCEPT. `ansible/playbook.yml:72` expands `{{ ansible_architecture }}` with `ansible_facts.architecture` (`x86_64`), but apt needs `amd64` (`aarch64` → `arm64`). Breaks Docker/VSCode `apt update`. Spec `02-apt-repos.md:40-41` itself mandates `ansible_architecture` — spec bug too.
- Action: map arch (`x86_64→amd64`, `aarch64→arm64`, fallback `dpkg --print-architecture`) and fix the spec mandate.

### AI-02 — No `community.general` dependency declaration (Blocker)
- Verdict: ACCEPT. Used at `ansible/playbook.yml:169,184,198`; no `requirements.yml`, no galaxy install in `install`, no README note. Fresh host fails module resolution.
- Action: add `ansible/requirements.yml` (`community.general>=10.7.0`, see AI-16), install it from `install`, document in README.

### AI-03 — Unconditional apt update after repos (Major)
- Verdict: ACCEPT. `ansible/playbook.yml:79-85` has no `cache_valid_time` and is ungated on key/repo `changed`; always reports `changed`, violating step 02's second-run acceptance. Contrast `:149-155` which has `cache_valid_time: 3600`.
- Action: add `cache_valid_time` and/or register key/repo results and gate the update on change.

### AI-04 — `pipx ensurepath` masks failures (Major)
- Verdict: ACCEPT. `ansible/playbook.yml:138-146` combines `failed_when: false` with a stdout string-match `changed_when`; `rc=127`/empty stdout reports `changed` and hides the error.
- Action: remove `failed_when: false`; assert `rc==0` or check `pipx` presence first.

### AI-05 — `git` `creates` never honored / unpinned HEAD (Major)
- Verdict: PARTIAL (reproducibility kernel accepted; "breaks changed=0" overstated — git+update usually reports ok unless upstream moved). Clone (`ansible/playbook.yml:263-273`) has no `creates`, defaults `version: HEAD`, `update: true`; `build: []` yields 0 loop items so per-entry `creates` is never checked.
- Action: pin git versions or use `update: false`, honor `creates` on clone, decide per-step `creates` semantics for builds.

### AI-06 — `command: '{{ build_step }}'` cannot run shell builds (Major, latent)
- Verdict: ACCEPT. `ansible/playbook.yml:276` uses `command` (no `&&`/`|`/`$VAR`); shared `item.0.value.creates` across the `subelements` loop skips later steps once the marker exists.
- Action: switch builds to `shell` (or `argv`), define per-step `creates` semantics for multi-step builds.

### AI-07 — Naive `~` expansion, no schema validation, silent drops (Major)
- Verdict: ACCEPT. `replace('~', home)` replaces all occurrences; unknown `source` matches no selector and is silently skipped; bad `repo` id raises KeyError.
- Action: use `regex_replace('^~', …)`; add a fail-fast validation task (allowed sources/profiles, required per-source fields, repo-id check).

### AI-08 — Zero `npm`/`pipx`/`archive` manifest entries (Major, coverage)
- Verdict: ACCEPT. Counts verified (`apt:22, git:3, cargo:1, script:1, deb:1`; `npm/pipx/archive: 0`). 3/8 sources never execute; gating untestable as shipped.
- Action: add fixture entries or record an explicit deferral waiver for the three untested sources.

### AI-09 — `--check` conflict preview fails (Major)
- Verdict: ACCEPT (proven). Conflict case: `mv` skipped in check mode, then `Link ... force: false` fails instead of predicting. Violates step 05 preview acceptance.
- Action: add `check_mode` handling to `ansible/tasks/link.yml` (predict mv/link) and re-verify `--check --diff`.

### AI-10 — npm bootstrap dead code + wrong PATH + fnm `creates` mismatch (Major, latent)
- Verdict: ACCEPT (B2+B3 downgraded to Major, latent — 0 npm entries so never executes); PARTIAL on B4 (mismatch real: `packages.json:184` `creates=~/.cargo/bin/fnm` vs `playbook.yml:111` stat `~/.local/share/fnm/fnm`; "re-runs every time" unproven — existing `~/.cargo/bin/fnm` makes the script task skip). `playbook.yml:109-125` registers checks no task consumes; `:193` PATH points at the fnm binary dir, not node shims.
- Action: implement fnm + LTS node bootstrap per spec 03 (or waive npm explicitly), correct PATH via `fnm env`, unify `creates`/stat paths.

### AI-11 — `gpg` needed before `gnupg` installed (Major, conditional)
- Verdict: PARTIAL. Dearmor (`ansible/playbook.yml:40-56`) precedes the `gnupg` apt install; breaks minimal images lacking `gpg` (host has `gnupg 2.4.7`).
- Action: pre-install `gnupg`/`ca-certificates` before dearmor or assert presence.

### AI-12 — Predictable `/tmp` `.deb` path (Minor/hardening)
- Verdict: PARTIAL (downgraded; sha256 portion rejected — checksums explicitly deferred in `00-overview.md:41`/follow-up 3). `get_url` as user → `apt deb=` as root on a predictable `/tmp` path is a real symlink-race shape; single-user exploitability low.
- Action: use a root-owned temp/cache dir or registered tempfile; prune stale `.asc` (leftover `.asc` + `creates: keyring` also blocks key rotation — accepted nit).

### AI-13 — Duplicate `INSTALLER(03)` commits (Minor, process)
- Verdict: ACCEPT. `272b3e9` + `3ef5e56` share the step number; order `01,02,03a,04,05,03b` violates one-commit-per-step/ordering.
- Action: process-only; squash/rename convention for any follow-up touching step 03 scope.

### AI-14 — SPECS commit skew: overview Done vs steps Planning (Minor, docs)
- Verdict: ACCEPT. `e2bc686` adds all 6 spec files at once; `00-overview.md:5` Done + all `[x]` vs `01–05` still `Status: Planning`.
- Action: reconcile step-file statuses (or record that only the overview tracks closure).

### AI-15 — `install` accepts Ubuntu via `ID_LIKE` (Minor)
- Verdict: ACCEPT. `install:55-58` passes Ubuntu; contradicts Debian-only. Spec internally contradicts itself (`04-installer-ux.md:28-30` says accept `ID_LIKE debian`).
- Action: narrow to `ID=debian` strict check and fix the spec contradiction.

### AI-16 — `pipx: name: pkg==ver` needs collection floor (Minor)
- Verdict: ACCEPT. `ansible/playbook.yml:199` `name: pkg==ver` requires `community.general>=10.7.0`; no floor pinned; zero test entries.
- Action: pin the floor in `requirements.yml` (with AI-02); add a pipx fixture or waiver (with AI-08).

### AI-17 — Per-package apt loop instead of single transaction (Minor, perf)
- Verdict: ACCEPT. `ansible/playbook.yml:157-166` runs ~22 transactions; correct but slow, non-atomic, noisy.
- Action: single task with a package-name list.

### AI-18 — Stale `wezterm` Debian12 pin + unpinned `starship` (Minor/Major)
- Verdict: PARTIAL. `wezterm-20240203 ... Debian12.deb` (2024) on a trixie host + unpinned cargo `starship` (slow compile, non-reproducible) are real; docker-deps and neovim/qtile-age claims rejected (deps auto-install; no evidence).
- Action: refresh the wezterm pin per Debian release; pin `starship` version or switch source.

### AI-19 — `rustup`/`ensurepath` edits vs managed symlinks (Major, latent)
- Verdict: PARTIAL. Ordering real (bootstrap precedes linking, so shell-file edits can be lost); "no cargo PATH" overstated — `home/.profile:18` sources `.cargo/env`. Latent today (no pipx-source entries, cargo present).
- Action: order bootstrap vs linking deliberately; ensure PATH lines live in repo dotfiles, not side-effect edits.

### AI-20 — Accepted nit batch
- Verdict: ACCEPT (real nits). Double apt update; archive `--strip-components` tar-only (breaks zip); archive-parent task ignores `creates`; deb re-download after `/tmp` clear; backup timestamp-parent perms (leaf `0700`, parent umask); `--profile=` undocumented; `-h/--help` to stderr (`install:8`); symlink-invoked `repo_root` (`BASH_SOURCE` unresolved); double `sudo` prompts; duplicate `-e` passthrough collision; `ansible.cfg` relative inventory fragile outside wrapper; README mode `755→644` churn bundled silently.
- Action: one cleanup pass per item; keep each fix scoped and verifiable.

## Rejected findings (false alarms — no action)

### AR-01 — LXSESSION commit as scope violation
- Verdict: REJECT. `5c0aa7a` is maintainer-intentional. No action.

### AR-02 — Always `--ask-become-pass` as defect
- Verdict: REJECT. Spec-mandated UX (`04-installer-ux.md:18-19`). CI inconvenience is an enhancement request, not a bug. No action.

### AR-03 — Missing locale handling
- Verdict: REJECT. Fixed OS-wide (`en_US.UTF-8` verified in `/etc/default/locale` and env). No failure evidence. No action.

### AR-04 — pipx `| list` correctness
- Verdict: REJECT as defect (style-only). Generator probe shows `in` works without `| list`. No action.

### AR-05 — Missing checksums on script/deb
- Verdict: REJECT. Explicitly deferred (`00-overview.md:41`, follow-up 3). Tracked there, not here. No action.

### AR-06 — docker-ce deps / neovim-qtile age speculation
- Verdict: REJECT. `-cli`/`containerd` are `Depends` (auto-installed); version-age claims had no evidence. No action.

### AR-07 — Nit false alarms
- Verdict: REJECT. `link.yml` `bool`-filter precedence is correct (`|` binds tighter than `not`); bogus `-e` profile still linking is by design (step 05: no profile gating); `source /etc/os-release` is a standard trusted idiom; `.bin/` untouched is an explicit non-goal (`00-overview.md:25,39`). No action.

## New issues from the refuter (missed by the finder)

### AN-01 — Unguarded nvm source in `home/.bashrc:10`
- `source /usr/share/nvm/init-nvm.sh` with no existence guard; file absent → every interactive bash errors.
- Action: guard with `[ -f … ]` or migrate to fnm (`.zshrc` already uses `fnm env`).

### AN-02 — Quoted `features:` stringifies a list
- `ansible/playbook.yml:172` `features: '{{ … }}'`; module expects a list.
- Action: drop the quotes.

### AN-03 — Mode churn (`install` 775, README 755→644)
- Verdict: factually observed. Normalize modes (`install 755`, README 644) and avoid silent mode changes in future commits.
- Action: normalize in a cleanup commit.

## Verification gaps (unproven PR claims — accept, need live proof)

### VG-01 — Full idempotency / profile split / repo / conflict / opt-out / preview
- Only dotfiles `--check` on an already-linked host (`ok=64 changed=0`) was proven. Still unproven on a fresh Debian stable host/VM: full second-run `changed=0`, server-vs-workstation split, `apt-cache policy` for third-party packages, key+repo second-run `ok`, conflict backup placement, `-e dotfiles_backup_conflicts=false` failure message, `--check` accuracy for packages (AI-09 disproves it for conflicts).
- Action: run the spec acceptance suites (steps 02/03/05) against a fresh Debian stable container/VM with sudo and record evidence.

## Handoff note for the next chat

Suggested work order (risk/effort): AI-02 + AI-16 (requirements floor) → AI-01 (arch map) → AI-03 + AI-09 (update gating, check-mode) → AI-04 + AI-07 (ensurepath, validation) → AI-10 + AI-08 (npm bootstrap decision, fixtures/waivers) → AI-05 + AI-06 (git pinning, shell builds) → AI-11 + AI-12 + AI-20 (gnupg order, temp files, nit cleanup) → AI-13/AI-14/AI-15/AI-17/AI-18/AI-19 + AN-01/AN-02/AN-03 (process/docs/pins/modes) → VG-01 (live fresh-host proof). Each fix should cite its AI-/AN-/VG- id in the commit message.

## Resolution (2026-09-05 — all accepted items addressed, uncommitted)

Playbook (`ansible/playbook.yml`): AI-01 (`dotfiles_deb_arch` map, templated
into repo lines); AI-03 (repo-triggered update registered + gated,
`cache_valid_time: 3600`); AI-04 (`failed_when: rc != 0`, changed on missing
`already`); AI-05 (pinned git `version`s, `update` only when pinned, clone
honors entry `creates`); AI-06 (`shell` builds, per-step `{cmd, creates}`
override); AI-07 (fail-fast assert block for source/profiles/required fields +
repo-id check, `regex_replace('^~', …)` everywhere); AI-11 (`gnupg` +
`ca-certificates` pre-install with `cache_valid_time` before dearmor);
AI-12 (per-user `~/.cache/dotfiles-debs/`, stale `.asc` pruned after dearmor);
AI-17 (single `apt: name=<list>` transaction); AN-02 (unquoted `features`).
New behavior: fnm install + `fnm install --lts` bootstrap (AI-10), npm via the
fnm default-alias npm with node on PATH, manifest fixtures `prettier` (npm),
`ruff==0.8.4` (pipx), `lazygit` (archive) (AI-08/AI-16), pinned
`starship 1.22.1` and zsh-plugin tags (AI-18/AI-05), `PIPX_BIN_DIR`-safe pipx
PATH (AI-19), tar-only `--strip-components` + `creates != dest` guard on
archive parents (AI-20).

Linking (`ansible/tasks/link.yml`): AI-09 (`mkdir`/`mv`/real link skipped
in check mode, paired `debug` predict-tasks report `changed`). Verified with
a synthetic conflict dir: first `--check` failed on the real link
(`force: false` refusing file→symlink conversion even in check mode), so the
link task itself is now check-mode-gated too; re-ran clean
(`ok=66 changed=23 failed=0`) with `Would link … (after backing up conflict)`
predictions, and the already-linked host stays `changed=0`.

Installer (`install`): AI-02 (galaxy install from `requirements.yml` when
`community.general` is missing); AI-15 (strict `ID=debian`, root without sudo);
AI-20 (`BASH_SOURCE` fallback, no duplicated `--ask-become-pass`/`-e`, help to
stdout, `ansible.cfg` untouched — relative inventory is correct since the
wrapper `cd`s to the repo root). New `ansible/requirements.yml`
(`community.general>=10.7.0`, AI-16) + README galaxy note (AI-02).

Dotfiles: AN-01 (guarded nvm source in `home/.bashrc`); AN-03 + AI-20
(normalized `install 0755`, tracked text files `0644`).

Specs: 02 (`dotfiles_deb_arch` mandate fix, gated-update acceptance), 01 (git
`version`/`{cmd, creates}` rules, leading-`~` rule), 03 (fnm+LTS bootstrap,
requirements floor, per-user deb cache, tar-only strip, shell builds,
fail-fast validation), 04 (strict Debian check, galaxy bootstrap, no duplicate
passthrough, help to stdout), 05 (check-mode prediction), 01–05 `Planning` →
`Done` (AI-14; only the overview tracked closure before).

Deliberately not done: AI-13 (history rewrite out of scope — convention
applies to follow-ups); VG-01 (needs a fresh Debian VM/container with sudo —
record as follow-up); live `apt-cache policy` / second-run `changed=0` proof
on a fresh host (same reason).

## VG-01 reasoning log (2026-09-05 — argued from code, no fresh host)

Walked each VG-01 claim against the fixed tree instead of a fresh VM. Method:
read the task, state the steady-state post-run-1 condition, then evaluate what
run 2 (and `--check`) must report. Pre-existing local evidence where noted;
everything else is deduction, marked as such.

Setup facts used throughout: server selects 20 entries, workstation 31
(counted from `packages.json`); both profiles share all dual-tagged entries;
no GUI-only entry leaks into server (checked by script). The local host has
`~/.zshrc`/`~/.zshenv` already symlinked into the repo, which is why the
no-conflict `--check` reports `changed=0`.

1. **Full second-run `changed=0` (packages).** DEDUCED per task, not proven:
   - Validation `assert`: `changed=0` always (no state).
   - `gnupg`/`ca-certificates` apt: `state: present` → ok when installed.
   - `get_url` key `.asc`: re-downloads only if remote checksum differs; then
     the new `file: state=absent` prune task reports `changed` on run 1 (it
     deletes the just-downloaded `.asc`) and `ok` on run 2 (nothing there).
     Either way run 2 settles to ok. Residual risk: none for idempotency,
     one wasted download per run by design.
   - Dearmor `command` with `creates: <keyring>`: skipped once the keyring
     exists. Residual risk (accepted at review): `creates` also blocks key
     *rotation* — a changed upstream key never re-dearmors until the keyring
     is manually removed. Same shape as every other `creates` guard below.
   - `apt_repository`: `state: present` with identical line → ok.
   - Gated repo update (`when: … is changed`, `cache_valid_time: 3600`):
     all three registers unchanging → skipped on run 2. First-run edge:
     `get_url` may report ok while dearmor reports changed (or vice versa);
     the `or` covers every combination. Check-mode caveat: registers from
     skipped/untaken branches evaluate via `is changed` → false, so `--check`
     predicts no update — accurate only if run 1 actually converges, which is
     the standard Ansible check-mode limitation, not a playbook bug.
   - rustup/fnm/LTS scripts: `creates` markers
     (`~/.cargo/bin/cargo`, `~/.local/share/fnm/fnm`, `…/aliases/default`)
     exist after run 1 → skipped. fnm edge: if the user already has fnm but
     no `aliases/default`, the LTS task still runs — intended (it converges
     toward the state npm tasks assume).
   - `pipx ensurepath`: `failed_when: rc != 0`; `changed_when` = stdout lacks
     `already in PATH` (case-insensitive). Run 2 with PATH settled → prints
     `… is already in PATH.` → ok. Residual risk, minor: if a future pipx
     rewords that message, every run reports changed (cosmetic, still
     converges — no failure masked since rc is checked separately).
   - Plain `apt update_cache` (`cache_valid_time: 3600`) + single-transaction
     `apt: name=<22-item list>, state: present`: ok when installed and cache
     fresh. KNOWN WEAKNESS, reasoned not tested: `cache_valid_time` only
     suppresses the *update*; the install task itself always contacts the
     cache metadata, and any genuinely upgraded upstream package re-reports
     changed — that is correct behavior (system drifted), not non-idempotency.
   - `cargo` (`community.general`, `state: present`, pinned `1.22.1`):
     module queries installed version → ok when satisfied. Unpinned crates
     would still report ok (present = any version) — pinning was for
     reproducibility (AI-18), not idempotency.
   - `npm` (`state: present`, pinned `3.4.2`, `executable:` = fnm default
     alias npm): same present-check → ok on run 2. Depends on the LTS task
     having created `aliases/default` — ordering guaranteed (bootstrap tasks
     precede installs). Fresh-host residual: if `fnm install --lts` fails
     (no network), npm fails with a clear missing-executable error rather
     than silently using system npm — fail-loud is intended.
   - `pipx install ruff==0.8.4`, `unarchive lazygit` (`creates`), `shell`
     fnm script (`creates`), `get_url` wezterm `.deb` + `apt: deb=`:
     all guarded or content-addressed. `get_url` re-downloads only on
     checksum change; `apt: deb=` with the same version installed → ok.
     The old `/tmp` predictable-path race is gone (per-user
     `~/.cache/dotfiles-debs/`), though a concurrent same-user run could
     still race the download — negligible, noted.
   - `git` clones pinned (`0.8.0`, `v0.7.1`, `0.35.0`) with
     `update: "{{ version is defined }}"` → `update: true` but already at the
     pinned ref → ok. Build steps: `build: []` + `skip_missing=True` yields
     zero loop items → no task, no changed. Per-step `{cmd, creates}` override
     exists for future non-empty builds; untested with a real build (no
     fixture has build steps — accepted gap, same class as AI-08's original
     complaint, now narrowed to git-builds only).
   - Archive parents (`file: state=directory`, skipped when
     `creates == dest`): `0755` already correct → ok. `unarchive`
     `creates=<binary>`: skipped. Tar-only `--strip-components` guard means a
     future `.zip` + `strip` entry extracts without stripping — deterministic,
     documented in spec 03.
   - NET CONCLUSION: run 2 `changed=0` follows from per-task guards **iff**
     run 1 converges (network OK, no upstream version yank mid-run). The
     one structural rotation-blindness (`creates` on dearmor/scripts) is
     accepted trade-off, consistent with step 03's `creates`-marker design.

2. **Server-vs-workstation split.** PROVEN by manifest computation (script
   output, no host needed): server = 20 entries, workstation = 31, every
   workstation-only entry is GUI-scoped (`alacritty dunst flameshot picom
   rofi xbindkeys xscreensaver qtile lxsession vscode wezterm`), zero leak
   into server. DEDUCED consequence: server run never references the `vscode`
   repo, so `dotfiles_repos_selected == ['docker']` and the vscode key/repo
   tasks skip via `loop: '{{ dotfiles_repos_selected }}'` — the step-02
   acceptance ("server must not add workstation-only repos") holds by
   construction of the loop variable, not by `when` clauses that could rot.
   Unproven on live apt: that `docker-ce` actually installs from the new repo
   (`apt-cache policy` showing the docker source) — requires root + network
   on Debian, cannot be reasoned away.

3. **Key + repo second-run `ok`.** DEDUCED from (1): `get_url` stable,
   dearmor `creates`-skipped, `apt_repository` present → all ok, gated update
   skipped. No live `apt-cache policy` evidence — same gap as (2).

4. **Conflict backup placement.** PARTIALLY PROVEN locally: real linking tasks
   were exercised with `--check` against a synthetic conflict dir overriding
   `dotfiles_home` (safe: no `$HOME` writes). Conflict case now predicts
   (`Would create backup directory …`, `Would move …`, `Would link …`) with
   `failed=0`; no-conflict `--check` on the already-linked host gives
   `ok=64 changed=0`. DEDUCED but unproven: the *real* (non-check) `mv`
   places the file under `<backup_root>/home/` and the symlink follows —
   the task sequence is `stat → mkdir → mv → link` with identical `when`
   guards, and `mv -- <dst> <dir>/` semantics put the basename inside the
   group dir; failure atomicity argued: if `mv` fails mid-run the link task
   still executes and `force: false` refuses, leaving the original in place
   (no data loss path — `mv` within one filesystem is a rename). Live `ls`
   of a backup dir after a real conflict run is the missing evidence.

5. **`dotfiles_backup_conflicts=false` failure message.** PROVEN locally:
   `--check` with a synthetic conflict + `false` fails with `… already
   exists and is not the managed symlink. Move it manually …` (`failed=1`).
   Ordering argument: the `fail` task precedes `mkdir`/`mv`/link with the
   same stat condition plus `not backup | bool`, so no backup dir or move can
   precede the failure. DEDUCED: identical in live mode (the `fail` task has
   no check-mode guard, so check/live behave the same here).

6. **`--check` accuracy for packages.** REASONED LIMITATION, not a defect to
   fix here: check mode can only report what modules predict. `apt`
   (`update_cache`, installs), `get_url`, `git`, `unarchive`,
   `community.general.*` all support check mode and report would-change
   correctly against current state; `command`/`shell` bootstrap tasks with
   `creates` correctly skip when markers exist but report `changed` (would
   run) when absent — accurate as predictions. The known blind spot is
   cascading state: e.g. check mode cannot know that run 1's repo-add changes
   what run 1's later `apt install docker-ce` would resolve. That is inherent
   to `--check`, and the spec-05 acceptance that mentions preview accuracy is
   scoped to *linking* (`--skip-tags packages`), which (4) covers.

RESIDUAL RISK REGISTER (things reasoning cannot close — next fresh-host run
should check these first): (a) `fnm install --lts` + `default` alias flow on
a bare host (only the alias-symlink layout was verified against a sandbox
`FNM_DIR`); (b) `community.general.npm` `executable=` pointing at the alias
path before any shell ever ran `fnm env`; (c) `pipx ensurepath` stdout wording
on Debian's packaged pipx version; (d) wezterm `.deb` still installing on
trixie (2024 Debian12 pin) vs needing a release bump; (e) `starship 1.22.1`
crate still compiling against current stable rustc.
