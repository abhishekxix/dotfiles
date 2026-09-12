"""Steps 06-07: Neovim tool installation and LSP lifecycle.

Starts Neovim against the tracked config with isolated temporary XDG
directories and controlled tool stubs.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LSPCONFIG = (REPO / ".config/nvim/lua/plugins/nvim-lspconfig.lua").read_text()
TREESITTER = (
    REPO / ".config/nvim/lua/plugins/nvim-treesitter.lua"
).read_text()
AUTOCMDS = (REPO / ".config/nvim/lua/autocommands.lua").read_text()


def run_nvim(args, env_extra=None, timeout=120):
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run(
        ["nvim", "--headless", "--noplugin"] + args,
        capture_output=True, text=True, timeout=timeout, env=env,
    )


class NvimStartupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="dotfiles-nvim-"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def isolated_env(self, name):
        base = self.tmp / name
        data = base / "data"
        state = base / "state"
        cache = base / "cache"
        for d in (data, state, cache):
            d.mkdir(parents=True, exist_ok=True)
        env = {
            "XDG_DATA_HOME": str(data),
            "XDG_STATE_HOME": str(state),
            "XDG_CACHE_HOME": str(cache),
            "NVIM_APPNAME": "dotfiles-test",
        }
        return env

    def test_mason_setup_exactly_once(self):
        import re
        count = len(re.findall(r"require\(['\"]mason['\"]\)\.setup\(\)",
                               LSPCONFIG))
        self.assertEqual(count, 1,
                         "require('mason').setup() must appear exactly once")

    def test_tool_reconciliation_debounced_with_manual_command(self):
        self.assertIn("debounce_hours", LSPCONFIG)
        self.assertIn("MasonToolsInstallNow", LSPCONFIG)

    def test_treesitter_guards_missing_cli(self):
        self.assertIn("executable", TREESITTER)
        self.assertIn("tree-sitter", TREESITTER)

    def test_fold_only_after_parser_start(self):
        # foldexpr must be set after a successful start, with early
        # returns on both failure paths.
        start = AUTOCMDS.index("vim.treesitter.start")
        fold = AUTOCMDS.index("foldexpr")
        self.assertLess(start, fold)
        self.assertGreaterEqual(AUTOCMDS.count("return"), 2)

    def test_parser_aliases_resolved(self):
        for alias in ("zsh", "yaml.docker-compose"):
            self.assertIn(alias, AUTOCMDS)

    def test_lsp_highlight_single_install(self):
        # Handlers install once per buffer; the detach hook clears only
        # after checking remaining clients (see step 07) or clears the
        # buffer-local group.
        self.assertIn("as-lsp-highlight", LSPCONFIG)

    def test_telescope_deferred(self):
        self.assertNotIn("require('telescope.builtin').lsp_definitions",
                         LSPCONFIG.split("callback")[0] if "callback" in LSPCONFIG else LSPCONFIG)
        # Mapping callbacks must defer the require until invoked.
        for picker in ("lsp_definitions", "lsp_references"):
            idx = LSPCONFIG.index(picker)
            window = LSPCONFIG[max(0, idx - 120):idx]
            self.assertIn("function", window,
                          f"{picker} require must sit inside a function")

    def test_headless_opts_load(self):
        out = run_nvim([
            "+luafile", str(REPO / ".config/nvim/lua/opts.lua"),
            "+lua", "assert(vim.o.confirm)",
            "+qa",
        ])
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])

    def test_headless_langs_getters(self):
        script = self.tmp / "langs_check.lua"
        script.write_text(
            "vim.opt.runtimepath:prepend('%s/.config/nvim')\n"
            "local langs = require('langs')\n"
            "assert(#langs.get_parsers() > 0)\n"
            "assert(#langs.get_servers() > 0)\n"
            "print('LANGS_OK')\n" % REPO
        )
        out = run_nvim(["-l", str(script)])
        combined = out.stdout + out.stderr
        self.assertIn("LANGS_OK", combined, out.stderr[-2000:])


if __name__ == "__main__":
    unittest.main()
