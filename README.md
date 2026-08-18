# dotfiles

## Install

Clone the repository, preview the changes, and install the configuration:

```bash
git clone https://github.com/abhishekxix/dotfiles.git ~/dotfiles
cd ~/dotfiles
./install.py --dry-run
./install.py
```

The installer creates symlinks for home files and applications under `.config`.
Existing files are moved into a unique run directory under
`~/.dotfiles-backup` before they are replaced. It can be
run repeatedly or concurrently without backup collisions. The installer
presents a terminal checkbox list with everything selected by default. Use Up
and Down to move, Space to toggle individual entries, and Enter to confirm.
The parent checkboxes toggle their children and show `[-]` when partially
selected. Use `--all` to skip the checklist and install every entry.

For a non-interactive installation, pass names with `--home` and `--config`.
An omitted home or `.config` group defaults to all entries:

```bash
./install.py --home .bashrc,.zshrc --config nvim,tmux,starship.toml
```

Use `none` to skip a group, such as `--home none --config nvim`. The names
`all` and `none` are selection keywords; prefix either with `./` to select a
literal entry with that name.

Optional one-off scripts live in `.bin/` and are not installed automatically.

The installer requires Python 3.10 or newer and uses only the standard library.
Its implementation lives under `src/dotfiles_installer/`; `install.py` is the
executable entry point.

The Xorg configuration is machine-specific and is skipped by default. Install
it explicitly when needed:

```bash
./install.py --include-xorg
```

If `/etc/X11/xorg.conf.d/20-nvidia.conf` already differs from the repository
copy, the installer refuses to replace it. `DOTFILES_XORG_DIR` can redirect the
destination for testing.

For testing or installation into another home directory, set `DOTFILES_HOME`.
Set `DOTFILES_BACKUP_DIR` to override the parent directory where unique backup
run directories are allocated.


TODO: Move configuration to ansible or similar tools.