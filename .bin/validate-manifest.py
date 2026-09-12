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
# Exact per-source field allowlist: the complete contract consumed by
# Ansible (tasks/*.yml, playbook.yml) plus the schema-hint fields
# (version/features/sha256/interpreter). Reject anything else.
ALLOWED_FIELDS = {
    "apt": {"source", "package", "repo", "profiles"},
    "cargo": {"source", "crate", "version", "features", "profiles"},
    "flatpak": {"source", "package", "remote", "profiles"},
    "npm": {"source", "package", "version", "profiles"},
    "script": {"source", "url", "creates", "args", "interpreter", "link",
               "sha256", "floating_ok", "profiles"},
    "deb": {"source", "url", "sha256", "profiles"},
    "archive": {"source", "url", "url_amd64", "url_arm64", "url_armhf",
                "url_i386", "dest", "creates", "strip", "link", "sha256",
                "profiles"},
    "git": {"source", "repo", "creates", "dest", "version", "build",
            "profiles"},
}
SEQUENCE_FIELDS = {"script": ("args",), "git": ("build",),
                   "cargo": ("features",)}
NUMBER_FIELDS = {"archive": ("strip",)}
STRING_FIELDS = {
    "apt": ("package", "repo"),
    "cargo": ("crate", "version"),
    "flatpak": ("package", "remote"),
    "npm": ("package", "version"),
    "script": ("url", "creates", "interpreter", "link", "sha256"),
    "deb": ("url", "sha256"),
    "archive": ("url", "url_amd64", "url_arm64", "url_armhf", "url_i386",
                "dest", "creates", "link", "sha256"),
    "git": ("repo", "creates", "dest", "version"),
}
URL_FIELDS = ("url", "url_amd64", "url_arm64", "url_armhf", "url_i386")
PATH_TRAVERSAL_RE = re.compile(r"(^|/)\.\.(/|$)")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
SUPPORTED_INTERPRETERS = {"sh", "bash"}
HOME_PATH_FIELDS = ("creates", "dest")


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
        unknown = sorted(set(entry) - ALLOWED_FIELDS[source])
        if unknown:
            errors.append(
                f"packages.json: '{name}': unknown fields for source '{source}': {unknown}"
            )
        for field in STRING_FIELDS.get(source, ()):
            if field in entry:
                val = entry[field]
                if not isinstance(val, str) or not val:
                    errors.append(
                        f"packages.json: '{name}': field '{field}' must be a non-empty string"
                    )
        for field in SEQUENCE_FIELDS.get(source, ()):
            if field in entry:
                val = entry[field]
                if not isinstance(val, list):
                    errors.append(
                        f"packages.json: '{name}': field '{field}' must be a list"
                    )
                elif field != "build" and not val:
                    errors.append(
                        f"packages.json: '{name}': field '{field}' must be a non-empty list"
                    )
                elif field == "build":
                    for step in val:
                        if isinstance(step, str):
                            if not step:
                                errors.append(
                                    f"packages.json: '{name}': build steps must be non-empty strings"
                                )
                        elif isinstance(step, dict):
                            if set(step) - {"cmd", "creates"}:
                                errors.append(
                                    f"packages.json: '{name}': build step allows only 'cmd'/'creates' (got {sorted(step)})"
                                )
                            if not isinstance(step.get("cmd"), str) or not step.get("cmd"):
                                errors.append(
                                    f"packages.json: '{name}': build step requires non-empty 'cmd'"
                                )
                        else:
                            errors.append(
                                f"packages.json: '{name}': build steps must be strings or cmd objects"
                            )
        for field in NUMBER_FIELDS.get(source, ()):
            if field in entry and (isinstance(entry[field], bool) or not isinstance(entry[field], int)):
                errors.append(
                    f"packages.json: '{name}': field '{field}' must be an integer"
                )
        for field in URL_FIELDS:
            if field in entry and isinstance(entry[field], str):
                if not entry[field].startswith("https://"):
                    errors.append(
                        f"packages.json: '{name}': field '{field}' must be an https URL"
                    )
        if "sha256" in entry and isinstance(entry["sha256"], str):
            if not SHA256_RE.match(entry["sha256"]):
                errors.append(
                    f"packages.json: '{name}': field 'sha256' must be 64 hex chars"
                )
        for field in HOME_PATH_FIELDS:
            if field in entry and isinstance(entry[field], str):
                if PATH_TRAVERSAL_RE.search(entry[field]):
                    errors.append(
                        f"packages.json: '{name}': field '{field}' must not contain path traversal (..)"
                    )
        if "interpreter" in entry and entry["interpreter"] not in SUPPORTED_INTERPRETERS:
            errors.append(
                f"packages.json: '{name}': unsupported interpreter '{entry['interpreter']}' (choose from {sorted(SUPPORTED_INTERPRETERS)})"
            )
        if source in ("archive", "script") and "link" in entry:
            link = entry["link"]
            if not isinstance(link, str) or not link or link[0] in "~/":
                errors.append(
                    f"packages.json: '{name}': field 'link' must be a repo-relative path (not starting with '~' or '/')"
                )
            elif PATH_TRAVERSAL_RE.search(link):
                errors.append(
                    f"packages.json: '{name}': field 'link' must not contain path traversal (..)"
                )
        if source == "script" and "sha256" not in entry and entry.get("floating_ok") is not True:
            errors.append(
                f"packages.json: '{name}': floating script without sha256 must set 'floating_ok: true' (explicit integrity exception)"
            )
        if "version" in entry and source in ("cargo", "npm", "git"):
            if not isinstance(entry["version"], str) or not entry["version"]:
                errors.append(
                    f"packages.json: '{name}': field 'version' must be a non-empty string"
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
        if not deps_list:
            errors.append(
                f"package-deps.json: '{name}': must be a non-empty list"
            )
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
        if name == "$schema":
            continue
        if not isinstance(remote, dict):
            errors.append(f"flatpak-remotes.json: '{name}': entry must be an object")
            continue
        if set(remote) - {"url"}:
            errors.append(
                f"flatpak-remotes.json: '{name}': unknown fields {sorted(set(remote) - {'url'})} (only 'url' allowed)"
            )
        url = remote.get("url")
        if not isinstance(url, str) or not url:
            errors.append(
                f"flatpak-remotes.json: '{name}': missing field 'url' (non-empty string)"
            )
        elif not url.startswith("https://"):
            errors.append(
                f"flatpak-remotes.json: '{name}': field 'url' must be an https URL"
            )


def validate_repos(repos, errors):
    if not isinstance(repos, dict):
        errors.append("repos.json: top level must be an object")
        return
    for name, repo in repos.items():
        if name == "$schema":
            continue
        if not isinstance(repo, dict):
            errors.append(f"repos.json: '{name}': entry must be an object")
            continue
        if set(repo) - {"key_url", "keyring", "repo", "key_sha256", "key_fingerprint"}:
            errors.append(
                f"repos.json: '{name}': unknown fields {sorted(set(repo) - {'key_url', 'keyring', 'repo', 'key_sha256', 'key_fingerprint'})}"
            )
        for field in ("key_url", "keyring", "repo"):
            val = repo.get(field)
            if not isinstance(val, str) or not val:
                errors.append(
                    f"repos.json: '{name}': missing field '{field}' (non-empty string)"
                )
        key_url = repo.get("key_url")
        if isinstance(key_url, str) and key_url and not key_url.startswith("https://"):
            errors.append(
                f"repos.json: '{name}': field 'key_url' must be an https URL"
            )
        keyring = repo.get("keyring")
        if isinstance(keyring, str) and keyring:
            if not keyring.startswith("/usr/share/keyrings/") or not keyring.endswith(".gpg"):
                errors.append(
                    f"repos.json: '{name}': keyring must live under /usr/share/keyrings/ with a .gpg suffix"
                )
            if PATH_TRAVERSAL_RE.search(keyring):
                errors.append(
                    f"repos.json: '{name}': keyring must not contain path traversal (..)"
                )
        line = repo.get("repo")
        if isinstance(line, str) and line:
            if not line.startswith("deb "):
                errors.append(
                    f"repos.json: '{name}': repo line must start with 'deb '"
                )
            if "signed-by=" not in line:
                errors.append(
                    f"repos.json: '{name}': repo line must pin signed-by= to the declared keyring"
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
        if key == "$schema":
            continue
        if key == "global" and m.group(3):
            errors.append(
                f"hooks: '{name}': global hooks cannot use .root (global hooks run unprivileged)"
            )
            continue
        if key != "global" and key not in packages:
            errors.append(
                f"hooks: '{name}': orphan key '{key}' (no such package in packages.json)"
            )
        if not os.access(path, os.X_OK):
            errors.append(f"hooks: '{name}': not executable (chmod +x)")
    seen = {}
    for name in names:
        if name == "README.md":
            continue
        path = os.path.join(hooks_dir, name)
        if not os.path.isfile(path):
            continue
        m = HOOK_RE.match(name)
        if not m:
            continue
        if m.group(1) == "$schema":
            continue
        dup_key = (m.group(1), m.group(2), bool(m.group(3)))
        if dup_key in seen:
            errors.append(
                f"hooks: '{name}': duplicate hook for {seen[dup_key]} (at most one .sh/.py per key.phase[.root])"
            )
        else:
            seen[dup_key] = name


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
    try:
        validate_packages(packages, repos, flatpak_remotes, errors)
    except Exception as exc:
        errors.append(f"packages.json: validator error ({exc})")
    try:
        validate_deps(deps, packages, errors)
    except Exception as exc:
        errors.append(f"package-deps.json: validator error ({exc})")
    try:
        validate_repos(repos, errors)
    except Exception as exc:
        errors.append(f"repos.json: validator error ({exc})")
    try:
        validate_flatpak_remotes(flatpak_remotes, errors)
    except Exception as exc:
        errors.append(f"flatpak-remotes.json: validator error ({exc})")
    try:
        # Duplicate link destinations across script/archive entries would
        # collide in ~/.local/bin.
        seen_links = {}
        if isinstance(packages, dict):
            for name, entry in packages.items():
                if name == "$schema" or not isinstance(entry, dict):
                    continue
                link = entry.get("link")
                if isinstance(link, str) and entry.get("source") in ("script", "archive"):
                    dest = link.split("/")[-1]
                    if dest in seen_links:
                        errors.append(
                            f"packages.json: '{name}': duplicate link destination '{dest}' (also '{seen_links[dest]}')"
                        )
                    else:
                        seen_links[dest] = name
    except Exception as exc:
        errors.append(f"packages.json: link check error ({exc})")
    try:
        validate_hooks(packages, args.hooks, errors)
    except Exception as exc:
        errors.append(f"hooks: validator error ({exc})")
    for err in errors:
        print(err, file=sys.stderr)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
