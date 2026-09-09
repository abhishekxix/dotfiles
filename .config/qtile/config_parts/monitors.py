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
# A physically unplugged output can keep stale geometry on its
# `disconnected` line; treat that as still-live so the framebuffer is
# shrunk and qtile converges to one screen.
# (Single xrandr --off does NOT stick on NVIDIA: the driver re-adds the
# output ~1s later, and a second --off corrupts the panning domain — so we
# never emit --off; shrinking the framebuffer is the whole fix.)
_STALE_GEOM_RE = re.compile(r"^(\S+) disconnected (\d+x\d+)\+(\d+)\+(\d+)")
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


def stale_outputs(lines=None):
    """Unplugged outputs still holding framebuffer geometry.

    Returns {name: (mode, x, y)} — treated as live for framebuffer sizing
    (see _STALE_GEOM_RE note above)."""
    lines = lines if lines is not None else _run_xrandr_query()
    out = {}
    for line in lines:
        m = _STALE_GEOM_RE.match(line)
        if m:
            out[m.group(1)] = (m.group(2), m.group(3), m.group(4))
    return out


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
    stale = stale_outputs(lines)
    if stale:
        # Unplugged-but-mapped outputs keep the framebuffer wide; shrink it
        # to the internal panel so X reports one screen and qtile converges.
        desired["__fb__"] = ("--fb", internal)
    pref = preferred_mode_and_max_rate(internal, lines)
    if pref:
        desired[internal] = ("--primary", pref[0], pref[1])
    for ext in externals:
        pref = preferred_mode_and_max_rate(ext, lines)
        if pref:
            desired[ext] = ("--left-of", internal, pref[0], pref[1])
        else:
            desired[ext] = ("--auto-left-of", internal)

    # Shrink the framebuffer to the internal panel's preferred mode when a
    # stale output keeps it wide; skip when already solo-sized (hook loops).
    if "__fb__" in desired:
        m = re.search(r"current (\d+) x (\d+)", lines[0] if lines else "")
        want = preferred_mode_and_max_rate(internal, lines)
        if want and not m:
            del desired["__fb__"]
        elif want and (m.group(1), m.group(2)) == tuple(want[0].split("x")):
            del desired["__fb__"]
    # No-op when everything already matches (--fb has no mode to compare).
    for output, spec in list(desired.items()):
        if spec[0] == "--fb":
            continue
        cur = current_mode(output, lines)
        want_mode, want_rate = spec[-2], spec[-1]
        if isinstance(want_mode, str) and want_mode.startswith("--"):
            continue  # --auto fallback: can't compare, always apply
        if cur == (want_mode, want_rate):
            del desired[output]
    return desired


def configure_monitors():
    """Apply the plan via xrandr. True only if a command SUCCEEDED.

    A failed xrandr (e.g. --fb rejected while an output is still mapped)
    reports False so the hook falls through to group placement instead of
    early-returning on a lie every event (tight xrandr-fail loop, no converge).
    """
    lines = _run_xrandr_query()
    desired = plan(lines)
    if not desired:
        return False
    changed = False
    for output, spec in desired.items():
        if spec[0] == "--primary":
            _, mode, rate = spec
            res = subprocess.run(
                ["xrandr", "--output", output, "--primary",
                 "--mode", mode, "--rate", str(rate)],
                check=False,
            )
        elif spec[0] == "--fb":
            mode = preferred_mode_and_max_rate(spec[1], lines)
            if not mode:
                continue
            res = subprocess.run(["xrandr", "--fb", mode[0]], check=False)
            continue
        elif spec[0] == "--left-of":
            _, anchor, mode, rate = spec
            res = subprocess.run(
                ["xrandr", "--output", output, "--auto",
                 "--mode", mode, "--rate", str(rate),
                 "--left-of", anchor],
                check=False,
            )
        else:  # --auto-left-of fallback
            _, anchor = spec
            res = subprocess.run(
                ["xrandr", "--output", output, "--auto",
                 "--left-of", anchor],
                check=False,
            )
        changed = changed or res.returncode == 0
    return changed


_DUAL_Q = """Screen 0: minimum 8 x 8, current 4480 x 1440, maximum 32767 x 32767
HDMI-0 connected 2560x1440+0+0 (normal left inverted right x axis y axis) 698mm x 392mm
   2560x1440     59.95 +  74.96*
eDP-1-1 connected primary 1920x1080+2560+0 (normal left inverted right x axis y axis) 344mm x 194mm
   1920x1080    120.04*+  48.01""".splitlines()

_BROKEN_SOLO_Q = """Screen 0: minimum 8 x 8, current 4480 x 1440, maximum 32767 x 32767
HDMI-0 disconnected 2560x1440+0+0 (normal left inverted right x axis y axis) 0mm x 0mm
   2560x1440     59.95 +  74.96*
eDP-1-1 connected primary 1920x1080+2560+360 (normal left inverted right x axis y axis) 344mm x 194mm
   1920x1080    120.04*+  48.01""".splitlines()

_FIXED_SOLO_Q = """Screen 0: minimum 8 x 8, current 1920 x 1080, maximum 32767 x 32767
HDMI-0 disconnected (normal left inverted right x axis y axis)
eDP-1-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 344mm x 194mm
   1920x1080    120.04*+  48.01""".splitlines()


def _selfcheck():
    # ponytail: one runnable check — canned queries, no hardware needed.
    assert plan(_DUAL_Q) == {}, plan(_DUAL_Q)
    assert plan(_FIXED_SOLO_Q) == {}, plan(_FIXED_SOLO_Q)
    got = plan(_BROKEN_SOLO_Q)
    assert got == {"__fb__": ("--fb", "eDP-1-1")}, got  # never --off
    assert all(s[0] != "--off" for s in got.values())

    class _R:
        def __init__(self, rc, out=""):
            self.returncode = rc
            self.stdout = out

    import unittest.mock as _mock

    with _mock.patch.object(
        subprocess, "run", return_value=_R(1, "\n".join(_BROKEN_SOLO_Q))
    ):
        assert configure_monitors() is False  # fb rejected → not "changed"
    with _mock.patch.object(
        subprocess, "run", return_value=_R(0, "\n".join(_FIXED_SOLO_Q))
    ):
        assert configure_monitors() is False  # plan empty → no-op
    print("selfcheck ok: dual/fixed no-op, broken→fb-only, rc-aware")


if __name__ == "__main__":
    import sys as _sys

    if _sys.argv[1:] == ["--selfcheck"]:
        _selfcheck()
    else:
        print("changed" if configure_monitors() else "no-op")
