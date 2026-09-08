# 01 — Flatpak source plumbing

| Field | Value |
|---|---|
| Status | Done |
| Step | 01 |
| Commit | `ANSIBLE(01): add flatpak install source (remotes + app installs)` |

## Files

- `ansible/vars/packages.schema.json` (EDIT — add `flatpak` definition)
- `.bin/validate-manifest.py` (EDIT — flatpak rules + remotes-file validation)
- `ansible/vars/flatpak-remotes.json` (CREATE — id-keyed remote definitions)
- `ansible/playbook.yml` (EDIT — vars for flatpak selection + remotes; toolchain import name)
- `ansible/tasks/toolchain.yml` (EDIT — flatpak CLI bootstrap, fnm-style)
- `ansible/tasks/packages.yml` (EDIT — remote + app install tasks)
- `.pre-commit-config.yaml` (EDIT — validator triggers on the new remotes file)

## Changes

### Manifest shape

A flatpak entry looks like (field names mirror apt/npm `package` + apt `repo`
reference style):

```json
"okular": {
  "package": "org.kde.okular",
  "profiles": ["workstation"],
  "remote": "flathub",
  "source": "flatpak"
}
```

`remote` must be a key in the new `ansible/vars/flatpak-remotes.json`:

```json
{
  "flathub": {
    "url": "https://dl.flathub.org/repo/flathub.flatpakrepo"
  }
}
```

### `packages.schema.json`

Add a `flatpak` definition alongside the other per-source definitions:
`required: [source, package, remote, profiles]`, `additionalProperties: false`,
`source` const `flatpak`, `package`/`remote` non-empty strings (description
notes `package` is a Flatpak application ID and `remote` is enforced against
`flatpak-remotes.json` by the validator, not expressible here — same wording
as the apt `repo` note). Reference it from the top-level `oneOf`.

### `.bin/validate-manifest.py`

- Add `"flatpak"` to `SOURCES` and `("package", "remote")` to
  `REQUIRED_FIELDS`.
- Load `flatpak-remotes.json` (new `--flatpak-remotes` arg, default
  `ansible/vars/flatpak-remotes.json`) and validate its shape like
  `repos.json`: top level must be an object; each value an object with a
  non-empty string `url`.
- Unknown `remote` ids on flatpak entries fail with a
  `repo id ... not defined in repos.json`-style error
  (`remote id '<id>' not defined in flatpak-remotes.json`).

### `playbook.yml`

Vars, grouped like their siblings:

- `dotfiles_flatpak_remotes_manifest` next to `dotfiles_repos_manifest`
  (plain `lookup(...) | from_json`, no `$schema` stripping needed).
- `dotfiles_pkgs_flatpak` with the other per-source selections.
- `dotfiles_flatpak_remotes_selected` next to `dotfiles_repos_selected`:
  `dotfiles_pkgs_flatpak | map(attribute='value.remote') | unique | list`.
- Update the toolchain import name to include flatpak
  ("Bootstrap language toolchains (cargo, fnm, flatpak)").

### `tasks/toolchain.yml` (flatpak CLI bootstrap)

fnm/cargo pattern, appended after the existing bootstrap tasks:

1. `Check for flatpak` — `ansible.builtin.command: argv: [flatpak, --version]`,
   `changed_when: false`, `failed_when: false`, gated on
   `(dotfiles_pkgs_flatpak | length) > 0`, register `dotfiles_flatpak_check`.
2. `Install flatpak CLI (flatpak provider)` — `become: true`,
   `ansible.builtin.apt: {name: flatpak, state: present, update_cache: true,
   cache_valid_time: 3600}`, `when` flatpak entries selected AND
   `dotfiles_flatpak_check.rc | default(0) != 0`. `update_cache` covers
   fresh hosts with an empty apt cache (curl-based bootstraps never needed
   it; this one does).

The existing `flatpak` apt manifest entry stays for now (removed in step 02)
so there is no commit where a fresh workstation loses the CLI.

### `tasks/packages.yml`

Appended after the git build steps, both tagged `packages`:

1. `Ensure flatpak remotes (system)` — `community.general.flatpak_remote`,
   loop over `dotfiles_flatpak_remotes_selected`, `name: {{ item }}`,
   `flatpak_repo_url: {{ dotfiles_flatpak_remotes_manifest[item].url }}`,
   `state: present`, `method: system`, `become: true`. Runs before installs.
2. `Install flatpak applications` — `community.general.flatpak`, loop over
   `dotfiles_pkgs_flatpak`, `name: {{ item.value.package }}`,
   `remote: {{ item.value.remote }}`, `state: present`, `method: system`,
   `become: true`, `loop_control.label: {{ item.value.package }}`.

### `.pre-commit-config.yaml`

Extend the hook's `files` regex to
`^ansible/vars/(packages|package-deps|repos|flatpak-remotes)\.json$` so
editing the remotes file runs the validator.

## Acceptance

- [x] `.bin/validate-manifest.py` exits 0 on the current manifests.
- [x] Negative tests (temp copies via `--packages`/`--flatpak-remotes` flags):
      flatpak entry with unknown remote id, missing `package`, missing
      `remote`, and a malformed remotes file each fail with one precise error.
- [x] `pre-commit run --all-files` green; touching
      `ansible/vars/flatpak-remotes.json` alone triggers the hook.
- [x] `ansible-playbook --check --diff --skip-tags packages` parses clean
      (syntax + var wiring; no flatpak entries selected yet, so the new
      tasks no-op and the apt bootstrap is skipped).
- [x] `pre-commit` hook triggers when `ansible/vars/flatpak-remotes.json` is
      edited, and `packages.schema.json` remains valid JSON with
      `packages.json`'s `$schema` pointer resolving against it.
