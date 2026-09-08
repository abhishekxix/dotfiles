# 01 — Normalize deb822 components, guard legacy sources

| Field | Value |
|---|---|
| Status | In progress |
| Step | 01 |
| Commit | `ANSIBLE(01): ensure non-free components in deb822 apt sources` |

## Files

- `ansible/tasks/components.yml` (CREATE — component normalization)
- `ansible/playbook.yml` (EDIT — import + vars)
- `ansible/tasks/packages.yml` (EDIT — conditional `cache_valid_time`)

## Changes

### `playbook.yml` vars

```yaml
dotfiles_apt_components: main contrib non-free non-free-firmware
```

### `tasks/components.yml` (new)

Imported in `playbook.yml` between preflight and repos, tagged `packages`:

1. `Check for legacy one-line apt sources` — `ansible.builtin.stat` on
   `/etc/apt/sources.list` and on `/etc/apt/sources.list.d/debian.sources`.
2. `Fail fast on legacy-only apt sources` — `assert` that
   `debian.sources` exists; fail message tells the user to migrate to deb822
   (trixie default) or add the components manually. A present *legacy* file
   alongside `debian.sources` (upgraded systems) is allowed — deb822 is
   normalized, legacy is left untouched.
3. `Require Components stanzas in debian.sources` — slurp the file and
   assert it contains `Components:` (a file without any would make step 4 a
   silent no-op).
4. `Normalize apt source components` — `become: true`,
   `ansible.builtin.replace`:
   - `path: /etc/apt/sources.list.d/debian.sources`
   - `regexp: '^Components: (?!{{ dotfiles_apt_components | regex_escape }}$).+$'`
     (negative lookahead → the target line never matches → idempotent)
   - `replace: 'Components: {{ dotfiles_apt_components }}'`
   - register `dotfiles_components_result`.
   All `Components:` lines (repo, security, updates, backports stanzas) are
   normalized to the same set — safe per the overview (security serves all
   four).

### `tasks/packages.yml`

`Update APT package metadata` drops its static `cache_valid_time: 3600` for a
conditional one so a component change forces a real refresh even when the
lists are minutes old:

```yaml
cache_valid_time: "{{ 0 if (dotfiles_components_result.changed | default(false)) else 3600 }}"
```

(`update_cache: true` stays; registered vars from the earlier import are in
scope for the whole play.) Third-party repos from `tasks/repos.yml` are still
added *before* this update runs, so first-run index fetches stay correct.

## Acceptance

- [x] `ansible-playbook --check --diff --skip-tags packages` parses clean;
      the guard tasks pass on this host (the `become` replace itself hits the
      interactive-sudo wall in this environment, so its no-change behavior
      was verified via a temp copy of this host's `debian.sources` — no
      change, as expected).
- [x] Fresh-host simulation: temp copy with
      `Components: main contrib non-free-firmware` normalized by the real
      `ansible.builtin.replace` module →
      `Components: main contrib non-free non-free-firmware`; second run
      changes nothing (idempotency).
- [x] Legacy guard: stat/assert replica with only `sources.list` fails with
      the actionable deb822 message.
- [x] `.bin/validate-manifest.py` and `pre-commit run --all-files` green.
- [ ] On a fresh Debian trixie VM/container (user-run): playbook converges —
      fonts-ubuntu/nvidia resolve, the flatpak tasks install
      `org.kde.okular` + `md.obsidian.Obsidian` from flathub — closing the
      pending flatpak-install-source step-02 acceptance.
