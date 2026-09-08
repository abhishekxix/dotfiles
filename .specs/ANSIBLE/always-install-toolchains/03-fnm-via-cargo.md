# 03 — fnm installs via cargo

## Files

- `ansible/tasks/toolchain.yml` (EDIT)

## Changes

Switch the fnm install method from the curl script to cargo, aligning the
probes with the new artifact location:

- **"Install fnm (node provider)"** (`:44-56`): replace the
  `curl … https://fnm.vercel.app/install | bash -s -- --skip-shell` pipe
  with `cargo install fnm --locked` (shell task, `executable: /bin/bash`,
  `set -o pipefail`). `creates:` moves to
  `~/.cargo/bin/fnm`. The task `environment` PATH already prepends
  `~/.cargo/bin`, which finds a rustup-installed cargo and an apt cargo
  alike. `--skip-shell` disappears — cargo install touches no shell config
  (`home/.zshrc` already runs `eval "$(fnm env --use-on-cd --shell zsh)"`).
- **"Check for fnm"** (`:24-30`): stat path `~/.local/share/fnm/fnm` →
  `~/.cargo/bin/fnm`, so the probe and `creates:` agree (AI-10 lesson).
- **AI-30 comment** (`:32-33`): rewritten — cargo is now the install
  source; the PATH probe (`command -v fnm`) remains to skip a foreign fnm
  (apt, manually installed) instead of reinstalling over it.
- **"Install Node LTS via fnm"** (`:58-69`): drop the leading
  `~/.local/share/fnm` from the task PATH. That dir is data-only once fnm
  ships via cargo (`~/.cargo/bin/fnm` is the binary); a legacy
  curl-installed `~/.local/share/fnm/fnm` left by an old playbook run can
  then no longer shadow the cargo binary. The comment (09-18) is updated to
  match. Everything else — `eval "$(fnm env --shell bash)"`,
  `fnm install --lts`, `aliases/default` creates-marker, and the data dir
  itself (FNM_DIR default, stable per `09-fix-round.md` item 9) — is
  unchanged.

## Acceptance

- [ ] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
- [ ] On this host: "Install fnm" skips via the stat (`~/.cargo/bin/fnm`
  exists) and `fnm --version` works afterwards.
- [ ] "Install Node LTS via fnm" skips via the `aliases/default`
  creates-marker — behavior unchanged.
