import argparse
import os
from pathlib import Path
import subprocess
import sys

from .actions import InstallerActions
from .errors import InstallError
from .paths import validate_link_paths
from .selection import choose_sources


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="install.py",
        description="Install this repository by creating symlinks in the home directory.",
        epilog=(
            "Environment:\n"
            "  DOTFILES_HOME        Override the target home directory\n"
            "  DOTFILES_BACKUP_DIR  Override the parent directory for unique backups\n"
            "  DOTFILES_XORG_DIR    Override the Xorg destination directory"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="show changes without modifying files"
    )
    parser.add_argument(
        "--all", action="store_true", help="install every home and .config entry"
    )
    parser.add_argument("--home", metavar="LIST", help="install comma-separated home file names")
    parser.add_argument(
        "-c", "--config", metavar="LIST", help="install comma-separated .config names"
    )
    parser.add_argument(
        "--include-xorg",
        action="store_true",
        help="install xorg.conf in /etc/X11/xorg.conf.d (uses sudo)",
    )
    return parser


def _discover_home_files(home_dir: Path) -> list[Path]:
    return sorted(
        entry
        for entry in home_dir.iterdir()
        if entry.name.startswith(".") and entry.is_file() and not entry.is_symlink()
    )


def _discover_config_sources(config_dir: Path) -> list[Path]:
    return sorted(
        entry
        for entry in config_dir.iterdir()
        if not entry.name.lower().startswith(("readme", "license"))
        and entry.name != ".gitkeep"
    )


def run(arguments: list[str], repo_dir: Path) -> int:
    parser = build_parser()
    options = parser.parse_args(arguments)

    if options.all and (options.home is not None or options.config is not None):
        parser.error("--all cannot be used with --home or --config")
    for option, value in (("--home", options.home), ("--config", options.config)):
        if value is not None and not value.strip():
            parser.error(f"{option} requires a non-empty selection")

    home_dir = repo_dir / "home"
    config_dir = repo_dir / ".config"
    if not home_dir.is_dir():
        raise InstallError(f"Missing dotfiles source directory: {home_dir}", 2)
    if not config_dir.is_dir():
        raise InstallError(f"Missing dotfiles source directory: {config_dir}", 2)

    target_home = Path(os.environ.get("DOTFILES_HOME", Path.home()))
    backup_parent = Path(
        os.environ.get("DOTFILES_BACKUP_DIR", target_home / ".dotfiles-backup")
    )
    xorg_dir = Path(
        os.environ.get("DOTFILES_XORG_DIR", "/etc/X11/xorg.conf.d")
    )
    home_files = _discover_home_files(home_dir)
    config_sources = _discover_config_sources(config_dir)
    selected_home, selected_config = choose_sources(
        home_files,
        config_sources,
        options.all,
        options.home,
        options.config,
    )

    managed_paths = [
        *((source, target_home / source.name) for source in selected_home),
        *((source, target_home / ".config" / source.name) for source in selected_config),
    ]
    if options.include_xorg:
        managed_paths.append((repo_dir / "xorg.conf", xorg_dir / "20-nvidia.conf"))
    validate_link_paths(repo_dir, backup_parent, managed_paths)

    actions = InstallerActions(
        repo_dir=repo_dir,
        target_home=target_home,
        backup_parent=backup_parent,
        xorg_dir=xorg_dir,
        dry_run=options.dry_run,
    )
    if options.include_xorg:
        actions.install_xorg()

    operation = "Previewing" if options.dry_run else "Installing"
    actions.log(f"{operation} dotfiles from {repo_dir} into {target_home}")
    for source in selected_home:
        actions.link_item(source, target_home / source.name)
    for source in selected_config:
        actions.link_item(source, target_home / ".config" / source.name)

    if options.dry_run:
        actions.log("Dry run complete. No changes were made.")
    else:
        actions.log("Dotfiles installed. Restart your shell or log in again to load them.")
    return 0


def main(repo_dir: Path | None = None) -> int:
    try:
        return run(sys.argv[1:], repo_dir or Path(__file__).resolve().parents[2])
    except InstallError as error:
        print(error, file=sys.stderr)
        return error.exit_code
    except subprocess.CalledProcessError as error:
        return error.returncode or 1
    except OSError as error:
        print(f"Installation failed: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInstallation cancelled.", file=sys.stderr)
        return 130