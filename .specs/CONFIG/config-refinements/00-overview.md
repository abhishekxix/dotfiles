# Cross-Config Refinements

| Field | Value |
|---|---|
| Status | Approved |
| Component | CONFIG |
| Created | 2026-09-09 |

## Goal

Close the remaining findings from the 2026-09-09 five-agent audit that are
still open after the NVIM (3 specs) and QTILE (2 specs) slices — covering
tmux, Alacritty, Starship, shell startup, gitconfig, and desktop extras
(dunst, rofi, picom). One centralized spec because every item is a
few-line, cross-cutting config tweak that fits nowhere else.

## Context & Research

The audit produced ~124 findings across nvim (28), qtile (32), tmux +
alacritty + starship (19), shell + git (28), and desktop extras (17). The
NVIM and QTILE slices landed (see Dedup below); this spec takes what's left
and still true, verified against the tree on 2026-09-09 (file/line refs are
current-state).

Key facts:

1. **tmux `screen-256color`** (`tmux.conf:2`) kills undercurl/italics; the
   fix is `tmux-256color` + a `Tc` override. No OSC-52 passthrough
   (`set-clipboard`) means yanks never leave tmux/SSH sessions. `mode-keys
   vi` is set but there are **no `v`/`y` copy-mode bindings**, so vi mode is
   half-wired.
2. **Starship has no `format` line** (`starship.toml` starts at
   `add_newline`, then ~40 symbol-only module stanzas). Without `format`,
   every default module's detection runs per prompt; an explicit format is an
   allowlist. `git_metrics` and `sudo` are explicitly *enabled* (slow/noisy);
   `status`/`jobs`/`cmd_duration` signal is absent.
3. **Two node managers at once**: `.zshrc:58` eagerly evals `fnm env` every
   shell; `.bashrc:16` eagerly sources system `nvm` (0.3–0.8s). Bare
   `compinit` (`.zshrc:29-30`) costs ~100–300ms per shell with no dump cache.
   `credential.helper = store` (`.gitconfig:39`) stacks under the gh helpers
   (lines 47–50) — verify `~/.git-credentials` is empty/absent before
   removing.
4. **dunst `follow = none` + `monitor = 0`** (`dunstrc:7,20`) pins every
   notification to monitor 0 on a 2-screen setup; no per-urgency `timeout`
   lines plus `notification_limit = 20` lets spam linger; `font = Ubuntu 10`
   lacks the Nerd glyphs the format strings assume. **picom's third rule**
   forces `corner-radius = 0` for `class_g = 'Dunst'` while dunstrc sets
   `corner_radius = 16` — the compositor undoes the rounding.
5. **rofi config is one line** (`config.rasi`: theme import only) — all
   defaults: no `modes`, no listview tuning, ungrabbable scrollbar.
6. **Qtile bar still ticks every second**: `Clock(format="...%H:%M:%S")`
   (`screens.py:92`) redraws the bar 60×/min for a seconds display nobody
   reads. `StatusNotifier` + `Systray` both render (lines 100–101). 9 layouts
   (`layouts.py`) cycle via Tab with Floating trapping focus. No
   volume/brightness/media keys (`keys.py` ends at line 111) despite
   pavucontrol/backlight tooling installed.
7. **nvim `langs.lua`**: `html`, `markdown`, `php` specs have no `formatters`
   even though `prettier` is already in the toolchain and handles all three.

## Dedup — already implemented or deliberately decided (NOT in this spec)

- **NVIM done**: clangd caps merge, cmp `select=false` + Tab fallback,
  conform scope + format-on-save toggle, telescope/todo keys-lazy-load, mini
  VeryLazy, neo-tree follow, treesitter parser guard, lint on TextChanged,
  explicit LSP enable, yaml spec, autotag/sleuth lazy-load.
- **NVIM deliberately reverted/skipped per user** (do not relitigate):
  `keymaps.lua` additions (save/buffer-delete/splits/diagnostic jumps),
  buffer source, virtual-text-off, neo-tree hide-filters, which-key `f`
  group, opencode (plugin removed), copilot stays eager, mini.surround maps.
- **QTILE done**: non-blocking autostart, keyring `&`, guarded xrandr/tray
  daemons, idempotent echo-cancel, Net combined + backlight autodetect,
  None-safe copyq hook, full dynamic-monitor hotplug (xrandr helper,
  screen_change hook, geometry placement, per-output wallpaper).
- **HOME done**: `~/.path` extraction (4 steps).
- **Low-payoff audit noise** (drop, not worth a commit each): icon PNG
  archaeology, TaskList width, temp/battery/memory widget tuning, cursor-size
  mismatches, sparse Xresources, lxsession leftovers, flameshot defaults,
  `help()` shadow, `lg` nesting, gtkrc/Xresources trivia, rofi launcher flag
  disagreement, debian-vs-arch logo choice, group label casing, nvim
  sleuth/tabstop comment, macro indicator, scrolloff/foldlevel generosity.

## Non-goals

- Do **not** touch `lua/keymaps.lua`, copilot eagerness, virtual text, cmp
  sources, mini.surround maps, or anything else reverted in `c5c5426` /
  `76b0c35` (user decisions stand).
- Do **not** change Qtile group names/bindings, bar layout order, palette,
  mouse drag-hack, or monitor logic (dynamic-monitors spec owns that).
- Do **not** add new plugins, daemons, or dependencies (no resurrect/continuum
  — tpm plugin adds boot cost for a solo laptop; no brightnessctl, no new
  widgets; use `xrandr`/`pactl` keys only).
- Do **not** switch node managers wholesale — one manager in both shells,
  minimal diff.
- Do **not** restyle the prompt beyond the allowlist (no new Starship
  segments except the missing status/jobs/cmd_duration signal).

## Steps

Each step maps to exactly one commit, named `<COMPONENT>(<NN>): <summary>`.

### 01 — tmux truecolor + clipboard + vi-copy + sane defaults

- **Files:** `.config/tmux/tmux.conf` (EDIT)
- **Changes:** `default-terminal` → `tmux-256color` (keep/extend `Tc`
  override); enable OSC-52 passthrough (`set-clipboard on`) so yanks escape
  tmux incl. SSH; add copy-mode-vi `v` (begin-selection) / `y` (copy +
  exit); add `history-limit`, `renumber-windows`, `focus-events`; add
  prefix-`r` config reload and repeatable resize binds (`H/J/K/L`).
- **Test:** `tmux kill-server; tmux new -d 'nvim --headless'` then check
  `:checkhealth` undercurl/italics ok; yank in copy-mode, paste outside tmux
- **Acceptance:**
  - [ ] italics/undercurl render; `y` in copy-mode lands in system clipboard
  - [ ] windows renumber on close; reload + resize binds work

### 02 — Alacritty env + window polish

- **Files:** `.config/alacritty/alacritty.toml` (EDIT)
- **Changes:** drop `TERM = "xterm-256color"` override (let it default to
  `alacritty`, matching tmux's `Tc` handling — verify no breakage first);
  add `[scrolling]` history + `[selection]`/clipboard save; drop the dangling
  empty `[terminal]` section; make the theme import absolute
  (`~/.config/alacritty/...`) so launch cwd never matters; bump default
  window from 80×25 to something usable on a 1440p/1080p setup.
- **Test:** launch alacritty from `/`, confirm theme loads; `echo $TERM`;
  scrollback + clipboard copy works
- **Acceptance:**
  - [ ] correct theme regardless of cwd; no empty section; scrollback present

### 03 — Starship format allowlist + prompt signal

- **Files:** `.config/starship.toml` (EDIT)
- **Changes:** add an explicit minimal `format` string (only modules actually
  read: directory, git_branch/commit/status, language(s) in use, jobs,
  cmd_duration, status, line break, char); disable `git_metrics` + `sudo`
  (slow/noisy); keep existing symbols untouched.
- **Test:** `starship timings` before/after in a big repo; failing command
  shows nonzero status, long command shows duration, background job shows
  jobs indicator
- **Acceptance:**
  - [ ] prompt render measurably faster in large repos; exit-code/duration/jobs visible

### 04 — Shell startup: compinit cache, one node manager, fzf/bat hardening

- **Files:** `home/.zshrc` (EDIT), `home/.bashrc` (EDIT)
- **Changes:** `compinit -C -d <dumpfile>` (skip rehash check, cached dump);
  lazy-load fnm (`--use-on-cd` only on first `node`/`fnm` use, or defer to
  first prompt) instead of eager eval; drop the eager system-`nvm` source in
  `.bashrc` (fnm owns node; keep bash functional without it); source fzf once
  (prefer `~/.fzf.zsh` *or* system examples when the other is absent, guarded
  by `command -v fzf`); `batcat` → `bat` with fallback so preview works
  off-Debian; `EDITOR=nvim` to match git; scope `NODE_ENV` out of the global
  env (set per-project, not exported for every GUI app).
- **Test:** `time zsh -ic true` before/after; `bash -ic true`; open shell on a
  machine without fzf/bat/fnm — no errors, shell usable
- **Acceptance:**
  - [ ] interactive shell start measurably faster; missing tools degrade silently
  - [ ] `node`/`npm` still work in both shells via the single manager

### 05 — gitconfig hygiene + shell history/aliases

- **Files:** `home/.gitconfig` (EDIT), `home/.zshrc` (EDIT), `home/.bashrc` (EDIT)
- **Changes:** drop `credential.helper = store` **only if**
  `~/.git-credentials` is empty/absent (gh helper covers github/gist);
  add `fetch.prune`, `push.autoSetupRemote`, `pull.rebase`,
  `core.excludesFile`-neutral diff niceties (`column.ui=auto`,
  `diff.colorMoved`); zsh history: add `share/append/inc_append/history_verify`
  (keep existing dedup opts); remove duplicated `autocd`/`auto_cd`;
  converge the ls/cp/mv/rm alias sets between bash/zsh (keep or drop `-i`
  consistently — confirm with user at review); add `bash-completion` source
  guarded by file-exists.
- **Test:** `git config --list --show-origin`; `gh auth git-credential`
  still fills github creds; new shell history shared across sessions
- **Acceptance:**
  - [ ] no plaintext credential path when gh covers it; prune/autosetup/rebase active
  - [ ] history shared + verified; no duplicated shell options

### 06 — Qtile bar + keys polish (slice-4 look-and-feel)

- **Files:** `.config/qtile/config_parts/screens.py` (EDIT), `.config/qtile/config_parts/keys.py` (EDIT), `.config/qtile/config_parts/layouts.py` (EDIT)
- **Changes:** Clock → minute precision (`%H:%M`, `update_interval=60`);
  keep `StatusNotifier`, drop `Systray` (or vice versa — whichever renders
  this host's tray completely, verify via tray icon census); trim layout
  list to the 3–4 actually used (keep Columns/Max + one tiling + Floating);
  add float rules for flameshot/nm-connection-editor/blueman; add
  volume/brightness keys (`pactl`, sysfs backlight — no new deps) +
  next-screen / window-to-screen / unminimize keys.
- **Test:** `qtile check -c config.py`; reload, confirm bar ticks once/min,
  single tray, Tab never lands on a focus-trap; press media keys
- **Acceptance:**
  - [ ] bar redraws 1×/min; one tray backend; layouts cycle cleanly; media + screen keys work

### 07 — nvim leftovers: formatters + autocmd polish

- **Files:** `.config/nvim/lua/langs.lua` (EDIT), `.config/nvim/lua/autocommands.lua` (EDIT)
- **Changes:** add `prettier` to the `html`, `markdown`, `php` specs
  (formatters only — no server/parser changes); add the deferred small
  autocmds: `VimResized` → `wincmd =`, `FocusGained`/`BufEnter` checktime
  reload, last-place jump on `BufReadPost`, `q`-to-close for help/quickfix
  (all in `autocommands.lua`, no keymap/plugin changes).
- **Test:** `:ConformInfo` on html/md/php shows prettier; resize splits +
  reopen file at last line + `q` closes help
- **Acceptance:**
  - [ ] format works in html/md/php; resize/checktime/last-place/q-close all behave

### 08 — dunst follow + timeouts, rofi modes, picom rounding/blur

- **Files:** `.config/dunst/dunstrc` (EDIT), `.config/rofi/config.rasi` (EDIT), `.config/picom.conf` (EDIT)
- **Changes:** dunst `follow = keyboard` (focused monitor), per-urgency
  `timeout` (low ~3s / normal ~8s / critical sticky) + lower
  `notification_limit` to ~5, font to a Nerd-patched family matching the bar;
  rofi: set `modes` (drun,run,window,ssh), listview lines/columns, sidebar
  mode to kill the jitter; picom: remove `Dunst` from the
  `corner-radius = 0` rule (let dunstrc's 16px rounding survive), drop
  `dual_kawase` → cheaper `box`/`gaussian` blur (iGPU cost) or weaken
  strength.
- **Test:** `dunstify` low/normal/critical on each monitor — placement +
  timeout correct; `rofi -show drun` stable with visible scrollbar;
  `picom --diagnostics`; notifications keep rounded corners
- **Acceptance:**
  - [ ] notifications follow focus with sane timeouts; rofi stable; dunst corners round

## Risks & Rollback

- **tmux-256color (step 01):** needs the terminfo entry on every host/SSH
  target; if missing, tmux fails to start. Mitigation: verify `infocmp
  tmux-256color` in the installer context; rollback restores `screen-256color`.
- **Alacritty TERM (step 02):** unsetting changes terminfo for all children;
  some remote hosts lack the `alacritty` entry (worse than xterm). If SSH
  breakage appears, keep the override and drop that hunk.
- **compinit -C (step 04):** skips the dump-security/compaudit check; on a
  single-user laptop this is standard practice. Rollback: plain `compinit`.
- **Dropping nvm (step 04):** any shell script sourcing system nvm breaks;
  grep for `init-nvm` users first. Rollback: restore the line.
- **Credential store removal (step 05):** gated on empty/absent
  `~/.git-credentials` — if non-empty, keep `store` and close that hunk.
- **Tray backend choice (step 06):** dropping the wrong one loses tray icons;
  census before/after decides. One-commit revert restores both.
- **picom blur downgrade (step 08):** visual change; if the look regresses,
  keep kawase and only fix the Dunst rounding rule.

Each step is its own commit, so `git revert` or `git bisect` localizes any
regression.
