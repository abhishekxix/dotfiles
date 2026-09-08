# Always-install toolchains; fnm via cargo

| Field | Value |
|---|---|
| Status | Planning |
| Component | ANSIBLE |
| Created | 2026-09-08 |

## Goal

Make the language-toolchain bootstrap unconditional — rustup/cargo, fnm,
Node LTS (npm), and the flatpak CLI are always installed and set up on every
playbook run, regardless of which manifest sources the active profile
selects. Switch the fnm install method from the curl script to
`cargo install`, and move `tree-sitter-cli` from the npm source to cargo.

## Context & Research

- User decision (2026-09-08): toolchains must **always** be installed —
  "cargo, rustup, fnm, node, npm, and flatpak and flatpak cli should all
  always be installed and set up". The current design gates every bootstrap
  task on "some selected manifest package needs this toolchain"
  (`.specs/INSTALLER/debian-fresh-setup/03-multi-source-install.md` step 2).
- Coupling that forces the rework: `tree-sitter-cli` is the **only**
  `npm`-source entry, and the fnm/node bootstrap is gated on
  `dotfiles_pkgs_npm | length > 0`. Moving tree-sitter-cli to cargo would
  leave zero npm entries and permanently orphan the fnm bootstrap — so
  ungating is a prerequisite, not a nicety.
- fnm via cargo: `cargo install fnm` puts the binary at `~/.cargo/bin/fnm`.
  This host already runs a cargo-installed fnm there (observed in
  `.specs/INSTALLER/debian-fresh-setup/07-review-attestation.md` AI-30 and
  `08-fix-round.md`), so the playbook's curl install is currently dead weight
  here; switching makes the playbook match reality.
- The fnm *data* dir (`~/.local/share/fnm` — node versions, `aliases/default`)
  is chosen at runtime by FNM_DIR default and is stable regardless of binary
  origin (`09-fix-round.md` item 9, observed live). The `aliases/default`
  creates-marker for the Node LTS task therefore stays valid.
- `--skip-shell` (curl installer) becomes moot: cargo install touches no
  shell config, and `home/.zshrc` already runs `eval "$(fnm env ...)"`.
- Manifest schema (`ansible/vars/packages.schema.json`): `cargo` entries
  require `source`, `crate`, `profiles`; `npm` entries require `package`.
  tree-sitter-cli's entry swaps `package` → `crate` and stays schema-valid.
- Preflight already asserts `community.general >= 10.7.0`
  (`ansible/tasks/preflight.yml:31`), the floor for the cargo module era.
- AI-10 lesson (`06-review-attestation.md`): a task's `creates` marker and
  its probe/stat path must agree — the fnm stat moves to `~/.cargo/bin/fnm`
  together with the new `creates`.
- AI-30 lesson: probe PATH (`command -v fnm`) in addition to the stat so an
  fnm installed by other means is not reinstalled. Still applies — only the
  *preferred* install method changes.

## Non-goals

- No `fnm` entry in `packages.json` — the bootstrap task remains the single
  source of truth for fnm (the INSTALLER(17) rationale); only its install
  method changes.
- npm source support stays in the schema and `packages.yml` (harmless no-op
  with zero npm entries; the `dotfiles_pkgs_npm` var remains for the npm
  install loop only, no longer gating toolchain tasks).
- No version pins on the cargo-installed crates (`fnm`, `tree-sitter-cli`);
  consistent with the manifest's optional `version` field.
- No return of pipx (removed in `.specs/ANSIBLE/remove-pipx-pipeline/`).
- No edits to historical specs under `.specs/INSTALLER/debian-fresh-setup/` —
  this spec supersedes their gating design.
- No migration/cleanup of a legacy curl-installed `~/.local/share/fnm/fnm`
  binary on hosts that ran the old playbook; step 03 stops *preferring* that
  path but does not delete it.

## Steps

Each step maps to exactly one commit, named `ANSIBLE(<NN>): <summary>`.

### 01 — tree-sitter-cli: npm → cargo

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** entry becomes `{"crate": "tree-sitter-cli", "profiles":
  ["workstation"], "source": "cargo"}` (fields alphabetized per AGENTS.md).
  Zero npm entries remain; the npm install loop becomes a no-op until a
  future npm entry appears.
- **Acceptance:**
  - [ ] `python3 -m json.tool ansible/vars/packages.json` exits 0.
  - [ ] `ansible-playbook --check --tags packages ansible/playbook.yml`
    passes preflight schema validation.
  - [ ] The "Install cargo crates" loop now includes `tree-sitter-cli`
    (visible in `--check` task labels).

### 02 — Toolchain bootstrap runs unconditionally

- **Files:** `ansible/tasks/toolchain.yml` (EDIT), `ansible/playbook.yml`
  (EDIT — comment only)
- **Changes:** drop the `dotfiles_pkgs_{cargo,npm,flatpak} | length > 0`
  gates from all eight toolchain tasks (cargo check, rustup install, fnm
  stat + PATH probes, fnm install, Node LTS, flatpak check + CLI install).
  Idempotency guards stay: rc probes, stat checks, `creates` markers. Update
  the section header comment and the playbook import comment
  ("auto, gated on selected sources" → "always installed").
- **Acceptance:**
  - [ ] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
  - [ ] `--check --tags packages` run: toolchain tasks are no longer skipped
    for gate reasons; on this host each still skips via its
    existing-install guard (cargo present, fnm on PATH, default alias
    exists, flatpak installed).

### 03 — fnm installs via cargo

- **Files:** `ansible/tasks/toolchain.yml` (EDIT)
- **Changes:** "Install fnm (node provider)" runs
  `cargo install fnm --locked` with `creates: ~/.cargo/bin/fnm` and a PATH
  that prepends `~/.cargo/bin` (rustup) — covers an apt cargo too. The
  "Check for fnm" stat moves to `~/.cargo/bin/fnm` (aligns with `creates`,
  AI-10). The AI-30 comment is rewritten: cargo is now the install source;
  the PATH probe still skips a foreign fnm. The "Install Node LTS via fnm"
  PATH drops the leading `~/.local/share/fnm` entry — that dir is data-only
  now (`~/.cargo/bin/fnm` resolves the binary), so a legacy curl-installed
  binary lingering there no longer shadows the cargo one.
- **Acceptance:**
  - [ ] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
  - [ ] On this host the fnm install task skips (stat `~/.cargo/bin/fnm`
    exists) and `fnm --version` still works.
  - [ ] Node LTS task untouched behavior: skips via the `aliases/default`
    creates-marker.

## Risks & Rollback

- **Compile time:** `cargo install fnm` and `cargo install tree-sitter-cli`
  build from source (~1–3 min each, first run on a fresh host only;
  `creates`/module idempotence skips later runs). Accepted — cargo install
  is the explicit user requirement (same trade-off class as AR-04's
  starship note, which moved to archive for unrelated pin-rot reasons).
- **Duplicate binaries:** hosts that ran the old curl installer may keep a
  stale `~/.local/share/fnm/fnm`. Step 03 removes it from the node task's
  PATH so it can't shadow the cargo binary; it is not deleted (non-goal).
- **Fresh-node freshness:** Node LTS still converges once
  (`aliases/default` marker, never auto-upgraded) — unchanged semantics.
- **Rollback:** one commit per step; `git revert` of 03 restores the curl
  installer (probes keep their shape), of 02 restores source gating, of 01
  restores the npm entry. Bisect stays meaningful because every step lands
  with the playbook green (`--syntax-check` + `--check` verified).
