# 01 — CLI/dev tools, workstation+server

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** Add six apt entries (both profiles, matching bat/fzf/git
  convention): `fastfetch`, `gh`, `maven`, `ripgrep`, `shellcheck`, `tree`,
  each inserted in lexical position:

  ```json
  "<name>": { "package": "<name>", "profiles": ["workstation", "server"], "source": "apt" }
  ```
- **Acceptance:**
  - [x] `jq -e 'keys == (keys | sort)' ansible/vars/packages.json` passes.
  - [x] `jq -c '[.fastfetch,.gh,.maven,.ripgrep,.shellcheck,.tree] | map(.profiles)'`
        shows both profiles for all six.
  - [x] `ansible-playbook --check --skip-tags packages ansible/playbook.yml`
        parses cleanly (manifest validation green).
