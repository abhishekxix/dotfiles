"""Step 01: shell startup must survive partial provisioning.

Creates disposable HOME fixtures with plugin/starship paths present and
absent, then sources the tracked .zshrc/.bashrc equivalents for syntax and
behavior assertions.
"""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ZSHRC = (REPO / "home/.zshrc").read_text()
BASHRC = (REPO / "home/.bashrc").read_text()


class ShellStartupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="dotfiles-shell-"))
        for name in ("zshrc_fixtures", "bashrc_fixtures"):
            (cls.tmp / name).mkdir()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_syntax_checks(self):
        subprocess.run(["bash", "-n", str(REPO / "home/.bashrc")],
                       check=True)
        subprocess.run(["zsh", "-n", str(REPO / "home/.zshrc")],
                       check=True)

    def test_zsh_creates_compdump_parent(self):
        self.assertRegex(
            ZSHRC,
            r"mkdir -p.*XDG_CACHE_HOME.*\/zsh",
            "compinit cache parent must be created before compinit",
        )

    def test_zsh_guards_optional_sources(self):
        for needle in ("zsh-autosuggestions", "zsh-syntax-highlighting"):
            line = next(
                line for line in ZSHRC.splitlines() if needle in line
            )
            self.assertIn("[ -f", line,
                          f"{needle} source must be guarded by -f test")

    def test_zsh_highlighting_loads_last(self):
        hl = ZSHRC.index("zsh-syntax-highlighting")
        for needle in ("zsh-autosuggestions", "key-bindings.zsh",
                       "starship init", "fnm env"):
            if needle in ZSHRC:
                self.assertLess(
                    ZSHRC.index(needle), hl,
                    f"{needle} must initialize before syntax highlighting",
                )

    def test_zsh_starship_guarded(self):
        self.assertRegex(ZSHRC, r"command -v starship[\s\S]*starship init")

    def test_fzf_scoped_previews(self):
        for rc, name in ((ZSHRC, ".zshrc"), (BASHRC, ".bashrc")):
            self.assertNotRegex(
                rc, r"(?m)^export FZF_DEFAULT_OPTS=.*--preview",
                f"{name}: global fzf opts must carry no preview",
            )
            self.assertIn("FZF_CTRL_T_OPTS", rc)
            self.assertIn("FZF_ALT_C_OPTS", rc)

    def test_zoxide_direnv_guarded_init(self):
        for rc, shell in ((ZSHRC, "zsh"), (BASHRC, "bash")):
            self.assertRegex(
                rc, r"command -v zoxide[\s\S]*zoxide init %s" % shell)
            self.assertRegex(
                rc, r"command -v direnv[\s\S]*direnv hook %s" % shell)

    def test_zsh_single_shared_history_mode(self):
        self.assertIn("set -o share_history", ZSHRC)
        self.assertNotIn("set -o append_history", ZSHRC)
        hist = int(re.search(r"^HISTSIZE=(\d+)", ZSHRC, re.M).group(1))
        save = int(re.search(r"^SAVEHIST=(\d+)", ZSHRC, re.M).group(1))
        self.assertGreater(hist, save,
                           "extra in-memory capacity expires duplicates")

    def test_bash_prompt_command_composed_not_replaced(self):
        self.assertIn("_dotfiles_share_history", BASHRC)
        self.assertIn("PROMPT_COMMAND", BASHRC)
        # An existing hook must survive sourcing.
        script = (
            "export HOME=%s; PROMPT_COMMAND='echo kept'; "
            "source %s/home/.bashrc; echo \"$PROMPT_COMMAND\""
            % (self.tmp / "bashrc_fixtures", REPO)
        )
        out = subprocess.run(["bash", "-i", "-c", script],
                             capture_output=True, text=True)
        self.assertIn("echo kept", out.stdout + out.stderr)
        self.assertIn("_dotfiles_share_history", out.stdout + out.stderr)

    def test_bash_gpg_tty_refresh_hook(self):
        self.assertIn("GPG_TTY", BASHRC)
        self.assertIn("_dotfiles_refresh_gpg_tty", BASHRC)

    def test_zsh_partial_install_starts_clean(self):
        home = self.tmp / "zshrc_fixtures" / "partial"
        home.mkdir(exist_ok=True)
        env = dict(os.environ, HOME=str(home),
                   XDG_CACHE_HOME=str(home / ".cache"))
        # Stub compinit/site functions so sourcing is hermetic.
        script = (
            "autoload() { :; }; compinit() { :; }; "
            "bindkey() { :; }; fpath=(); "
            "source %s/home/.zshrc; echo STARTED_OK"
            % REPO
        )
        out = subprocess.run(["zsh", "-c", script], capture_output=True,
                             text=True, env=env)
        self.assertIn("STARTED_OK", out.stdout)
        self.assertNotIn("no such file", out.stderr)
        self.assertTrue((home / ".cache/zsh").is_dir())


if __name__ == "__main__":
    unittest.main()
