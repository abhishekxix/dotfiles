# 02 — Apt repos file

| Field | Value |
|---|---|
| Status | Done |
| Step | 02 |
| Commit | `INSTALLER(02): add repos.json and apt key-repo tasks` |

## Files

- `ansible/vars/repos.json` (CREATE)
- `ansible/playbook.yml` (CREATE — repo tasks only; package installs land in step 03)

## Changes

Separate repos file for the Docker-engine / VSCode pattern: add third-party
signing key + `sources.list.d` entry idempotently, then plain `apt` packages
reference it via `"repo": "<id>"` in `packages.json` (schema from step 01).

```json
{
  "docker": {
    "key_url": "https://download.docker.com/linux/debian/gpg",
    "keyring": "/usr/share/keyrings/docker-archive-keyring.gpg",
    "repo": "deb [arch=@ARCH@ signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian @RELEASE@ stable"
  },
  "vscode": {
    "key_url": "https://packages.microsoft.com/keys/microsoft.asc",
    "keyring": "/usr/share/keyrings/packages.microsoft.gpg",
    "repo": "deb [arch=@ARCH@ signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main"
  }
}
```

(`@ARCH@` is the Debian apt arch name (`amd64` / `arm64`) and `@RELEASE@`
the release codename. The playbook maps `ansible_facts.architecture`
(`x86_64` / `aarch64`) to the Debian arch via `dotfiles_deb_arch` before
expanding the placeholders — never template the raw kernel name into the
line. Placeholders are deliberately non-Jinja literals so no whitespace
variant can break the replacement.)

Field rules:

- `key_url`: https URL of the ASCII-armored signing key.
- `keyring`: absolute path under `/usr/share/keyrings/` where the dearmored
  key lives. `signed-by=` in `repo` must point at the same path.
- `repo`: full `deb [...] ...` line; may use Ansible facts. The arch
  placeholder must expand to the Debian arch name (`amd64`/`arm64`), i.e. the
  playbook maps `ansible_facts.architecture` (`x86_64`/`aarch64`) first —
  never template the raw kernel name into the line.
- An entry with no `key_url` (plain PPA-style line or local repo) is allowed:
  omit the field and the key task skips it.

Playbook behavior (Debian stable only, `become: true`):

1. Load `repos.json`. Compute the set of repo ids referenced by the
   profile-selected `packages.json` entries with `source == "apt"` and a
   `repo` field.
2. Healing first, before every `apt` invocation: remove a foreign
   `/etc/apt/sources.list.d/<id>.sources` deb822 twin, then own the exact
   content of `/etc/apt/sources.list.d/<id>.list` with `copy`. apt parses
   all of sources.list.d on startup, so a drifted host (vendor installers
   like docker's `docker.asc` entry or Microsoft's `vscode.sources`, or
   lines left by older manifest formats) fails every apt task — even
   `update_cache` in the prerequisites step — with "Conflicting values set
   for option Signed-By" until healed. `apt_repository` is deliberately
   not used: it only appends its line and never removes foreign ones.
   Content-owned `copy` overwrites that drift while a matching file stays
   `ok`. Skip unreferenced repos entirely — selecting profile `server`
   must not add workstation-only repos.
3. Install keyring prerequisites (`gnupg`, `ca-certificates`) with no
   `update_cache`: on a fresh host the `.list` files already reference
   keyrings that don't exist until dearmor runs, so an earlier index
   refresh would abort with "repository is not signed".
4. `get_url` key → dearmor into `keyring` (idempotent, mode `0644`).
5. `apt-get update` after any repo change, before any install (installs
   themselves are step 03). The update is gated on purge/key/copy change
   with `cache_valid_time` so clean re-runs stay `ok`.

## Acceptance

- [ ] `python3 -m json.tool ansible/vars/repos.json` exits 0.
- [ ] Dry run with profile `server` adds only repos referenced by
  server-selected entries: `ansible-playbook --check --diff` shows no
  workstation-only repo tasks as changed.
- [ ] Live check on Debian stable: repo tasks report ok/changed, then
  `apt-cache policy docker-ce` (or the seeded third-party package) shows the
  new repo as a candidate source.
- [ ] Re-run is idempotent: key + repo tasks report `ok`, never `changed`, on
  the second run.
