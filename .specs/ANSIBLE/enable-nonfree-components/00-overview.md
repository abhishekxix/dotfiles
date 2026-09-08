# Enable non-free apt components on fresh hosts

| Field | Value |
|---|---|
| Status | Planning |
| Component | ANSIBLE |
| Created | 2026-09-08 |

## Goal

Make the playbook self-sufficient on a fresh Debian stable host: apt sources
must carry every component the manifest needs (`main contrib non-free
non-free-firmware`), so entries like `fonts-ubuntu` (non-free) and
`ttf-mscorefonts-installer` (contrib) install without manual source editing.

## Context & Research

- Fresh Debian trixie installs default to components
  `main contrib non-free-firmware` (deb822 file
  `/etc/apt/sources.list.d/debian.sources`); plain `non-free` is absent.
- Manifest entries resolvable **only** via plain `non-free` (verified with
  `apt-cache policy` on the maintainer host): `fonts-ubuntu`, `nvidia-driver`,
  `nvidia-kernel-dkms`. `ttf-mscorefonts-installer` needs `contrib`;
  `firmware-misc-nonfree` needs `non-free-firmware` (both in the default set).
- Failure mode observed on a fresh VM: the alphabetical first unresolvable
  package is `fonts-ubuntu`, so the single apt transaction aborts with
  "No package matching 'fonts-ubuntu' is available" — before any flatpak work.
- Component resolution has a chicken-and-egg property: without the non-free
  index fetched, nothing can tell *which* package needs which component, so
  the playbook cannot enable components "on demand". They are a host-level
  requirement of this manifest and are normalized unconditionally.
- This host's `debian.sources` (all four stanzas, including `trixie-security`)
  already carries all four components, so normalization is a no-op here —
  idempotency must hold.
- Debian security suites serve all four components (confirmed by this host's
  working security stanza), so normalizing every `Components:` line in
  `debian.sources` — including the security stanza — is safe.
- `packages.yml`'s `Update APT package metadata` uses `cache_valid_time: 3600`;
  a host whose lists were refreshed <1h ago (e.g. by the just-failed run on a
  fresh VM) would skip the refresh and still miss the new components. The
  cache refresh must be forced whenever components actually changed.
- Legacy one-line `/etc/apt/sources.list` is not rewritten (regex-fragile,
  not present on trixie defaults — confirmed absent on the maintainer host);
  the playbook fails fast with an actionable message instead of silently
  doing nothing.

## Non-goals

- No rewriting of third-party `.list`/`.sources` files (docker, vscode,
  corretto, google-chrome) or of legacy `sources.list` deb lines.
- No per-package component derivation (impossible pre-index; see Context).
- No `apt-get update` inside the components task itself — the refresh is
  forced via the existing packages.yml task so it happens *after*
  `tasks/repos.yml` has added third-party sources (keeps first-run order
  correct: components → repos → one update).
- No support claims for pre-trixie releases (`non-free-firmware` component
  assumes trixie).

## Steps

- [ ] 01 — `01-deb822-components.md` — normalize deb822 components, guard
  legacy sources, force cache refresh on change
