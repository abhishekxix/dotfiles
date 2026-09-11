# Config QOL Updates (round 2)

| Field | Value |
|---|---|
| Status | Planning |
| Component | CONFIG |

> Status lifecycle: `Planning` → `Approved` (frozen; edits need re-approval) →
> `In progress` → `Done`.

## Goal

Small, current-state quality-of-life improvements across shell, git, tmux,
nvim, qtile, and desktop helpers — each a few lines, none relitigating the
user reverts from `config-refinements` (see Non-goals).

## Context & Research

`config-refinements` (Approved, 8 steps) landed with user trims on top
(`df18d09`, `65db911`, `40fc4b9`, `09d96c1`, `015aa49`, `2a19396`,
`43f5649`). Verified against the tree 2026-09-12, the remaining gaps are:

1. **Shell plugins unguarded** (`.zshrc:35-36`): two `source` lines for
   zsh-syntax-highlighting/autosuggestions with no existence check — a fresh
   clone without those plugins prints errors on every prompt. fzf got the
   guarded treatment in step 04; these two didn't.
2. **bash history cross-session**: `.bashrc:18` has `histappend` but bash
   only writes history on shell exit — parallel terminals clobber each
   other. `PROMPT_COMMAND="history -a; history -n"` gives zsh-like
   `share_history` feel in one line.
3. **git QoL**: `help.autocorrect` (fat-finger `git chekcout` DTRT),
   `rerere` (reuse recorded conflict resolutions — pairs with the
   `diff3`/`mergetool` setup already here),
   and a `cleanup`/`gone-branch-prune` alias. `credential.helper = store`
   stays (user kept it — do not touch).
4. **tmux ergonomics**: no `detach-on-destroy` (closing the last pane kills
   the client instead of switching sessions), no `display-time` bump
   (messages vanish in 750ms), no `set-titles` (terminal tab shows tmux,
   not the running command). All one-liners.
5. **nvim confirm**: `opts.lua` lacks `confirm = true` — `:q` on a dirty
   buffer errors instead of offering to save. One line; no keymap/plugin
   changes.
6. **Desktop papercuts**: `screens.sh` is superseded by `monitors.py` but
   kept as a documented fallback — add a header comment saying so;
   `flameshot.ini` lacks `startupLaunch=true` despite autostart launching
   it (double-tray risk); `dunst` idle-threshold commented out (step-08
   timeouts get bypassed when idle).

## Non-goals

- Do **not** relitigate `config-refinements` user reverts: alacritty TERM/
  scrollback/clipboard/window-size/theme-path, starship format allowlist,
  eager fnm, `EDITOR=vim`, `credential.helper = store`, prune/autosetup/
  rebase, dunst follow/font, picom blur/Dunst rounding, qtile flameshot
  float rule, brightness-in-qtile, prettier for md/php, nvim
  resize/checktime/q-close autocmds, `lua/keymaps.lua` of any kind.
- Do **not** add new plugins, daemons, or dependencies.
- Do **not** change Qtile group names/bindings, bar order, palette, or
  monitor logic.

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

### 01 — Guard zsh plugin sources

- **Files:** `home/.zshrc` (EDIT)
- **Changes:** guard the two plugin `source` lines with file-exists checks
  (same pattern step 04 used for fzf).
- **Test:** `zsh -ic true` on a machine without the plugins — no errors.
- **Acceptance:**
  - [ ] shell starts clean with plugins absent, loads them when present

### 02 — Bash shared history + git QoL aliases

- **Files:** `home/.bashrc` (EDIT), `home/.gitconfig` (EDIT)
- **Changes:** `PROMPT_COMMAND="history -a; history -n"` for cross-session
  bash history; git: `help.autocorrect = 10`, `rerere.enabled = true`,
  a branch-cleanup alias.
- **Test:** open two bash shells, run a command in one, `history` in the
  other shows it; `git config --list` shows new keys.
- **Acceptance:**
  - [ ] history shared across live bash sessions; new git keys active

### 03 — tmux session/title/message defaults

- **Files:** `.config/tmux/tmux.conf` (EDIT)
- **Changes:** `detach-on-destroy off` (fall through to another session),
  `set-titles on` + `set-titles-string`, `display-time 2000`.
- **Test:** kill last pane of a session with 2 sessions — client switches,
  doesn't exit; terminal title tracks command; messages readable.
- **Acceptance:**
  - [ ] session switch on destroy; titles track; messages persist 2s

### 04 — nvim confirm on unsaved quit

- **Files:** `.config/nvim/lua/opts.lua` (EDIT)
- **Changes:** `vim.opt.confirm = true` — `:q`/`:bd` on dirty buffers
  prompts instead of erroring.
- **Test:** edit a buffer, `:q` — confirmation dialog appears.
- **Acceptance:**
  - [ ] dirty-buffer quit prompts to save

### 05 — Desktop leftovers: screens.sh, flameshot, dunst idle

- **Files:** `.bin/screens.sh` (EDIT — header comment only, script stays),
  `.config/flameshot/flameshot.ini` (EDIT),
  `.config/dunst/dunstrc` (EDIT)
- **Changes:** header comment on `screens.sh` noting `monitors.py` owns
  layout and this is a manual fallback; `startupLaunch=true` in flameshot
  (autostart owns launch, no double tray); `idle_threshold = 120`
  uncommented in dunst.
- **Test:** reboot — one flameshot tray; idle notifications held per
  threshold.
- **Acceptance:**
  - [ ] screens.sh documented as fallback; single flameshot tray; idle hold works

## Risks & Rollback

- **`PROMPT_COMMAND` (step 02):** overwrites any existing value — append
  (`PROMPT_COMMAND="history -a; history -n${PROMPT_COMMAND:+;$PROMPT_COMMAND}"`)
  if one exists at review time.
- **`rerere` (step 02):** records resolutions in `.git/rr-cache`; harmless,
  disable with `rerere.enabled = false`.

Each step is its own commit, so `git revert` or `git bisect` localizes any
regression.
