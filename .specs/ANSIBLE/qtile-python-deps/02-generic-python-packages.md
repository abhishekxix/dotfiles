# 02 — generic python3-pip / python3-venv entries

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** Add two generic top-level apt packages (both profiles, matching
  `curl`/`git`), inserted in lexical position (between `picom` and `qtile`;
  `python3-pip` before `python3-venv`):

  ```json
  "python3-pip": {
    "package": "python3-pip",
    "profiles": [
      "workstation",
      "server"
    ],
    "source": "apt"
  },
  "python3-venv": {
    "package": "python3-venv",
    "profiles": [
      "workstation",
      "server"
    ],
    "source": "apt"
  },
  ```

  Note: no `python3-qtile-extras` entry — not packaged in Debian trixie
  (user decision, see 00-overview.md Non-goals).
- **Acceptance:**
  - [x] `jq 'keys' ansible/vars/packages.json` is sorted (verified with
        `jq -e '. == (. | sort)'`).
  - [x] `jq '.["python3-pip"], .["python3-venv"]' ansible/vars/packages.json`
        shows both entries with both profiles and `source: apt`.
  - [x] `ansible-playbook --check --skip-tags packages ansible/playbook.yml`
        parses cleanly — manifest validation tasks green (become tasks need an
        interactive sudo password, unrelated to this change).
