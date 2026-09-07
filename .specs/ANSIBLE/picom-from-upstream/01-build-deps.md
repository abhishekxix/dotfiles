# 01 — package-deps.json: build-dependency manifest

- **Files:** `ansible/vars/package-deps.json` (CREATE),
  `ansible/vars/package-deps.schema.json` (CREATE), `ansible/playbook.yml` (EDIT)
- **Changes:**
  - New deps manifest keyed by the **dependent package name** (a key from
    `packages.json`); value = flat list of apt package names. First entry:
    picom's Debian build deps from the upstream v12 README, plus `gcc` and
    `pkg-config` (upstream assumes usual build tools; `meson`/`ninja-build`
    are already in the upstream Debian list).
  - Playbook vars: load `package-deps.json` (strip `$schema`), select entries
    whose key is among the packages selected for the current profile, union
    their apt lists into `dotfiles_deps_apt` — so e.g. server machines never
    install picom's X/GL dev packages.
  - Validation asserts (separate "Validate build-deps manifest" task next to
    the manifest validation): must be a mapping; keys must exist in
    `packages.json` (fail fast on typos/stale keys); values must be
    non-empty lists of non-empty strings.
  - New `become` task "Install build dependencies" **immediately after
    "Install apt packages" and before all per-source install/build tasks** —
    the explicit deps-before-build ordering guarantee. One apt transaction.
- **Acceptance:**
  - [x] `ansible-playbook --check --diff --skip-tags packages
        ansible/playbook.yml` passes (validation tasks green).
  - [x] Negative fixtures fail the new asserts (unknown key, empty list,
        non-list value — caught via `select('string')` since strings are
        Jinja sequences —, empty string item).
  - [x] All picom deps resolve via `apt-cache policy` (no unknown names).
