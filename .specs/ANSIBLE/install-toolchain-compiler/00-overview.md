# Guarantee a linker for cargo-built toolchains

| Field | Value |
|---|---|
| Status | Planning |
| Component | ANSIBLE |
| Created | 2026-09-08 |

## Goal

The toolchain bootstrap compiles from source (`cargo install fnm --locked`
in `toolchain.yml`, cargo crates in `packages.yml`), but nothing guarantees a
C compiler/linker before those tasks run. Install `build-essential` as part of
the always-on bootstrap so every fresh Debian host can complete the toolchain
section.

## Context & Research

- Found in the adversarial review of PR #8 (`always-install-toolchains`),
  confirmed empirically: a fresh `debian:stable-slim` + the playbook's exact
  rustup bootstrap (`--profile minimal`) has no `cc`/`gcc`/`make` and
  `rustc` fails with `error: linker 'cc' not found`.
- Ordering gap: `ansible/playbook.yml` imports `tasks/toolchain.yml` (`:68`)
  before `tasks/packages.yml` (`:72`), and packages.yml installs the
  `package-deps.json` build deps ("Install build dependencies", `:42-49`)
  only *after* the toolchain section — too late for `cargo install fnm`
  (`toolchain.yml:40-44`).
- Repo treats a compiler as non-guaranteed: `gcc` appears only as a picom
  build dep (`ansible/vars/package-deps.json:4`), so tree-sitter-cli's cargo
  install is protected only transitively via picom's selection, and fnm not
  at all. `preflight.yml` has no linker assert; CI (`validate.yml`) runs
  pre-commit only — no ansible coverage.
- The old fnm install method (curl script) downloaded a prebuilt static
  binary (verified against `https://fnm.vercel.app/install`: it fetches
  `fnm-linux.zip`, unzips, chmod) and needed no linker — step 03 of
  `always-install-toolchains` introduced the compile requirement.
- Package choice: `gcc` only *Recommends* `libc6-dev`
  (`apt-cache show gcc`), which is not a guarantee on minimal hosts;
  `build-essential` hard-*Depends* on `libc6-dev | libc-dev`, `gcc`, `g++`,
  `make`, `dpkg-dev` (`apt-cache show build-essential`). Rust linking needs
  cc + libc dev files; tree-sitter's `cc`-crate C runtime needs a C compiler.
- User decision (2026-09-08): build-essential is a **toolchain** — it follows
  the always-install rule like cargo/fnm/flatpak, with no "is a linker
  already present" gate. The apt module's `state: present` is the only
  already-present skip (ok when installed, installs when missing). A probe
  (`cc --version`) was considered and rejected: a clang-only host would skip
  and end up without gcc/g++/make, violating "always installed".
- Shape: unconditional `become` apt install with `update_cache`
  (fresh-host empty cache) + `cache_valid_time` — the same knobs as the
  flatpak CLI task in the same file (`toolchain.yml`), minus its probe;
  module idempotence comes from `state: present` (same as the apt loops in
  `packages.yml`).
- Placement: immediately after "Install rustup (cargo provider)" and before
  "Check for fnm" — the first cargo-compiling task ("Install fnm") then has
  its linker guaranteed locally in file order.

## Non-goals

- No `build-essential` entry in `packages.json` / `package-deps.json` — the
  toolchain bootstrap is the single source of truth (flatpak CLI precedent);
  manifest entries would gate it on profile selection, which defeats the
  purpose.
- No preflight linker assert (a cheap hardening idea from the review — keep
  it as a possible follow-up spec, out of scope here).
- No clang/musl target setup, no `RUSTFLAGS`/linker pinning.
- No changes to `packages.yml` (its dep-install ordering stays as is; the
  toolchain guarantee makes it irrelevant for fnm and a backstop for crates).

## Steps

Each step maps to exactly one commit, named `ANSIBLE(<NN>): <summary>`.

### 01 — build-essential in the toolchain bootstrap (always installed)

- **Files:** `ansible/tasks/toolchain.yml` (EDIT)
- **Changes:** insert one unconditional task between "Install rustup (cargo
  provider)" and "Check for fnm":
  - "Install build tools (cargo linker)" — comment explaining why (a
    toolchain like cargo/fnm/flatpak: always installed regardless of
    manifest sources or profile; cargo installs in this section and in
    packages.yml link with `cc`; `build-essential` chosen over `gcc`
    because it hard-Depends on `libc6-dev` while gcc only Recommends it; no
    rc probe — apt `state: present` is the idempotence), then
    `become: true`, `ansible.builtin.apt: name: build-essential,
    state: present, update_cache: true, cache_valid_time: 3600`,
    `tags: [packages]`.
- **Acceptance:**
  - [ ] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
  - [ ] Real run of the toolchain section on this host: "Install build
    tools (cargo linker)" evaluates unconditionally and reports ok /
    `changed=0` (build-essential already present — apt module idempotence);
    section ends `changed=0` (all other guards unchanged).
  - [ ] `ansible-playbook --check --diff --skip-tags packages` preview shows
    the file change only (no live-path effects).

## Risks & Rollback

- **Disk footprint:** build-essential pulls g++/make (~hundreds of MB with
  libc6-dev on a bare host). Accepted — the bootstrap is explicitly
  "always installed", and this host already runs build-essential, so the
  task is a no-op here.
- **Server profile cost:** server hosts now also get build-essential. That
  is the point of the fix (toolchains are unconditional since PR #8).
- **become:** the apt task needs sudo like the flatpak CLI task — same
  existing requirement, no new privilege surface.
- **Rollback:** single commit; `git revert` restores the pre-PR#8-review
  behavior (and re-opens the fresh-host linker gap — deliberate).
