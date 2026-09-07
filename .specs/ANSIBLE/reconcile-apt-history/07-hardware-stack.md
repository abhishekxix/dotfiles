# 07 — hardware/driver stack, workstation

- **Files:** `ansible/vars/packages.json` (EDIT)
- **Changes:** Add eight workstation apt entries: `firmware-misc-nonfree`,
  `linux-headers-amd64`, `nvidia-driver`, `nvidia-kernel-dkms`,
  `nvidia-xconfig`, `nvtop`, `v4l2loopback-dkms`, `v4l2loopback-utils`.
  User decision: include the full driver stack (non-free components enabled;
  localhost inventory = this machine).
- **Acceptance:**
  - [ ] `jq -e 'keys == (keys | sort)' ansible/vars/packages.json` passes.
  - [ ] All eight keys present with `profiles: ["workstation"]`.
  - [ ] Playbook check-mode parse clean (manifest validation green).
