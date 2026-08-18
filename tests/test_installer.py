from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import pty
import select
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from dotfiles_installer.cli import run
from dotfiles_installer.errors import InstallError
from dotfiles_installer.paths import validate_link_paths
from dotfiles_installer.selection import select_group


class SelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sources = [Path("/repo/.bashrc"), Path("/repo/all"), Path("/repo/none")]

    def test_selection_keywords_and_literal_names(self) -> None:
        self.assertEqual(select_group("all", self.sources), self.sources)
        self.assertEqual(select_group("none", self.sources), [])
        self.assertEqual(
            select_group(" .bashrc, ./all, ./none, .bashrc ", self.sources),
            self.sources,
        )

    def test_rejects_invalid_and_empty_choices(self) -> None:
        for selection in ("missing", ".bashrc,,all"):
            with self.subTest(selection=selection), self.assertRaises(InstallError):
                select_group(selection, self.sources)


class PathValidationTests(unittest.TestCase):
    def test_rejects_repository_and_target_overlaps(self) -> None:
        repo = Path("/tmp/dotfiles")
        with self.assertRaises(InstallError):
            validate_link_paths(repo, repo / "backups", [])
        with self.assertRaises(InstallError):
            validate_link_paths(
                repo,
                Path("/tmp/backups"),
                [(repo / "home/.bashrc", repo / "target")],
            )
        with self.assertRaises(InstallError):
            validate_link_paths(
                repo,
                Path("/tmp/backups"),
                [
                    (repo / "home/.bashrc", Path("/tmp/home/.config")),
                    (repo / ".config/nvim", Path("/tmp/home/.config/nvim")),
                ],
            )


class InstallerIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        temporary_root = Path(self.temporary_directory.name)
        self.repo = temporary_root / "repo"
        self.target_home = temporary_root / "home"
        self.backup_parent = temporary_root / "backups"
        (self.repo / "home").mkdir(parents=True)
        (self.repo / ".config/nvim").mkdir(parents=True)
        (self.repo / "home/.bashrc").write_text("managed\n")
        (self.repo / ".config/nvim/init.lua").write_text("managed\n")
        self.target_home.mkdir()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def environment(self) -> dict[str, str]:
        return {
            "DOTFILES_HOME": str(self.target_home),
            "DOTFILES_BACKUP_DIR": str(self.backup_parent),
        }

    def test_installs_backs_up_and_is_idempotent(self) -> None:
        (self.target_home / ".bashrc").write_text("existing\n")

        with patch.dict(os.environ, self.environment(), clear=False), redirect_stdout(
            io.StringIO()
        ):
            self.assertEqual(run(["--all"], self.repo), 0)
            self.assertEqual(run(["--all"], self.repo), 0)

        self.assertEqual(
            (self.target_home / ".bashrc").resolve(),
            (self.repo / "home/.bashrc").resolve(),
        )
        self.assertEqual(
            (self.target_home / ".config/nvim").resolve(),
            (self.repo / ".config/nvim").resolve(),
        )
        backup_runs = list(self.backup_parent.iterdir())
        self.assertEqual(len(backup_runs), 1)
        self.assertEqual((backup_runs[0] / ".bashrc").read_text(), "existing\n")

    def test_dry_run_does_not_modify_targets(self) -> None:
        target = self.target_home / ".bashrc"
        target.write_text("existing\n")

        with patch.dict(os.environ, self.environment(), clear=False), redirect_stdout(
            io.StringIO()
        ):
            self.assertEqual(
                run(["--dry-run", "--home", ".bashrc", "--config", "none"], self.repo),
                0,
            )

        self.assertFalse(target.is_symlink())
        self.assertEqual(target.read_text(), "existing\n")
        self.assertFalse(self.backup_parent.exists())

    def test_down_arrow_does_not_cancel_interactive_selection(self) -> None:
        master_fd, slave_fd = pty.openpty()
        environment = os.environ | self.environment() | {"NO_COLOR": "1"}
        process = subprocess.Popen(
            [sys.executable, PROJECT_ROOT / "install.py", "--dry-run"],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            env=environment,
            close_fds=True,
        )
        os.close(slave_fd)
        try:
            output = b""
            while b"Select dotfiles to install" not in output:
                readable, _, _ = select.select([master_fd], [], [], 5)
                self.assertTrue(readable, "interactive prompt was not rendered")
                output += os.read(master_fd, 4096)
            os.write(master_fd, b"\x1b[B\r")
            return_code = process.wait(timeout=5)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            os.close(master_fd)

        self.assertEqual(return_code, 0)


if __name__ == "__main__":
    unittest.main()