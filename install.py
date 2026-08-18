#!/usr/bin/env python3

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

from src.dotfiles_installer.cli import main


if __name__ == "__main__":
    raise SystemExit(main(PROJECT_ROOT))