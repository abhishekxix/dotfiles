# 02 — Swap neovim to the GitHub tarball

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** Replace the `neovim` apt entry with an `archive` entry pinned
  to v0.12.5, replicating the install already present on this machine (tarball
  extracted at `~/.local/src/nvim`, `~/.local/bin/nvim` symlink):

  ```json
  "neovim": {
    "source": "archive",
    "url": "https://github.com/neovim/neovim/releases/download/v0.12.5/nvim-linux-x86_64.tar.gz",
    "url_arm64": "https://github.com/neovim/neovim/releases/download/v0.12.5/nvim-linux-arm64.tar.gz",
    "strip": 1,
    "dest": "~/.local/src/nvim",
    "creates": "~/.local/src/nvim/bin/nvim",
    "link": "bin/nvim",
    "profiles": ["workstation", "server"]
  }
  ```

  The `url_arm64` override keeps the arch-validation assert
  (`playbook.yml:443`) green on ARM. `~/.local/src/` matches the default
  install root of `git`-source entries (`playbook.yml:490`). The `creates`
  guard makes a re-run on a machine that already has v0.12.5 extracted a
  no-op.
- **Acceptance:**
  - [ ] `ansible-playbook --check --diff --skip-tags packages
        ansible/playbook.yml` passes (schema + validation tasks green).
  - [ ] After a real run: `nvim --version` reports `v0.12.5` and resolves to
        `~/.local/bin/nvim` (`command -v nvim`).
  - [ ] `~/.local/bin/nvim` is a symlink to `~/.local/src/nvim/bin/nvim`.
