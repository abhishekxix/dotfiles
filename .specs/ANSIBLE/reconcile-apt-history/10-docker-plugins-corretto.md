# 10 — docker buildx/compose plugins + Corretto JDK 21 (packages1.txt check)

- **Files:** `ansible/vars/repos.json` (EDIT), `ansible/vars/packages.json` (EDIT)
- **Changes:**
  - From the user's `packages1.txt` (docker + corretto history): `ca-certificates`
    and `curl` are already tracked; `docker-ce` is tracked with
    `repo: docker`; `containerd.io` and `docker-ce-cli` are hard Depends of
    `docker-ce` (skip, implicit); `docker-buildx-plugin` and
    `docker-compose-plugin` are only Recommends of `docker-ce-cli` → declare
    explicitly: workstation+server apt entries with `repo: docker`.
  - Corretto JDK 21 (installed from apt.corretto.aws, which is configured on
    this machine but unmanaged): add a `corretto` key to `repos.json`
    (lexical position: first, before `docker`):

    ```json
    "corretto": {
      "key_url": "https://apt.corretto.aws/corretto.key",
      "keyring": "/usr/share/keyrings/corretto-keyring.gpg",
      "repo": "deb [arch=@ARCH@ signed-by=/usr/share/keyrings/corretto-keyring.gpg] https://apt.corretto.aws stable main"
    }
    ```

    Keyring path matches the machine's existing corretto.list `signed-by=`;
    `filename: corretto` in repos.yml:70 converges with the existing
    `/etc/apt/sources.list.d/corretto.list`.
  - Add package entry `java-21-amazon-corretto-jdk`
    (`profiles: [workstation, server]`, `repo: corretto`, `source: apt`;
    lexical position: between `iosevka-nerd-font` and `lxappearance`).
    `dotfiles_repos_selected` (playbook.yml:24) auto-activates the repo
    because the selected package references it.
- **Acceptance:**
  - [x] `jq -e 'keys == (keys | sort)'` passes for both vars files.
  - [x] `jq` shows docker-buildx-plugin/docker-compose-plugin (repo: docker)
        and java-21-amazon-corretto-jdk (repo: corretto), all
        workstation+server.
  - [x] `jq '.corretto' ansible/vars/repos.json` matches the block above.
  - [x] Playbook check-mode parse clean (repos + packages manifests validate).
