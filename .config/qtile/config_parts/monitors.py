"""Dynamic monitor configuration.

Parses `xrandr --query` and applies: internal panel as `--primary` at its
preferred mode + max rate; external outputs at preferred mode + max rate,
positioned left of the internal panel. Idempotent — no-ops when the current
state already matches (avoids `screen_change` hook loops).
"""

import re
import subprocess

_INTERNAL_RE = re.compile(r"^(eDP|LVDS)", re.IGNORECASE)
_EXTERNAL_RE = re.compile(r"^(HDMI|DP|DisplayPort)", re.IGNORECASE)
_CONNECTED_RE = re.compile(r"^(\S+) connected")
# e.g. "   2560x1440     59.95 +  74.96* " — preferred mode carries the +.
_MODE_RE = re.compile(r"^\s+(\d+x\d+)\s+([\d.\s*+]+)")


def _run_xrandr_query():
    out = subprocess.run(
        ["xrandr", "--query"], capture_output=True, text=True
    ).stdout
    return out.splitlines()


def connected_outputs(lines=None):
    """Names of connected outputs, internal first."""
    lines = lines if lines is not None else _run_xrandr_query()
    names = [m.group(1) for line in lines if (m := _CONNECTED_RE.match(line))]
    return sorted(names, key=lambda n: 0 if _INTERNAL_RE.match(n) else 1)


def internal_output(names):
    for n in names:
        if _INTERNAL_RE.match(n):
            return n
    return names[0] if names else None


def external_outputs(names):
    return [n for n in names if _EXTERNAL_RE.match(n)]


def preferred_mode_and_max_rate(output, lines=None):
    """(mode, max_rate) for the preferred (+) mode of output, else None."""
    lines = lines if lines is not None else _run_xrandr_query()
    in_block = False
    for line in lines:
        if not line.startswith(" "):
            in_block = line.split()[0] == output if line.strip() else False
            continue
        if not in_block:
            continue
        m = _MODE_RE.match(line)
        if m and "+" in m.group(2):
            rates = [float(r.strip("*+")) for r in m.group(2).split() if r.strip("*+")]
            return m.group(1), max(rates)
    return None


def current_mode(output, lines=None):
    """Currently active (mode, rate) of output, else None."""
    lines = lines if lines is not None else _run_xrandr_query()
    m = re.search(
        rf"^{re.escape(output)} connected(?: primary)? (\d+x\d+)\+",
        "\n".join(lines),
        re.MULTILINE,
    )
    if not m:
        return None
    # Find the active (*) rate on that mode line.
    in_block = False
    for line in lines:
        if not line.startswith(" "):
            in_block = line.split()[0] == output if line.strip() else False
            continue
        if in_block and line.strip().startswith(m.group(1)):
            rates = [r for r in line.split()[1:] if "*" in r]
            if rates:
                return m.group(1), float(rates[0].strip("*+"))
    return None


def plan(lines=None):
    """Desired xrandr args per output, or {} when state already matches."""
    lines = lines if lines is not None else _run_xrandr_query()
    names = connected_outputs(lines)
    if not names:
        return {}
    internal = internal_output(names)
    externals = external_outputs(names)
    if internal in externals:
        externals.remove(internal)

    desired = {}
    pref = preferred_mode_and_max_rate(internal, lines)
    if pref:
        desired[internal] = ("--primary", pref[0], pref[1])
    for ext in externals:
        pref = preferred_mode_and_max_rate(ext, lines)
        if pref:
            desired[ext] = ("--left-of", internal, pref[0], pref[1])
        else:
            desired[ext] = ("--auto-left-of", internal)

    # No-op when everything already matches.
    for output, spec in list(desired.items()):
        cur = current_mode(output, lines)
        want_mode, want_rate = spec[-2], spec[-1]
        if isinstance(want_mode, str) and want_mode.startswith("--"):
            continue  # --auto fallback: can't compare, always apply
        if cur == (want_mode, want_rate):
            del desired[output]
    return desired


def configure_monitors():
    """Apply the plan via xrandr. Returns True if anything changed."""
    desired = plan()
    if not desired:
        return False
    for output, spec in desired.items():
        if spec[0] == "--primary":
            _, mode, rate = spec
            subprocess.run(
                ["xrandr", "--output", output, "--primary",
                 "--mode", mode, "--rate", str(rate)],
                check=False,
            )
        elif spec[0] == "--left-of":
            _, anchor, mode, rate = spec
            subprocess.run(
                ["xrandr", "--output", output, "--auto",
                 "--mode", mode, "--rate", str(rate),
                 "--left-of", anchor],
                check=False,
            )
        else:  # --auto-left-of fallback
            _, anchor = spec
            subprocess.run(
                ["xrandr", "--output", output, "--auto",
                 "--left-of", anchor],
                check=False,
            )
    return True


if __name__ == "__main__":
    changed = configure_monitors()
    print("changed" if changed else "no-op")
