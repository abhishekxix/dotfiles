"""Step 13: doctor is read-only and detects required gaps."""

import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOCTOR = REPO / ".bin/doctor"


def snapshot_home(home):
    out = {}
    for root, _dirs, files in os.walk(home):
        for f in files:
            p = Path(root) / f
            try:
                out[str(p)] = p.read_bytes()
            except OSError:
                out[str(p)] = None
    return out


class DoctorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="dotfiles-doctor-"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_doctor(self, path_dirs, home):
        env = dict(os.environ, HOME=str(home),
                   PATH=os.pathsep.join(str(d) for d in path_dirs))
        return subprocess.run([str(DOCTOR)], capture_output=True, text=True,
                              env=env, timeout=60)

    def make_bin(self, name, tools):
        d = self.tmp / name
        d.mkdir(exist_ok=True)
        for tool, version_out in tools.items():
            exe = d / tool
            exe.write_text("#!/bin/sh\n" + version_out + "\n")
            exe.chmod(exe.stat().st_mode | stat.S_IXUSR)
        return d

    def test_version_mismatch_detected(self):
        manifest = json.loads(
            (REPO / "ansible/vars/packages.json").read_text())
        declared = manifest["neovim"]["url"].split("/v")[1].split("/")[0]
        wrong = "0.0.0" if declared != "0.0.0" else "9.9.9"
        bindir = self.make_bin("mismatch-bin", {
            "nvim": f"echo 'NVIM v{wrong}'",
            "git": "exit 0", "tmux": "exit 0", "zsh": "exit 0",
            "bash": "exit 0", "fzf": "exit 0", "zoxide": "exit 0",
            "direnv": "exit 0", "starship": "exit 0",
            "tree-sitter": "exit 0", "black": "exit 0",
        })
        home = self.tmp / "mismatch-home"
        home.mkdir(exist_ok=True)
        before_home = snapshot_home(home)
        before_tree = subprocess.run(["git", "status", "--porcelain"],
                                     capture_output=True, text=True,
                                     cwd=REPO).stdout
        out = self.run_doctor([bindir], home)
        self.assertEqual(out.returncode, 1)
        self.assertIn(wrong, out.stdout)
        self.assertIn(declared, out.stdout)
        self.assertEqual(snapshot_home(home), before_home)
        after_tree = subprocess.run(["git", "status", "--porcelain"],
                                    capture_output=True, text=True,
                                    cwd=REPO).stdout
        self.assertEqual(before_tree, after_tree)

    def test_missing_required_fails_missing_optional_passes(self):
        bindir = self.make_bin("gaps-bin", {
            "git": "exit 0", "bash": "exit 0",
        })
        home = self.tmp / "gaps-home"
        home.mkdir(exist_ok=True)
        out = self.run_doctor([bindir], home)
        self.assertEqual(out.returncode, 1)
        self.assertIn("Required gaps:", out.stdout)
        # Optional gaps section exists but does not fail on its own.
        bindir2 = self.make_bin("optional-bin", {
            "git": "exit 0", "nvim": "echo 'NVIM v0.12.5'",
            "tmux": "exit 0", "zsh": "exit 0", "bash": "exit 0",
            "fzf": "exit 0", "zoxide": "exit 0", "direnv": "exit 0",
            "starship": "exit 0", "tree-sitter": "exit 0",
            "black": "exit 0", "fc-match": "exit 0",
        })
        out2 = self.run_doctor([bindir2], home)
        # Only optional desktop tools (rofi/dunst/xrandr) may be missing.
        self.assertIn("Required gaps: none", out2.stdout)
        self.assertEqual(out2.returncode, 0)


if __name__ == "__main__":
    unittest.main()
