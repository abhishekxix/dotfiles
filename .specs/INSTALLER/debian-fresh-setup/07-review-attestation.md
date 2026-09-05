# 07 — Adversarial review attestation (PR #4, second round)

| Field | Value |
|---|---|
| Status | Review only — DO NOT merge the "all fixed" claim as-is (1 Blocker + 1 Major outstanding; see AI-21, AI-22) |
| Step | 07 (review-only, no code change, no commit) |
| PR | #4 `installer/debian-fresh-setup` → `main` |
| Reviewed commits | Full diff `main..installer/debian-fresh-setup`; heaviest scrutiny on `244acfc INSTALLER(06): address adversarial review findings` |
| Prior round | `.specs/INSTALLER/debian-fresh-setup/06-review-attestation.md` — treated as **untrusted input**, every verdict re-verified from code |
| Method | Biased adversarial finder subagent (fresh context, assume-broken, claim-volume rewarded, refutation forbidden → 41 claims F-01…F-41) → impartial refuter/verifier subagent (fresh context, ACCEPT/REJECT/PARTIAL per claim with file:line proof + live Jinja/Ansible probes) → owner spot-verification of every load-bearing verdict below. Live checks read-only: `syntax-check`, `--check --skip-tags packages`, `shellcheck`, `bash -n`, `json.tool`, `ansible-doc`, ad-hoc `ansible`/`ansible-playbook` probes in `/tmp/opencode`, `curl -sIL` for fixture URLs, `apt-cache policy`. No sudo/apt writes, no `$HOME` mutation. `--tags packages --check` deliberately NOT run (needs root/network). |
| Maintainer approvals carried over | `community.general` use; OS locale `en_US.UTF-8`; `5c0aa7a LXSESSION` intentional. |

## Accepted findings (fix-worthy — numbering continues AI-21…)

### AI-21 — `~/.cache/dotfiles-debs/` is never created → fresh-host `deb` install fails (Blocker, NEW — category a/b)
- Verdict: ACCEPT (finder F-22; refuter concurs; **owner reproduced live**).
  `ansible/playbook.yml:301-310` (`Download deb packages`) writes to
  `"{{ dotfiles_home }}/.cache/dotfiles-debs/{{ item.key }}.deb"`, but no
  `file: state=directory` task creates that dir — the only `state: directory`
  tasks are `ansible/tasks/link.yml:21` (backup leaf), `ansible/playbook.yml:325`
  (archive parents) and `:377` (`.config`). Live probe:
  `ansible localhost -m get_url -a "url=file:///etc/hostname dest=/tmp/opencode/gztest/nonexistent-subdir-xyz/f.deb"`
  → `"msg": "Destination /tmp/opencode/gztest/nonexistent-subdir-xyz does not exist"`.
  On a fresh host the workstation `wezterm` entry fails at download, so run 1
  never converges — this **invalidates the VG-01 reasoning log's NET CONCLUSION**
  (which assumes run-1 convergence) for the workstation profile.
- Action: add a `file: path="{{ dotfiles_home }}/.cache/dotfiles-debs" state=directory mode=0755`
  task before download (or `validate_certs`/tempfile equivalent); re-prove with a
  `dotfiles_home=/tmp/...` override run.

### AI-22 — Galaxy floor `>=10.7.0` is declared but never enforced/upgraded (Major, category b)
- Verdict: ACCEPT (finder F-07; refuter concurs; owner confirmed from code).
  `ansible/requirements.yml:4` pins `version: '>=10.7.0'` (syntax itself valid —
  F-04's "invalid syntax" half is rejected), but `install:89`
  `if ! ansible-galaxy collection list 2>/dev/null | grep -q '^community\.general ';`
  is presence-only: a host with `community.general 9.x` skips the install and
  later fails at `ansible/playbook.yml:278` (`pipx: name: ruff==0.8.4`), which
  per `ansible-doc community.general.pipx` needs ≥10.7.0
  ("you can use package specifiers when `state=present' or `state=install'…
  `name=tox<4.0.0'"). F-05's "grep fragile" half is rejected (live
  `ansible-galaxy collection list | grep` matches `community.general  13.3.0` fine).
- Action: version-aware check in `install` (parse installed version, `--upgrade`
  when below floor) or unconditional `ansible-galaxy collection install --upgrade -r`.

### AI-23 — `lazygit` archive hardcodes `x86_64`; `wezterm` 2024 Debian12 pin unchanged (Major/Minor, category b)
- Verdict: PARTIAL as one item (finder F-25; owner verified URLs live).
  Both URLs return HTTP 200 (`lazygit_0.55.1…`, `wezterm-20240203…Debian12.deb`),
  and `starship 1.22.1` / `prettier 3.4.2` / `ruff 0.8.4` are all real releases —
  the "yanked/missing version" halves are rejected. Real kernels:
  (1) `ansible/vars/packages.json:198`
  `"url": "…/lazygit_0.55.1_Linux_x86_64.tar.gz"` breaks on `aarch64` (AI-01-class
  recurrence, Major on ARM); (2) `ansible/vars/packages.json:221`
  `wezterm-20240203-110809-5046fc22.Debian12.deb` is byte-identical to the pin
  AI-18 flagged — the 06-resolution did **not** refresh it (AI-18 half NOT-FIXED).
- Action: arch-template the lazygit URL (or add per-arch entries); bump/parameterize
  the wezterm pin per Debian release (trixie).

### AI-24 — `install` `-e*` over-match suppresses default profile; `-K` not detected (Minor + spec non-compliance, category a)
- Verdict: ACCEPT (finder F-39; refuter concurs; owner confirmed).
  `install:18-20` (`-e | --extra-vars) …;; -e*) …;; --extra-vars=*) …;;`) sets
  `saw_profile_e=true` for **any** `-e foo=bar`, so an unrelated extra var silently
  drops the default `-e dotfiles_profile=…` (falls back to playbook `vars:` default
  `workstation` — benign today, wrong in principle). And spec `04-installer-ux.md:37`
  promises forwarding of `--ask-become-pass / -K`, but the scan at `install:15-22`
  never matches `-K`/`--become-password-file`, so `-K` gets a duplicated
  `--ask-become-pass`. Bare `-e` at end of args is passed through dangling (minor).
- Action: only treat `-e`/`--extra-vars` as profile-suppressing when its value
  mentions `dotfiles_profile` (or parse values properly); add `-K` detection.

### AI-25 — `Clone git sources` still has no `creates`; "clone honors entry creates" claim is false (Minor/docs, category b)
- Verdict: ACCEPT (finder F-13; refuter concurs; owner confirmed by read).
  `ansible/playbook.yml:348-353` has `repo/dest/version/update` and **no**
  `creates`/`args.creates`; all three git entries ship `"build": []`
  (`ansible/vars/packages.json:231,243,255`), so the `subelements('value.build')`
  loop at `playbook.yml:365` yields zero items and per-entry `creates` is never
  evaluated. The 06-resolution §"AI-05 (…clone honors entry `creates`)" is factually
  wrong. Functional impact is Minor (pinned `update:`-when-pinned clones report ok
  when at the ref), but the spec now *requires* `creates` for git
  (`01-package-manifest-schema.md` "required `creates`") while the clone ignores it.
- Action: either honor `creates` on clone (e.g. `args: creates:`) or relax the spec
  for `build: []` entries; correct the 06-resolution text.

### AI-26 — `features:`/`version:` still quoted `default(omit)`; AN-02 resolution claim wrong, functionally harmless (nit, category b)
- Verdict: PARTIAL — finder right on fact, wrong on breakage (F-31; owner confirmed both halves).
  `ansible/playbook.yml:248-249` (`cargo`), `:263` (`npm`) still read
  `version: '{{ … | default(omit) }}'` / `features: '{{ … | default(omit) }}'` —
  the 06-resolution "AN-02 (unquoted `features`)" is false. Breakage half rejected:
  live `community.general.cargo … version: '{{ missing | default(omit) }}'` in
  `check_mode` → `failed=False` (Ansible unwraps the `omit` sentinel through the
  quotes here), so style-only. Drop the quotes anyway.
- Prior-round note: AN-02 verdict becomes PARTIALLY-FIXED (intent) / NOT-FIXED (letter).

### AI-27 — `dotfiles_deb_arch` fallback passes unknown arches through raw (Minor, category b)
- Verdict: PARTIAL (finder F-01; owner proved rescue works).
  Live `ansible localhost -m debug -a "msg={{ {'x86_64':'amd64'}['riscv64'] | default('FALLBACK') }}"`
  → `FALLBACK`: `default` **does** rescue a dict-miss, so the "KeyError before
  default" half is rejected. Remaining kernel (`ansible/playbook.yml:27`): arches
  outside `{x86_64, aarch64}` (`armv7l→armhf`, `i686→i386`, `riscv64`, …) fall
  through as the raw kernel name, which is not a valid apt `arch=` — a broken repo
  line by construction.
- Action: extend the map (`armv7l: armhf`, `i386/i686: i386`, …) with a sane default
  or fail fast on unknown arch.

### AI-28 — Six `home/` text files still mode `0755` (Low, category b)
- Verdict: ACCEPT (finder F-33; owner confirmed via `git ls-files -s home/`).
  `install` is `100755` and `README.md`/`home/.bashrc` are now `100644`, but
  `home/.gitconfig`, `home/.gtkrc-2.0`, `home/.xbindkeysrc`, `home/.xscreensaver`,
  `home/.zshenv`, `home/.zshrc` remain `100755` executable text. AN-03 PARTIALLY-FIXED.
- Action: `git update-index --chmod=-x` on the six files in a cleanup commit.

### AI-29 — Manifest assert is presence-only; type/empty-profile gaps remain (Minor, category b)
- Verdict: PARTIAL (finder F-15; live manifest itself is clean).
  `ansible/playbook.yml:31-53` checks presence (`rejectattr … defined`) and repo-id
  membership but not types: `script.args: list`, `archive.strip: int`,
  `git.build: list`, `version: str` unchecked; unknown extra keys allowed;
  `profiles: []` passes the `contains`/`difference` checks vacuously
  (selects into no profile — silent drop). The shipped manifest is well-typed
  (owner scanned), so latent/hardening only.
- Action: add `… | selectattr('profiles','equalto',[])` emptiness check and minimal
  type asserts for `args/build/strip`.

### AI-30 — fnm bootstrap converges but never refreshes; stat path diverges from cargo-installed fnm (Minor, category a/d)
- Verdict: PARTIAL (finder F-17/F-18; owner checked live paths).
  Ordering/or `executable:` halves rejected: `Install Node LTS via fnm`
  (`ansible/playbook.yml:191-199`) precedes npm (`:260-274`), and
  `~/.local/share/fnm/aliases/default/bin/npm` **exists** on this host, so F-18's
  "path may not exist" is rejected. Real kernels: (1) `creates:
  …/aliases/default` (`:195`) means a stale LTS is never refreshed (rotation
  staleness, accepted trade-off class); (2) `Check for fnm`
  (`:170-177`, path `…/.local/share/fnm/fnm`) reports missing when fnm came from
  elsewhere — this host has `/home/abhi/.cargo/bin/fnm` but **no**
  `~/.local/share/fnm/fnm` — so the playbook would redundantly reinstall fnm.
  `--skip-shell` flag and `fnm install --lts` usage verified valid
  (`fnm install --help` shows `--lts`); `fnm current` → `v22.19.0` here.
- Action: probe `command -v fnm` (like the cargo check at `:149-154`) in addition
  to the stat path; document the no-refresh trade-off.

### AI-31 — ensurepath wording/PATH/ordering + `sh`-vs-`bash` script pipe (Minor/nit batch, category b/d)
- Verdict: PARTIAL (finder F-11/F-26/F-41; `rc` handling sound).
  `ansible/playbook.yml:220-221` keeps `failed_when: rc != 0` (AI-04 fixed); the
  stdout-only `'already in path' not in stdout|lower` match is cosmetic-only risk
  (a pipx rewording flips changed-status, never masks failure) — nit.
  `ensurepath` (bootstrap, `:213-224`) still runs before linking, so shell-file
  edits can be clobbered by later links (AI-19 residual, Minor). `Run script
  installers` (`:289-291`) pipes to `sh -s --` under `executable: /bin/bash`
  while the fnm/bootstrap flow uses `bash -s -- --skip-shell` (`:180`) — latent
  inconsistency only (the `fnm` manifest entry is skipped once bootstrap's
  `creates` exists), nit.
- Action: match on `stdout+stderr`, keep `PIPX_BIN_DIR` assumption documented,
  use `bash` consistently in the script pipe (or justify `sh`).

### AI-32 — Docs/spec drift + error-path usage to stdout (nit/docs batch, category a/b)
- Verdict: PARTIAL (finder F-27/F-29/F-38; each kernel small).
  (1) `extra_opts` zip guard (`ansible/playbook.yml:341`,
  `is not search('\\.zip$')`) is case-sensitive (`.ZIP`) and misses `?download=1`
  query strings — nit; the "mkdir every run" half is rejected (`file:
  state=directory mode=0755` is idempotent, reports ok when correct).
  (2) `install:7-9` `usage()` prints to stdout even on error paths (`:26-28`,
  `:50-52`) — nit; the `BASH_SOURCE`/`[[`/`pipefail`-under-dash halves are
  rejected (`install:5` is `#!/usr/bin/env bash`), and `--profile=` empty is
  correctly rejected by `:48-54`. (3) Spec drift: `03-multi-source-install.md`
  says script installs via "`get_url` to temp + execute" but code pipes
  `curl|sh` (`:290`); cargo "`creates`" wording vs `community.general.cargo
  state: present` (module path needs none); `01` git "default branch without
  tracking" vs string-`update:` (which however coerces correctly — see AR-12).
- Action: one docs touch-up pass; fix `.ZIP`/query-suffix guard; send error-path
  usage to stderr.

## Prior-round regression (re-verified from code; FIXED / PARTIALLY-FIXED / NOT-FIXED / CONFIRM-REJECT)

| ID | New verdict | Proof |
|---|---|---|
| AI-01 | FIXED (residual AI-27) | `ansible/playbook.yml:27` map + `:130` templated `dotfiles_deb_arch` |
| AI-02 | FIXED | `ansible/requirements.yml` + `install:88-91` galaxy bootstrap + `README.md:36-43` note |
| AI-03 | FIXED | `:144` `when: … is changed` + `cache_valid_time: 3600` on `:68,:142,:231`; loop-register `is changed` proven sound (mixed→True, skipped/empty→False) |
| AI-04 | FIXED (cosmetic residual AI-31) | `:220-221` `changed_when` stdout + `failed_when: rc != 0` |
| AI-05 | PARTIALLY-FIXED | Pins (`packages.json:230 0.8.0, :242 v0.7.1, :254 0.35.0`) + `:353` update-when-pinned done; "clone honors `creates`" FALSE (AI-25) |
| AI-06 | FIXED | `:361` `shell: '{{ build_step }}'` + `:364,:369` per-step `{cmd, creates}`; string-step `default` rescue proven live |
| AI-07 | FIXED (hardening residual AI-29) | `:31-53` assert + `regex_replace('^~',…)` on `:292,:324,:337,:339,:351,:363-364`; no `~otheruser` entries in tree |
| AI-08 | FIXED | `prettier` (npm, `packages.json:179`), `ruff` (pipx, `:188`), `lazygit` (archive, `:197`) fixtures present |
| AI-09 | FIXED | `ansible/tasks/link.yml:29-68` predicts + `:78` check-gates real link; owner re-ran `--check --skip-tags packages` → `ok=64 changed=0 failed=0` |
| AI-10 | FIXED (refresh residual AI-30) | `:178-199` fnm + `fnm install --lts` + `:267` alias npm + PATH; alias npm path exists on host |
| AI-11 | FIXED | `:60-69` gnupg/ca-certificates before `:74-` dearmor; no cycle (apt http needs no ca-cert) |
| AI-12 | FIXED **but regressed** (Blocker AI-21) | `~/.cache/dotfiles-debs/` (`:304,:315`) + `:105-113` `.asc` prune done, but cache dir itself never created → fresh-host deb fails |
| AI-13 | NOT-FIXED (waived, process-only) | `272b3e9`+`3ef5e56` dup + ordering still in history; no rewrite per resolution |
| AI-14 | FIXED | All `01–05 Status: Done` (owner grepped), `00-overview` + `06 Done` |
| AI-15 | FIXED | `install:67-68` strict `debian)` only |
| AI-16 | PARTIALLY-FIXED | Floor declared (`requirements.yml:4`); enforcement missing (AI-22) |
| AI-17 | FIXED | `:236-243` single `apt: name=<list>`; pipx-dup guard `:209` sound |
| AI-18 | PARTIALLY-FIXED | `starship 1.22.1` pinned (`:173`) FIXED; `wezterm` `:221` 20240203/Debian12 NOT-FIXED (AI-23) |
| AI-19 | PARTIALLY-FIXED | pipx PATH (`:284`) + cargo via `home/.profile:18`; bootstrap-before-link clobber order remains (AI-31) |
| AI-20 | PARTIALLY-FIXED | strip-tar-only `:341`, archive-parent guard `:330`, help-to-stdout, `BASH_SOURCE` fallback done; NOT-FIXED: `-e` over-match/`-K` (AI-24), usage-to-stdout-on-error + drift (AI-32) |
| AN-01 | FIXED | `home/.bashrc:10` `[ -f … ] && source …`, after `home/.bashrc:6` non-interactive guard; `shellcheck install` clean (rc=0) |
| AN-02 | NOT-FIXED letter / fixed intent (AI-26) | File still quoted (`playbook.yml:249`); functionally harmless (live quoted-`omit` probe passes) — 06-resolution text wrong |
| AN-03 | PARTIALLY-FIXED | `install 100755`, `README.md`/`home/.bashrc` `100644` ok; six `home/` files still `100755` (AI-28) |
| AR-01 | CONFIRM-REJECT | `5c0aa7a` intentional |
| AR-02 | CONFIRM-REJECT | Always-ask is spec-mandated (`04-installer-ux.md`) |
| AR-03 | CONFIRM-REJECT | No locale failure evidence |
| AR-04 | CONFIRM-REJECT | `in` without `\|list` works (`playbook.yml:209`) |
| AR-05 | CONFIRM-REJECT | Checksums deferred to follow-up 3 (`00-overview.md`) |
| AR-06 | CONFIRM-REJECT | Deps auto-install; no age evidence; fixture URLs all HTTP 200 |
| AR-07 | CONFIRM-REJECT | `\|` binds tighter than `not`/`or` (`link.yml:14,24,34…` grouping valid); no-profile-gating by design (`05`); `source /etc/os-release` reads `ID=` only, no command substitution (`install:63-65`) |

## Rejected findings (false alarms — no action; finder IDs in parens)

- AR-08 — Repo-line spacing/variant alarmism (F-02, F-03). Both shipped lines use
  exactly `{{ ansible_architecture }}` (`ansible/vars/repos.json:5,:10`), matching
  the `replace()` at `ansible/playbook.yml:130`; `signed-by` paths match `keyring`
  (`repos.json:3` vs `:5`). Upstream codename availability (trixie) is unproven,
  not a code bug.
- AR-09 — Galaxy grep/install fragility (F-05, F-06). Live grep matches
  `community.general  13.3.0`; `ansible-galaxy` ships with the `ansible` package
  the wrapper installs, and apt errors stay visible.
- AR-10 — Loop-register `is changed` (F-08, F-09). Owner probes: mixed loop →
  `True`, all-skipped → `False`, empty loop → register
  `{changed: False, skipped: True}` and `is changed` → `False`. Gating is correct,
  including the empty-selection case.
- AR-11 — Triple `apt update` (F-10). Three tasks defined (`playbook.yml:67,:141,:230`)
  but all carry `cache_valid_time: 3600`; at most one real update per run.
- AR-12 — `"False"`-string `update:` (F-12). Owner probe: `stat … follow: "{{ 'zzz'=='yyy' }}"`
  (string `"False"`) leaves the symlink unfollowed (`islnk=True`) while `"True"`
  follows it — Ansible boolean coercion handles `playbook.yml:353` correctly.
- AR-13 — String build-step `creates` lookup (F-14). `("justastring".creates|default("FALLBACK"))`
  → `FALLBACK`; `chdir` dest always exists (clone precedes builds); manifest is trusted input.
- AR-14 — `^~` vs `~otheruser`/bare-`~` (F-16). No `~otheruser` entries exist; all
  manifest paths are `~/…`. At most a `^~/` hardening nit.
- AR-15 — Link predict inflation/fail-grouping (F-19, F-20). Predicts are
  `ansible_check_mode`-gated (no live inflation, no double-count — real link is
  skipped in check-conflict at `link.yml:78`); the unguarded `fail` is what makes
  check+conflict+`backup=false` fail correctly; `mv -- <dst> <group>/` handles
  file/dir; `|`-vs-`not` grouping valid (AR-07).
- AR-16 — ca-certificates chicken-and-egg (F-21). Prereq apt runs before any
  `get_url https`, and apt http needs no ca-certificates.
- AR-17 — Duplicate `pipx` apt install (F-24). `playbook.yml:209`
  `"'pipx' not in …|map(attribute='value.package')"` skips the dup (manifest ships
  apt `pipx`); assert (`:31-53`) runs before any `map(package)` use.
- AR-18 — deb re-download/mtime churn (F-28). `get_url` default `force:` is
  content-compare (owner probe: same file twice → `changed True` then `False`);
  same-user races negligible.
- AR-19 — Relative inventory (F-30). By design: root `ansible.cfg:2`
  `inventory = ansible/inventory.yml` + `install:93` `cd "${repo_root}"`, mandated
  by spec 04; README documents `./install` and direct-playbook equivalents.
- AR-20 — `.bashrc` nvm guard/SC1091/dual-manager (F-32). Guarded (`home/.bashrc:6,10`);
  shellcheck clean; zsh-fnm vs bash-nvm coexistence is confusing, not breakage.
- AR-21 — Cargo check false-negative/masking (F-34). `creates: …/.cargo/bin/cargo`
  plus `when: rc != 0` (`playbook.yml:160-166`) covers the off-PATH case; `rc` is
  preserved (`failed_when: false` only, `changed_when: false`).
- AR-22 — pipx `name==ver` vs `source:` (F-35). `ansible-doc` documents specifiers
  in `name` for `present`/`install` since 10.7.0; `source` is for URLs/dirs.
- AR-23 — `dirname`/lazy-vars/excludes/`find` (F-36, F-37). Namespaced
  `ansible.builtin.dirname` (`playbook.yml:11`); playbook `vars:` are lazy so the
  assert (`:31-53`) runs before selections are consumed; single-`README.md`
  exclusion and per-run timestamped backup root are spec-05-mandated behavior.
- AR-24 — `source /etc/os-release` as code-exec (F-40). File only reads
  `distribution_id="${ID:-}"` (`install:63-65`); no command substitution present;
  prior AR-07 stands.

## New issues from this round (neither prior round examined — cross-refs to AI-21…)

- AN-04 → AI-21: deb cache dir never created (Blocker). Genuinely new surface from
  the AI-12 fix; prior round never checked parent-dir creation.
- AN-05 → AI-22: galaxy floor presence-check never upgrades (Major). New surface
  from the AI-02 fix; version-floor enforcement was assumed, not coded.
- AN-06 → AI-23: arch-specific fixture URL (`lazygit …_Linux_x86_64.tar.gz`,
  `packages.json:198`) breaks `aarch64` (Major on ARM). New coverage from AI-08 fixtures.
- AN-07 → AI-31 (part): script pipe uses `sh` (`playbook.yml:290`) while fnm flow
  needs `bash` (Minor/nit). New inconsistency inside the AI-08/AI-10 fixture work.
- AN-08 → AI-25: dead `creates` on `build: []` git entries + false "clone honors
  `creates`" resolution text (docs). New spec-drift class from the AI-05 fix.

## Verification gaps (VG-01 still open; VG-02 new)

### VG-01 — Fresh-host proof (still OPEN, now more urgent)
- Still unproven on a fresh Debian stable host/VM with sudo+network: full second-run
  `changed=0`, server-vs-workstation split effects, `apt-cache policy` for
  third-party packages, key+repo second-run `ok`, real (non-check) conflict `mv`
  placement, `-e dotfiles_backup_conflicts=false` live failure, `--check` accuracy
  for packages. Locally proven this round (owner): dotfiles `--check` on the
  already-linked host → `ok=64 changed=0 failed=0`; manifest computation →
  server 20 / workstation 31 entries, workstation-only set exactly
  `{alacritty,dunst,flameshot,lxsession,picom,qtile,rofi,vscode,wezterm,xbindkeys,xscreensaver}`;
  `syntax-check` passes; `shellcheck`/`bash -n` clean; both manifests valid JSON.
- Escalation: AI-21 means run 1 currently **cannot** converge on a fresh
  workstation host (wezterm download fails), so the VG-01 reasoning log's
  "run 2 `changed=0` follows iff run 1 converges" does not currently hold for the
  default profile. Fix AI-21 first, then run the acceptance suites.

### VG-02 — Reasoning-log residual risks carried forward (untestable without a fresh host)
- (a) `fnm install --lts` + `default`-alias flow on a bare host (only the
  alias-symlink layout was verified against this host's existing fnm);
  (b) `community.general.npm executable=` alias path before any shell ran
  `fnm env` (path exists here, not proven bare); (c) `pipx ensurepath` stdout
  wording on Debian's packaged pipx version; (d) wezterm Debian12 `.deb` on trixie
  (still installs per HTTP 200, not per `dpkg -i`); (e) `starship 1.22.1` crate
  vs current stable rustc (compile time/unproven). Next fresh-host run should
  check these first, plus AI-21/AI-22/AI-23 fixes.

## Handoff note for the next chat

Suggested work order (risk/effort): AI-21 (deb cache dir — Blocker, one `file`
task) → AI-22 (galaxy floor enforcement) → AI-23 (lazygit arch URL + wezterm pin)
→ AI-24 (`-e`/`-K` parsing) + AI-25/AI-26 (git `creates` decision + unquote
`omit`s, incl. correcting the 06-resolution text) → AI-27 (arch map) + AI-28
(mode bits) + AI-29 (assert types) + AI-30 (fnm probe/refresh note) → AI-31/AI-32
(nit/docs batch) → VG-01/VG-02 (fresh Debian VM acceptance: second-run
`changed=0`, `apt-cache policy`, conflict `mv`, `backup=false` failure).
Each fix should cite its AI-/AN-/VG- id in the commit message. Review only —
nothing was fixed or committed in this round (`git status` clean apart from this file).
