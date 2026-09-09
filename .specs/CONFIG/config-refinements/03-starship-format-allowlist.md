# 03 — Starship format allowlist + prompt signal

| Field | Value |
|---|---|
| Status | Planning |
| Step | 03 |
| Commit | `CONFIG(03): starship format allowlist, drop slow modules, add status signal` |

## Files

- `.config/starship.toml` (EDIT)

## Changes

1. Add an explicit minimal `format` string — only the modules actually read:
   directory, git_branch/commit/status, language(s) in use, jobs,
   cmd_duration, status, line break, char. Without `format`, every default
   module's detection runs per prompt; the format line is an allowlist.
2. Disable `git_metrics` (line 63–64) and `sudo` (line 150–151) — both are
   explicitly enabled today and are slow/noisy.
3. Add the missing `status` / `jobs` / `cmd_duration` signal (failing
   commands, long commands, and background jobs are invisible today).
4. Keep all existing symbol stanzas untouched — no restyling.

## Test

- `starship timings` before/after in a big repo (prompt render measurably faster).
- Run a failing command (nonzero status shows), a long command (duration
  shows), and a background job (jobs indicator shows).

## Acceptance

- [ ] prompt render measurably faster in large repos
- [ ] exit-code / duration / jobs all visible in the prompt
