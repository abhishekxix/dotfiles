# Expose script-installed binaries via ~/.local/bin

| Field | Value |
|---|---|
| Status | Planning |
| Component | ANSIBLE |
| Created | 2026-09-08 |

## Goal

Script-source installers land their binaries outside `~/.local/bin` (opencode
hardcodes `~/.opencode/bin`). Add archive-style `link` support to the script
source so entries can expose a binary on PATH via a `~/.local/bin` symlink,
use it for opencode, and drop the `.zshenv` PATH-dir entry added in
`dbfe779`.

## Context & Research

- User decision (2026-09-08): no `~/.opencode/bin` on PATH — symlink
  `$HOME/.opencode/bin/opencode` → `$HOME/.local/bin/opencode` instead. The
  symlink already exists on this host (created manually 2026-09-05), so this
  change is for future hosts.
- Upstream opencode installer hardcodes `INSTALL_DIR=$HOME/.opencode/bin`
  (install.sh:68) and, without `--no-modify-path`, appends PATH exports into
  the first shell config it finds (zsh case: `.zshrc` — a repo-tracked
  symlink). The current entry already passes `--no-modify-path` (fadb829).
- `~/.local/bin` is on PATH via `.profile:16` — the same mechanism the
  archive links (nvim) and direct installs (starship, picom) rely on.
- The archive source already supports `link`
  (`packages.yml:194-214`, schema `relPath`, validator
  `.bin/validate-manifest.py:77-82`); the script source lacks it.
  Generalizing beats hardcoding an opencode task in `packages.yml` (the
  manifest is the source of truth).
- Script source has no `dest`; its install root is the `creates` file's
  directory. So `link` is relative to `dirname(creates)`: opencode's
  `creates: ~/.opencode/bin/opencode` + `link: opencode` →
  `~/.local/bin/opencode` → `~/.opencode/bin/opencode`.

## Non-goals

- No new script entries beyond opencode.
- No changes to archive `link` semantics.
- No removal of the existing manual symlink on this host (`force: true`
  keeps it converging).

## Steps

Each step maps to exactly one commit, named `ANSIBLE(<NN>): <summary>`.

### 01 — link support for script installers

- **Files:** `ansible/vars/packages.schema.json` (EDIT),
  `.bin/validate-manifest.py` (EDIT), `ansible/tasks/packages.yml` (EDIT)
- **Changes:** script definition gains optional `link` (`relPath`);
  `relPath` description generalized (install root: `dest` for archive, the
  `creates` file's directory for script). Validator's link check applies to
  archive and script. `packages.yml` mirrors the archive tasks:
  "Ensure ~/.local/bin exists for script links" (gated on script entries
  with `link`) and "Link script binaries into ~/.local/bin" (`src` =
  `dirname(creates)`/`link`, `path` = `~/.local/bin/` + `basename(link)`,
  `state: link`, `force: true`).
- **Acceptance:**
  - [ ] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
  - [ ] `python3 .bin/validate-manifest.py` passes.
  - [ ] Negative test: a script entry with `link: "/abs"` or `link: "~/x"`
    is rejected by the validator.

### 02 — opencode uses link; drop the .zshenv PATH entry

- **Files:** `ansible/vars/packages.json` (EDIT), `home/.zshenv` (EDIT —
  revert of `dbfe779`)
- **Changes:** opencode entry gains `link: "opencode"`; `.zshenv` returns to
  cargo-env-only (no `~/.opencode/bin`).
- **Acceptance:**
  - [ ] `python3 .bin/validate-manifest.py` passes; lexical key order intact.
  - [ ] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
  - [ ] On this host `~/.local/bin/opencode` resolves to
    `~/.opencode/bin/opencode` (pre-existing symlink; task converges).

## Risks & Rollback

- **Installer upgrades:** opencode self-updates the binary in place at
  `~/.opencode/bin/opencode`; the symlink target stays valid.
- **Future script entries without `link`:** unaffected (link tasks are
  gated on `link` being defined).
- **Rollback:** one commit per step; `git revert` of 02 restores the
  .zshenv PATH entry and link-less entry, of 01 removes the mechanism.
