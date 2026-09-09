#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
PACKAGES_PATH = os.path.join(REPO_ROOT, "ansible", "vars", "packages.json")
DEPS_PATH = os.path.join(REPO_ROOT, "ansible", "vars", "package-deps.json")
REPOS_PATH = os.path.join(REPO_ROOT, "ansible", "vars", "repos.json")
FLATPAK_REMOTES_PATH = os.path.join(REPO_ROOT, "ansible", "vars", "flatpak-remotes.json")
HOOKS_DIR = os.path.join(REPO_ROOT, "ansible", "hooks")
HOOK_RE = re.compile(r"^([^.]+)\.(pre|post)(\.root)?\.(sh|py)$")

SOURCES = {"apt", "cargo", "flatpak", "npm", "script", "deb", "archive", "git"}
PROFILES = {"workstation", "server"}
REQUIRED_FIELDS = {
    "apt": ("package",),
    "cargo": ("crate",),
    "flatpak": ("package", "remote"),
    "npm": ("package",),
    "script": ("url", "creates"),
    "deb": ("url",),
    "archive": ("url", "dest", "creates"),
    "git": ("repo", "creates"),
}
SEQUENCE_FIELDS = {"script": ("args",), "git": ("build",)}
NUMBER_FIELDS = {"archive": ("strip",)}


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except OSError as exc:
        print(f"{path}: cannot read ({exc.strerror})", file=sys.stderr)
        sys.exit(2)
    except ValueError as exc:
        print(f"{path}: invalid JSON ({exc})", file=sys.stderr)
        sys.exit(2)


def validate_packages(packages, repos, flatpak_remotes, errors):
    if not isinstance(packages, dict):
        errors.append("packages.json: top level must be an object")
        return
    repo_ids = set(repos) if isinstance(repos, dict) else set()
    flatpak_remote_ids = set(flatpak_remotes) if isinstance(flatpak_remotes, dict) else set()
    for name, entry in packages.items():
        if name == "$schema":
            continue
        if not isinstance(entry, dict):
            errors.append(f"packages.json: '{name}': entry must be an object")
            continue
        source = entry.get("source")
        if source is None:
            errors.append(f"packages.json: '{name}': missing field 'source'")
            continue
        if source not in SOURCES:
            errors.append(
                f"packages.json: '{name}': unknown source '{source}' (choose from {sorted(SOURCES)})"
            )
            continue
        for field in REQUIRED_FIELDS[source]:
            if field not in entry:
                errors.append(
                    f"packages.json: '{name}': source '{source}' requires field '{field}'"
                )
        for field in SEQUENCE_FIELDS.get(source, ()):
            if field in entry and not isinstance(entry[field], list):
                errors.append(
                    f"packages.json: '{name}': field '{field}' must be a list"
                )
        for field in NUMBER_FIELDS.get(source, ()):
            if field in entry and not isinstance(entry[field], (int, float)):
                errors.append(
                    f"packages.json: '{name}': field '{field}' must be a number"
                )
        if source in ("archive", "script") and "link" in entry:
            link = entry["link"]
            if not isinstance(link, str) or not link or link[0] in "~/":
                errors.append(
                    f"packages.json: '{name}': field 'link' must be a repo-relative path (not starting with '~' or '/')"
                )
        if source == "apt" and "repo" in entry and entry["repo"] not in repo_ids:
            errors.append(
                f"packages.json: '{name}': repo id '{entry['repo']}' not defined in repos.json"
            )
        if source == "flatpak" and "remote" in entry and entry["remote"] not in flatpak_remote_ids:
            errors.append(
                f"packages.json: '{name}': remote id '{entry['remote']}' not defined in flatpak-remotes.json"
            )
        profiles = entry.get("profiles")
        if profiles is None:
            errors.append(f"packages.json: '{name}': missing field 'profiles'")
        elif not isinstance(profiles, list) or not profiles:
            errors.append(
                f"packages.json: '{name}': field 'profiles' must be a non-empty list"
            )
        else:
            unknown = [p for p in profiles if p not in PROFILES]
            if unknown:
                errors.append(
                    f"packages.json: '{name}': unknown profiles {unknown} (choose from {sorted(PROFILES)})"
                )


def validate_deps(deps, packages, errors):
    if not isinstance(deps, dict):
        errors.append("package-deps.json: top level must be an object")
        return
    for name, deps_list in deps.items():
        if name == "$schema":
            continue
        if name not in packages:
            errors.append(
                f"package-deps.json: '{name}': not a package in packages.json"
            )
        if isinstance(deps_list, (str, dict)) or not isinstance(deps_list, list):
            errors.append(
                f"package-deps.json: '{name}': must be a list of package names"
            )
            continue
        for dep in deps_list:
            if not isinstance(dep, str) or not dep:
                errors.append(
                    f"package-deps.json: '{name}': dep entries must be non-empty strings (got {dep!r})"
                )


def validate_flatpak_remotes(remotes, errors):
    if not isinstance(remotes, dict):
        errors.append("flatpak-remotes.json: top level must be an object")
        return
    for name, remote in remotes.items():
        if not isinstance(remote, dict):
            errors.append(f"flatpak-remotes.json: '{name}': entry must be an object")
            continue
        url = remote.get("url")
        if not isinstance(url, str) or not url:
            errors.append(
                f"flatpak-remotes.json: '{name}': missing field 'url' (non-empty string)"
            )


def validate_hooks(packages, hooks_dir, errors):
    try:
        names = sorted(os.listdir(hooks_dir))
    except FileNotFoundError:
        return
    except OSError as exc:
        errors.append(f"hooks: cannot list ({exc.strerror})")
        return
    for name in names:
        if name == "README.md":
            continue
        path = os.path.join(hooks_dir, name)
        if not os.path.isfile(path):
            continue
        m = HOOK_RE.match(name)
        if not m:
            errors.append(
                f"hooks: '{name}': must match <key>.<pre|post>[.root].<sh|py>"
            )
            continue
        key = m.group(1)
        if key != "global" and key not in packages:
            errors.append(
                f"hooks: '{name}': orphan key '{key}' (no such package in packages.json)"
            )
        if not os.access(path, os.X_OK):
            errors.append(f"hooks: '{name}': not executable (chmod +x)")


def main():
    parser = argparse.ArgumentParser(
        prog="validate-manifest.py",
        description="Validate ansible/vars manifest files (stdlib-only).",
    )
    parser.add_argument("--packages", default=PACKAGES_PATH)
    parser.add_argument("--deps", default=DEPS_PATH)
    parser.add_argument("--repos", default=REPOS_PATH)
    parser.add_argument("--flatpak-remotes", default=FLATPAK_REMOTES_PATH)
    parser.add_argument("--hooks", default=HOOKS_DIR)
    args = parser.parse_args()

    packages = load(args.packages)
    deps = load(args.deps)
    repos = load(args.repos)
    if not isinstance(repos, dict):
        print(f"{args.repos}: top level must be an object", file=sys.stderr)
        sys.exit(2)
    flatpak_remotes = load(args.flatpak_remotes)

    errors = []
    validate_packages(packages, repos, flatpak_remotes, errors)
    validate_deps(deps, packages, errors)
    validate_flatpak_remotes(flatpak_remotes, errors)
    validate_hooks(packages, args.hooks, errors)
    for err in errors:
        print(err, file=sys.stderr)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
