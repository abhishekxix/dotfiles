# Replace hand-rolled argv parsing with argparse

| Field | Value |
|---|---|
| Status | Done |
| Component | INSTALLER |
| Created | 2026-09-07 |

## Goal

Swap the `install` wrapper's hand-rolled prescan/parse loops for stdlib
`argparse` so flag handling follows standard CLI conventions and the common
footguns (split vs `=`-joined forms, error messages, exit codes, help
generation) stop being our problem. No new dependencies, no venv (per the
earlier decision), no UI.

## Context & Research

- Current code has two custom loops: a pre-scan (become flags, `-e` value
  capture) and a main loop (`--profile`, `-h/--help`, passthrough). Both
  replicate what argparse does natively.
- Mapping:
  - `--profile` → `add_argument(choices=PROFILES)`: validates and errors
    automatically (both `--profile NAME` and `--profile=NAME`).
  - `-e/--extra-vars` → `action="append"`: captures values in all three forms
    (`-e V`, `-eV`, `--extra-vars=V`, plus `--extra-vars V`). The
    `dotfiles_profile` suppression check becomes a simple `any()` over the
    captured values.
  - `-K/--ask-become-pass`, `--become-password-file` → real arguments instead
    of a regex-ish pre-scan.
  - Everything unknown → `parse_known_args()` extras = ansible-playbook
    passthrough, order preserved.
- Accepted deviations from the bash-era behavior (all standard argparse
  semantics — the point of the change):
  1. `-K` / `--become-password-file` are consumed and **re-emitted** into the
     passthrough (normalized to canonical form) so ansible still receives
     them; relative order vs other passthrough flags may change (irrelevant
     to ansible).
  2. A bare `--` separator is consumed by argparse and not forwarded.
  3. Invalid flags/values (e.g. `-Kx`, `-e` with no value) exit 2 with a
     standard argparse message instead of being silently passed through.
  4. Invalid profile exits 2 with an argparse `choices` message.
  5. Help output is argparse-generated (same content, standard layout).

## Non-goals

- No third-party parsing libs (click/typer) — would need a venv/pip bootstrap.
- No UI/animations; no changes to bootstrap, collection check, or exec logic.

## Steps

Each step maps to exactly one commit, named `INSTALLER(<NN>): <summary>`.

### 01 — argparse-based parsing

- **Files:** `install` (EDIT)
- **Changes:**
  - Replace `prescan()` and `parse()` with a single `parse()` built on
    `argparse.ArgumentParser` (`allow_abbrev=False`, `RawDescriptionHelpFormatter`,
    wrapper-behavior notes + examples as epilog).
  - Become markers consumed then re-appended to passthrough canonically;
    `--ask-become-pass` injected by the wrapper only when the user passed
    none (unchanged rule).
  - Profile injection rule unchanged: skip `-e dotfiles_profile=<p>` when any
    user `-e` value mentions `dotfiles_profile`.
- **Acceptance:**
  - [x] Fake-bin parity: final `ansible-playbook` argv identical for the
        port-spec case set (modulo documented re-emission order for `-K`
        cases, verified present).
  - [x] `--profile=server` and `--profile server` equivalent; invalid profile
        exits 2 with a clear message.
  - [x] `-e`, `-eV`, `--extra-vars=V`, `--extra-vars V` all suppress the
        injected profile default when the value mentions `dotfiles_profile`.
  - [x] `-K`/`--ask-become-pass`/`--become-password-file F` re-emitted so the
        wrapper does not add a duplicate `--ask-become-pass`.
  - [x] `./install --help` renders argparse help including wrapper notes.
  - [x] Piped output contains no prompt/garbage; `--help | cat` works.

### 02 — E2E verification + spec close

- **Files:** `.specs/INSTALLER/install-argparse-parsing/00-overview.md` (EDIT)
- **Changes:** Full wrapper run against the real toolchain; close spec.
- **Acceptance:**
  - [x] `./install --check --diff --skip-tags packages` still clean
        (`changed=0`, exit 0).
  - [x] Spec status set to Done, acceptance boxes ticked.

## Risks & Rollback

- Parsing behavior shifts (documented above) are intentional; the risk is a
  flag form we missed. Mitigation: replay the full fake-bin case matrix from
  the port spec before committing. Rollback: `git revert` the step — bootstrap
  and exec logic untouched.
