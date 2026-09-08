# 01 — build-essential in the toolchain bootstrap (always installed)

## Files

- `ansible/tasks/toolchain.yml` (EDIT)

## Changes

Insert between "Install rustup (cargo provider)" (`:12-20`) and "Check for
fnm":

```yaml
# build-essential is a toolchain like cargo/fnm/flatpak: always installed,
# regardless of manifest sources or profile. The cargo installs below ("Install
# fnm") and in packages.yml (crates) link with cc, which build-essential
# guarantees. It is chosen over bare gcc because gcc only Recommends libc6-dev
# while build-essential hard-Depends on it. No rc probe: apt state=present is
# idempotent (ok when present, installs when missing), matching the other
# toolchains' always-install rule.
- name: Install build tools (cargo linker)
  become: true
  ansible.builtin.apt:
    name: build-essential
    state: present
    update_cache: true
    cache_valid_time: 3600
  tags:
    - packages
```

- **No probe, no `when`** (user decision): build-essential is a toolchain
  and follows the always-install rule; the apt module's `state: present` is
  the only already-present skip. A `cc --version` probe was rejected — a
  clang-only host would skip and end up without gcc/g++/make.
- `update_cache: true` covers fresh hosts whose apt cache is still empty
  (same reasoning as the flatpak CLI task comment); `cache_valid_time`
  throttles it on subsequent runs.
- `become: true` — apt needs sudo, same as the flatpak CLI task.

## Acceptance

- [ ] `ansible-playbook --syntax-check ansible/playbook.yml` exits 0.
- [ ] Real run of the toolchain section on this host: "Install build tools
  (cargo linker)" evaluates unconditionally and reports ok / `changed=0`
  (build-essential already present); section finishes `changed=0` with
  every pre-existing guard intact.
  (Unconditional evaluation confirmed — the task runs and stops only at the
  sudo prompt, which this shell cannot answer. Ad-hoc equivalent to finish
  the check: `ansible localhost -c local --become -K -m ansible.builtin.apt
  -a 'name=build-essential state=present update_cache=true
  cache_valid_time=3600'` → expect SUCCESS / `changed=false`.)
- [ ] `ansible-playbook --check --diff --skip-tags packages` preview shows
  only the toolchain.yml change (no live-path effects).
