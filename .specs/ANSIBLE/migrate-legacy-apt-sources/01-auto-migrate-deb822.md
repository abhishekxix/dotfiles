# 01 — Auto-migrate legacy-only default-mirror sources, keep fail-fast elsewhere

| Field | Value |
|---|---|
| Status | In progress |
| Step | 01 |
| Commit | `ANSIBLE(01): auto-migrate legacy one-line apt sources to deb822` |

## Files

- `ansible/tasks/components.yml` (EDIT — migration block + split asserts)
- `ansible/tasks/packages.yml` (EDIT — one-line `cache_valid_time` change)

## Changes

In `components.yml`, between the stat task and the slurp task:

1. Keep `Check apt source files` as-is.
2. NEW `Read legacy sources.list` — `ansible.builtin.slurp`
   (`check_mode: false`),
   `when: dotfiles_sources_stat.results[0].stat.exists and not
   dotfiles_sources_stat.results[1].stat.exists`.
3. NEW `Extract legacy mirror URIs` — `ansible.builtin.set_fact` running

   ```
   (?m)^\s*deb(?:-src)?(?:\s+\[[^\]]*\])?\s+(\S+)
   ```

   via `ansible.builtin.regex_findall` over the decoded content →
   `dotfiles_legacy_uris` (empty list when the file has only comments;
   `cdrom:` lines are captured whole because their bracket is part of the
   URI token).
4. NEW `Fail fast on custom apt mirrors` — assert every entry of
   `dotfiles_legacy_uris` matches
   `^https?://(deb\.debian\.org|security\.debian\.org)/`; fail message =
   the existing actionable text, extended with "non-default mirror
   detected in /etc/apt/sources.list; migrate to deb822 manually".
5. NEW `Migrate legacy sources.list to deb822` block —
   `when: legacy exists and deb822 absent and mirror gate passed`:
   - `ansible.builtin.copy` (become, mode 0644) canonical deb822 content to
     `/etc/apt/sources.list.d/debian.sources` — two stanzas:

     ```
     Types: deb
     URIs: http://deb.debian.org/debian
     Suites: {{ ansible_facts.distribution_release }} {{ ansible_facts.distribution_release }}-updates
     Components: {{ dotfiles_apt_components }}
     Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

     Types: deb
     URIs: http://deb.debian.org/debian-security
     Suites: {{ ansible_facts.distribution_release }}-security
     Components: {{ dotfiles_apt_components }}
     Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
     ```

     register `dotfiles_sources_migrated`.
   - `ansible.builtin.command: mv /etc/apt/sources.list
     /etc/apt/sources.list.bak-{{ ansible_date_time.iso8601_basic_micro }}`
     (become, `creates:` the backup path).
   - `rescue`: move the backup back, `ansible.builtin.file state=absent`
     the generated `debian.sources`, then `ansible.builtin.fail` with a
     message pointing at the backup.
   - inside the block, `ansible.builtin.apt: update_cache=true` (become)
     validates the new sources while the rescue path is still available.
6. REPLACE the single `Fail fast on legacy-only apt sources` assert with
   two `when`-split asserts on `dotfiles_sources_stat.results[1].stat.exists`:
   - legacy present (gate refused) → existing manual-migration message;
   - legacy absent too → new "no apt sources found at all" message.
7. Slurp, `Components:` assert, and normalization task unchanged.

In `packages.yml`, `Update APT package metadata` line becomes:

```yaml
cache_valid_time: "{{ 0 if (dotfiles_components_result.changed | default(false) or dotfiles_sources_migrated.changed | default(false)) else 3600 }}"
```

Without this, a migrated host's normalization is a no-op and the
migration's own validation update (<1h old) would suppress the post-repos
refresh — third-party indexes would never be fetched on first run.

## Acceptance

- [ ] `ansible-playbook --syntax-check ansible/playbook.yml` passes.
- [ ] Jinja URI extraction verified via an ad-hoc `localhost` `set_fact`
      probe against fixture contents: default one-liner, options-bracket
      one-liner, `cdrom:` line, comments-only file.
- [ ] This host (`debian.sources` present): `--check --tags packages` run
      proceeds past all migration/assert tasks unchanged and stops only at
      the known sudo wall on the become tasks.
- [ ] Fresh-container simulation (`docker run debian:trixie` with a legacy
      `deb.debian.org` one-liner): migration writes canonical
      `debian.sources`, legacy file moved to `.bak-*`, `apt-get update`
      succeeds; second run reports no changes (idempotent).
- [ ] Fresh-container simulation with a non-default mirror URI: run fails
      fast with the manual-migration message; no files touched.
- [ ] Fresh-container simulation with no sources at all: fails with the
      "no apt sources found" message.
- [ ] `.bin/validate-manifest.py` and `pre-commit run --all-files` green.
