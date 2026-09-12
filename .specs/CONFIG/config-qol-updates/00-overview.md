# Config QOL Updates (round 2)

| Field | Value |
|---|---|
| Status | In progress |
| Component | CONFIG |
| Created | 2026-09-12 |

> Status lifecycle: `Planning` -> `Approved` -> `In progress` -> `Done`.
> After approval, body edits need re-approval; lifecycle metadata and
> status/acceptance checkboxes remain editable.

## Goal

Remove the highest-value reliability and daily-use friction across the shell,
Git, tmux, Neovim, Qtile, desktop helpers, and provisioning pipeline. Work is
ordered by quality of life, then productivity, aesthetics, and optional fun;
prior user reverts remain authoritative.

## Context & Research

`config-refinements` landed with user trims on top (`df18d09`, `65db911`,
`40fc4b9`, `09d96c1`, `015aa49`, `2a19396`, `43f5649`). A second full-tree
review on 2026-09-12 compared the current files with those decisions and ran
the available read-only checks.

Checks that passed:

- `.bin/validate-manifest.py` on the current manifests.
- Python compilation of the installer, validator, and Qtile configuration.
- Bash and Zsh syntax checks.
- The canned Qtile dynamic-monitor self-check.
- The worktree remained clean after all probes.

Environment gaps observed during the review:

- The active Neovim was 0.12.2 while the manifest declared 0.12.5.
- A headless Neovim start retried Black installation and Black failed.
- Treesitter attempted every configured parser, but compilation failed because
  `tree-sitter` was absent from `PATH` on the review host.
- `pre-commit`, `shellcheck`, and `ansible-playbook` were unavailable on the
  review host. ShellCheck is provisioned for Debian; pre-commit remains a
  documented manual development dependency.

### Reconciliation Decisions

| Proposal | Decision |
|---|---|
| Guard Zsh plugin sources | Keep; also load syntax highlighting last and guard Starship. |
| Share Bash history between live shells | Keep; preserve existing prompt hooks. |
| Git `help.autocorrect` | Omit by user choice; automatic typo execution is not worth the risk. |
| Git `rerere` | Keep; it reduces repeated conflict-resolution work. |
| Git branch cleanup | Add a read-only gone-branch report; deletion remains explicit. |
| Preserve `credential.helper = store` | Keep by prior user decision; document its risk but do not change it here. |
| tmux session/message/title defaults | Keep; Alacritty continues to create separate sessions by user choice. |
| Neovim `confirm` | Keep; dirty-buffer exits should offer a save choice. |
| Mark `screens.sh` as superseded | Keep as an emergency hardware-specific fallback. |
| Set Flameshot `startupLaunch=true` | Reject; Qtile autostart remains the single owner. |
| Dunst idle threshold | Keep; notifications should remain available after idle time. |
| Automatic screen lock/DPMS | Omit by user choice; harden only the manual lock/suspend path. |
| Desktop visual baseline | Standardize GTK/Xcursor on Yaru Purple Dark, Ubuntu, Papirus Dark, and Breeze. |
| New CLI tools | Add `zoxide` and `direnv` for navigation and project-local environments. |

### Priority Findings

1. Shell startup assumes complete provisioning, applies file previews to every
   fzf input, loads syntax highlighting before later widgets, and combines
   overlapping history modes.
2. Qtile launches a disabled Rofi mode, Dunst calls uninstalled dmenu,
   Xbindkeys prioritizes hardware-specific keycodes, and brightness tooling is
   undeclared.
3. Session variables are exported too late, two components can own the SSH
   agent, and explicit launches can duplicate XDG autostart applications.
4. Mason initializes twice, tool installation retries noisily, failed
   Treesitter startup still enables folds, LSP highlight handlers have an
   unsafe lifecycle, and LSP attach eagerly loads Telescope.
5. Wallpaper state breaks on whitespace, Flameshot hardcodes `/home/abhi`, and
   `xrandr` is used without explicitly declaring `x11-xserver-utils`.
6. Stable markers prevent declared archive/Git upgrades, scripts always report
   changed, and package integrity/retry/audit behavior is incomplete.
7. Runtime validation is weaker than the retained schemas, repository metadata
   is not semantically validated, and CI lacks ShellCheck, Ansible syntax, and
   Debian integration coverage.
8. LXSession, GTK2, and Xresources disagree on visual defaults; Qtile relies on
   implicit Nerd Font fallback; obsolete tmux/Picom options remain.

## Non-goals

- Do not relitigate prior user reverts: Alacritty TERM/scrollback/clipboard/
  window size/theme path, Starship format allowlist, eager fnm, `EDITOR=vim`,
  Git prune/auto-setup/rebase, Dunst follow/font, Picom blur/Dunst rounding,
  Qtile group names/bar order/palette, Prettier for Markdown/PHP, or any global
  Neovim keymap/buffer-source/virtual-text/Neo-tree-filter change.
- Do not remove or replace `credential.helper = store` in this spec.
- Do not enable automatic locking or DPMS.
- Do not change Alacritty from separate tmux sessions to a shared named session.
- Do not add a Neovim test runner, debugger, session manager, dashboard, theme
  picker, or other plugin until the existing toolchain is healthy.
- Do not generalize Qtile beyond one internal plus one external display without
  target hardware for acceptance testing.
- Do not widen the mutating installer beyond Debian. The doctor may inspect
  another platform but must not alter it.
- Do not install or modernize the dormant top-level `xorg.conf`.
- Do not update the vendored Catppuccin tmux plugin in a behavior-change commit.

## Steps

Each step has a numbered file and maps to one commit named
`CONFIG(<NN>): <summary>`. Implementation begins only after this revised spec
is explicitly approved.

- [x] [01 - Harden shell startup and history](01-shell-startup-history.md)
- [x] [02 - Scope fzf and add zoxide/direnv](02-fzf-zoxide-direnv.md)
- [x] [03 - Improve Git conflict/tool ergonomics](03-git-conflict-tools.md)
- [x] [04 - Refine tmux session ergonomics](04-tmux-session-ergonomics.md)
- [x] [05 - Add safe Neovim exit confirmation](05-nvim-confirm.md)
- [x] [06 - Make Neovim tool installation diagnosable](06-nvim-tool-install.md)
- [x] [07 - Correct Neovim LSP lifecycle](07-nvim-lsp-lifecycle.md)
- [x] [08 - Reconcile Rofi and Dunst](08-rofi-dunst.md)
- [x] [09 - Make hardware keys reliable](09-hardware-keys.md)
- [x] [10 - Establish one session/autostart owner](10-session-autostart.md)
- [x] [11 - Make wallpaper/screenshots portable](11-wallpaper-screenshots.md)
- [x] [12 - Unify desktop visual defaults](12-desktop-visuals.md)
- [x] [13 - Add non-mutating environment diagnostics](13-environment-doctor.md)
- [x] [14 - Strengthen installer preflight/link safety](14-installer-preflight-links.md)
- [x] [15 - Make manifest validation strict](15-manifest-validation.md)
- [x] [16 - Define package lifecycle/integrity](16-package-lifecycle.md)
- [x] [17 - Expand CI and operator documentation](17-ci-docs.md)

## Deferred Follow-ups

- Update vendored Catppuccin tmux separately after reviewing its migration and
  status-line reset behavior.
- Evaluate Dunst per-monitor DPI and separate Qtile bar sizes on real hardware.
- Extend Qtile beyond one external display only with target topology available.
- Replace `xorg.conf` with a minimal snippet only if the manual file is needed.
- Revisit Git credential storage only with explicit approval and a migration
  plan for non-GitHub credentials.
- Add broader Neovim test/debug/session workflows only for a repeated need.
- Consider an fzf tmux popup/project sessionizer after core behavior is stable.
- Consider a curated random XScreenSaver mode later; blank/manual lock remains.
- Resolve the undeclared/fragile `xbacklight` dependency only after explicit
  approval to revisit the prior no-new-brightness-dependency decision.
- Reconcile historical spec statuses through separately approved follow-up
  records rather than rewriting frozen specifications.

## Risks & Rollback

- Shell history changes can duplicate entries or interfere with prompt hooks;
  concurrent-shell tests gate the change.
- `direnv` changes process environments by directory; explicit review and
  `direnv allow` remain mandatory.
- Git `rerere` can replay obsolete resolutions; every replay remains reviewable
  and repository-local recorded state can be cleared.
- Parser aliases and clangd capabilities are version-sensitive; health and
  representative-language checks gate those commits.
- Xbindkeys, lock/suspend, keyring, notification, and toolkit behavior require a
  real X11 login; static validation is insufficient.
- Installer lifecycle/integrity work occurs only after fixture and disposable
  Debian coverage exists.
- Every step is isolated in one commit, so `git revert` or `git bisect`
  localizes rollback. The spec remains `Planning` until explicitly approved.
