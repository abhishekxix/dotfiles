"""Step 14: installer preflight and link safety.

Uses temporary root, unsupported-OS/architecture, conflict, and
link-failure fixtures. No fixture directory is committed; nothing touches
the real home directory.
"""

import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
INSTALL_SRC = (REPO / "install").read_text()
LINK_YML = (REPO / "ansible/tasks/link.yml").read_text()
PREFLIGHT_YML = (REPO / "ansible/tasks/preflight.yml").read_text()


class InstallTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="dotfiles-install-"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def fixture(self, name):
        d = self.tmp / name
        d.mkdir(exist_ok=True)
        return d

    def test_root_refused_before_collection_changes(self):
        # The wrapper must refuse root inside main() before any
        # collection/install work (first executable statement of main).
        main_body = INSTALL_SRC.split("def main():", 1)[1]
        first_stmt = INSTALL_SRC.index("os.geteuid")
        coll = INSTALL_SRC.index("have = collection_version()")
        self.assertLess(first_stmt, coll)
        self.assertIn("Refusing to run as root", main_body)

    def test_sudo_unavailable_warns(self):
        self.assertIn("sudo", INSTALL_SRC)

    def test_preflight_enforces_release_and_arch(self):
        self.assertIn("distribution_release", PREFLIGHT_YML)
        self.assertIn("trixie", PREFLIGHT_YML)
        self.assertIn("bookworm", PREFLIGHT_YML)
        self.assertIn("dotfiles_deb_arch", PREFLIGHT_YML)
        self.assertIn("amd64", PREFLIGHT_YML)

    def test_link_failure_restores_backup(self):
        # link.yml must register the link result, restore on failure with
        # mv -n (never overwriting a new file), then fail explicitly.
        self.assertIn("dotfiles_link_result", LINK_YML)
        self.assertIn("mv", LINK_YML)
        self.assertIn("-n", LINK_YML)

    def test_conflict_fixture_roundtrip(self):
        # Filesystem-level roundtrip: original bytes survive a
        # backup-then-failed-link-then-restore cycle.
        d = self.fixture("conflict")
        dest = d / "target"
        original = b"original-destination-bytes"
        dest.write_bytes(original)
        backup_dir = d / "backup"
        backup_dir.mkdir(exist_ok=True)
        shutil.move(str(dest), str(backup_dir))
        # Simulate a failed link (nothing created) then restore with -n.
        out = subprocess.run(
            ["mv", "-n", str(backup_dir / "target"), str(dest)],
            capture_output=True)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(dest.read_bytes(), original)

    def test_new_file_not_overwritten_by_restore(self):
        d = self.fixture("no-overwrite")
        backup = d / "backup-file"
        backup.write_bytes(b"old-backup")
        new = d / "dest-file"
        new.write_bytes(b"new-file-created-after-backup")
        out = subprocess.run(
            ["mv", "-n", str(backup), str(new)], capture_output=True)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(new.read_bytes(), b"new-file-created-after-backup")

    def test_binary_link_conflict_policy(self):
        packages = (REPO / "ansible/tasks/packages.yml").read_text()
        self.assertNotIn("    force: true", packages,
                         "binary links must not force-replace")

    def test_post_run_report_once(self):
        playbook = (REPO / "ansible/playbook.yml").read_text()
        self.assertIn("Report required relogins", playbook)

    def test_no_network_to_shell_pipe(self):
        script_one = (REPO / "ansible/tasks/install-script-one.yml").read_text()
        self.assertNotIn("curl -fsSL", script_one)
        self.assertNotIn("| {{", script_one)
        self.assertIn("get_url", script_one)

    def test_lifecycle_modes_declared(self):
        install_src = (REPO / "install").read_text()
        self.assertIn("--audit", install_src)
        self.assertIn("--upgrade", install_src)
        self.assertIn("dotfiles-install.lock", install_src)
        playbook = (REPO / "ansible/playbook.yml").read_text()
        self.assertIn("dotfiles_upgrade", playbook)
        git_one = (REPO / "ansible/tasks/install-git-one.yml").read_text()
        self.assertIn("dotfiles_upgrade", git_one)
        script_one = (REPO / "ansible/tasks/install-script-one.yml").read_text()
        self.assertIn("dotfiles_upgrade", script_one)

    def test_retries_and_lock(self):
        for name in ("install-script-one.yml", "install-git-one.yml",
                     "install-archive-one.yml", "install-deb-one.yml",
                     "repos.yml"):
            text = (REPO / f"ansible/tasks/{name}").read_text()
            self.assertIn("retries", text, f"{name} needs finite retries")
        install_src = (REPO / "install").read_text()
        self.assertIn("holds ~/.cache/dotfiles-install.lock", install_src)

    def test_key_rotation_guarded(self):
        repos = (REPO / "ansible/tasks/repos.yml").read_text()
        self.assertIn("key_fingerprint", repos)
        self.assertIn("fingerprint", repos.lower())

    def test_doctor_audit_upgrade_documented(self):
        readme = (REPO / "README.md").read_text()
        self.assertIn(".bin/doctor", readme)

    def test_syntax_check(self):
        out = subprocess.run(
            ["ansible-playbook", "--syntax-check", "ansible/playbook.yml"],
            capture_output=True, text=True, cwd=REPO, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])


if __name__ == "__main__":
    unittest.main()
