# 02 — picom git source entry with build step

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** Replace the apt `picom` entry with a `git` entry pinned to the
  v12 tag, building and installing per-user:

  ```json
  "picom": {
    "source": "git",
    "repo": "https://github.com/yshui/picom.git",
    "version": "v12",
    "build": [
      "rm -rf build && meson setup --buildtype=release -Dprefix=\"$HOME/.local\" build && ninja -C build install"
    ],
    "creates": "~/.local/bin/picom",
    "profiles": ["workstation"]
  }
  ```

  - Default `dest` is `~/.local/src/picom` — the existing clone on this
    machine, so the playbook reuses it instead of re-cloning.
  - `rm -rf build` first: the existing build dir on this machine was
    configured with the `/usr/local` prefix, and `meson setup` refuses an
    already-configured dir. A wipe is idempotent — the step only runs when
    `~/.local/bin/picom` is missing.
  - `creates: ~/.local/bin/picom` doubles as the clone marker and the build
    step's `creates` guard (build skipped once installed).
  - Single build step: configure with per-user prefix, build, install —
    all guarded by the binary's existence.
- **Acceptance:**
  - [x] `ansible-playbook --check --diff --skip-tags packages
        ansible/playbook.yml` passes.
  - [x] After a real run: `command -v picom` resolves to
        `~/.local/bin/picom`, which shadows `/usr/local/bin/picom`.
  - [x] `~/.local/bin/picom --version` reports a v12 build
        (`yshui/picom revision 69539ed` — the same revision as the prior
        `/usr/local` build, since `update: false` leaves the existing
        `v12-131` clone untouched; verified the git module's no-checkout
        behavior on a scratch clone).
  - [x] Re-run is idempotent: build step skipped via `creates`
        (`~/.local/bin/picom` exists).
