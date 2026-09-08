# 08 — ttf-mscorefonts-installer + EULA preseed

- **Files:** `ansible/vars/packages.json` (EDIT),
  `ansible/tasks/packages.yml` (EDIT)
- **Changes:**
  - Add workstation apt entry `ttf-mscorefonts-installer` (contrib; component
    already enabled) in lexical position.
  - New task in `ansible/tasks/packages.yml`, placed immediately BEFORE the
    "Install apt packages" task, mirroring the docker-group conditional
    pattern (packages.yml:34-42):

    ```yaml
    - name: Preseed mscorefonts EULA acceptance
      become: true
      ansible.builtin.debconf:
        name: ttf-mscorefonts-installer
        question: msttcorefonts/accepted-mscorefonts-eula
        value: "true"
        vtype: boolean
      when: "'ttf-mscorefonts-installer' in dotfiles_pkgs_apt | map(attribute='value.package')"
      tags:
        - packages
    ```

  Without the preseed the postinst EULA prompt hangs/fails the
  non-interactive apt transaction.
- **Acceptance:**
  - [x] `jq '.["ttf-mscorefonts-installer"]' ansible/vars/packages.json` shows
        the workstation entry; `jq -e 'keys == (keys | sort)'` passes.
  - [x] `ansible-playbook --check --list-tasks` shows "Preseed mscorefonts
        EULA acceptance" (task 25) immediately before "Install apt packages"
        (task 26); check-mode parse clean.
  - [x] Note: postinst downloads fonts from SourceForge at install time
        (needs network).
