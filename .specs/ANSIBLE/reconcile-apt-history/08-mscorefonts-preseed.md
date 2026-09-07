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
  - [ ] `jq '.["ttf-mscorefonts-installer"]' ansible/vars/packages.json` shows
        the workstation entry; `jq -e 'keys == (keys | sort)'` passes.
  - [ ] `ansible-playbook --check --tags packages ansible/playbook.yml` shows
        the preseed task listed before "Install apt packages"; check-mode
        parse clean.
  - [ ] Note in commit message: postinst downloads fonts from SourceForge at
        install time (needs network).
