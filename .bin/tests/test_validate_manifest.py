"""Step 15: strict manifest validation.

Generates temporary malformed manifests covering every validation family
and top-level/value type. No fixture directory is committed.
"""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / ".bin"))
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "validate_manifest", str(REPO / ".bin/validate-manifest.py"))
V = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(V)


def base_manifests():
    pkgs = json.loads((REPO / "ansible/vars/packages.json").read_text())
    deps = json.loads((REPO / "ansible/vars/package-deps.json").read_text())
    repos = json.loads((REPO / "ansible/vars/repos.json").read_text())
    remotes = json.loads(
        (REPO / "ansible/vars/flatpak-remotes.json").read_text())
    hooks = str(REPO / "ansible/hooks")
    return pkgs, deps, repos, remotes, hooks


class ValidateManifestTest(unittest.TestCase):
    def check(self, pkgs=None, deps=None, repos=None, remotes=None):
        base = base_manifests()
        pkgs = base[0] if pkgs is None else pkgs
        deps = base[1] if deps is None else deps
        repos = base[2] if repos is None else repos
        remotes = base[3] if remotes is None else remotes
        errors = []
        V.validate_packages(pkgs, repos, remotes, errors)
        V.validate_deps(deps, pkgs, errors)
        V.validate_repos(repos, errors)
        V.validate_flatpak_remotes(remotes, errors)
        return errors

    def test_valid_manifests_pass(self):
        self.assertEqual(self.check(), [])

    def test_validator_cli_passes(self):
        out = subprocess.run([str(REPO / ".bin/validate-manifest.py")],
                             capture_output=True, text=True, cwd=REPO)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])

    def test_unknown_and_source_incompatible_fields(self):
        pkgs, _, _, _, _ = base_manifests()
        bad = copy.deepcopy(pkgs)
        bad["fzf"]["bogus_field"] = 1
        self.assertTrue(any("unknown fields" in e for e in self.check(pkgs=bad)))
        bad2 = copy.deepcopy(pkgs)
        bad2["fzf"]["crate"] = "x"  # cargo-only field on an apt entry
        self.assertTrue(any("unknown fields" in e for e in self.check(pkgs=bad2)))

    def test_wrong_field_types(self):
        pkgs, _, _, _, _ = base_manifests()
        bad = copy.deepcopy(pkgs)
        bad["starship"]["args"] = "not-a-list"
        self.assertTrue(any("must be a list" in e for e in self.check(pkgs=bad)))
        bad2 = copy.deepcopy(pkgs)
        bad2["neovim"]["strip"] = "1"
        self.assertTrue(any("must be an integer" in e for e in self.check(pkgs=bad2)))
        bad3 = copy.deepcopy(pkgs)
        bad3["fzf"]["package"] = ""
        self.assertTrue(any("non-empty string" in e for e in self.check(pkgs=bad3)))
        bad4 = copy.deepcopy(pkgs)
        bad4["neovim"]["strip"] = True
        self.assertTrue(any("must be an integer" in e for e in self.check(pkgs=bad4)))

    def test_empty_required_strings_lists(self):
        pkgs, deps, _, _, _ = base_manifests()
        bad = copy.deepcopy(pkgs)
        bad["direnv"]["package"] = ""
        self.assertTrue(self.check(pkgs=bad))
        bad2 = copy.deepcopy(pkgs)
        bad2["direnv"]["profiles"] = []
        self.assertTrue(any("non-empty list" in e for e in self.check(pkgs=bad2)))
        bad3 = copy.deepcopy(deps)
        key = next(k for k in bad3 if k != "$schema")
        bad3[key] = []
        errs = []
        V.validate_deps(bad3, pkgs, errs)
        self.assertTrue(any("non-empty" in e for e in errs))

    def test_invalid_urls_checksums(self):
        pkgs, _, _, _, _ = base_manifests()
        bad = copy.deepcopy(pkgs)
        bad["starship"]["url"] = "http://insecure.example/x"
        self.assertTrue(any("https URL" in e for e in self.check(pkgs=bad)))
        bad2 = copy.deepcopy(pkgs)
        bad2["starship"]["sha256"] = "xyz"
        errs = []
        V.validate_packages(bad2, {}, {}, errs)
        self.assertTrue(any("64 hex" in e for e in errs))

    def test_path_traversal(self):
        pkgs, _, _, _, _ = base_manifests()
        bad = copy.deepcopy(pkgs)
        bad["neovim"]["dest"] = "~/../evil"
        self.assertTrue(any("traversal" in e for e in self.check(pkgs=bad)))
        bad2 = copy.deepcopy(pkgs)
        bad2["neovim"]["link"] = "../evil"
        errs = []
        V.validate_packages(bad2, {}, {}, errs)
        self.assertTrue(any("traversal" in e for e in errs))

    def test_unsupported_interpreter(self):
        pkgs, _, _, _, _ = base_manifests()
        bad = copy.deepcopy(pkgs)
        bad["starship"]["interpreter"] = "fish"
        self.assertTrue(any("interpreter" in e for e in self.check(pkgs=bad)))

    def test_repos_and_remotes_semantics(self):
        _, _, repos, remotes, _ = base_manifests()
        bad = copy.deepcopy(repos)
        key = next(k for k in bad if k != "$schema")
        bad[key]["repo"] = "deb https://example.com stable main"
        errs = []
        V.validate_repos(bad, errs)
        self.assertTrue(any("signed-by" in e for e in errs))
        bad2 = copy.deepcopy(repos)
        bad2[key]["keyring"] = "/tmp/evil.gpg"
        errs = []
        V.validate_repos(bad2, errs)
        self.assertTrue(any("keyring" in e for e in errs))
        bad3 = copy.deepcopy(remotes)
        rkey = next(k for k in bad3 if k != "$schema")
        bad3[rkey]["url"] = "http://insecure.example/x"
        errs = []
        V.validate_flatpak_remotes(bad3, errs)
        self.assertTrue(any("https URL" in e for e in errs))

    def test_malformed_input_collects_diagnostics(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "packages.json"
            bad.write_text("{not json")
            out = subprocess.run(
                [str(REPO / ".bin/validate-manifest.py"),
                 "--packages", str(bad)],
                capture_output=True, text=True, cwd=REPO)
            self.assertNotEqual(out.returncode, 0)
            self.assertIn("invalid JSON", out.stderr)
            self.assertNotIn("Traceback", out.stderr)


if __name__ == "__main__":
    unittest.main()
