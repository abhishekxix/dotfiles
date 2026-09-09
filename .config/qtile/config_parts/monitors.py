"""Dynamic monitor configuration.

Parses `xrandr --query` and applies: internal panel as `--primary` at its
preferred mode + max rate; external outputs at preferred mode + max rate,
positioned left of the internal panel, bottom-aligned via explicit `--pos`
(the external here is 1440px tall vs the 1080px panel, so `--left-of`
top-aligns and the bar/wallpaper seam splits — absolute positions fix that).
Idempotent — no-ops when the current state already matches (avoids
`screen_change` hook loops). One xrandr call per configure.
"""

import re
import subprocess

_INTERNAL_RE = re.compile(r"^(eDP|LVDS)", re.IGNORECASE)
_EXTERNAL_RE = re.compile(r"^(HDMI|DP|DisplayPort)", re.IGNORECASE)
_CONNECTED_RE = re.compile(r"^(\S+) connected")
# A physically unplugged output can keep geometry on its `disconnected`
# line; treat that as still-live ONLY when it carries no real EDID (a
# live-but-cache-stale output reports a full EDID block — see _has_edid).
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


def stale_outputs(lines=None, verbose=None):
    """Unplugged outputs still holding framebuffer geometry.

    Returns {name: (mode, x, y)} — treated as live for framebuffer sizing
    (see _STALE_GEOM_RE note above). Skips outputs whose EDID block is a
    full read (live-but-cache-stale after a reseat; the kernel just hasn't
    flipped the word yet) — those converge on their own via --auto.
    `verbose` is `xrandr --verbose` text (queried lazily when omitted)."""
    lines = lines if lines is not None else _run_xrandr_query()
    out = {}
    for line in lines:
        m = _STALE_GEOM_RE.match(line)
        if m and not _has_edid(m.group(1), verbose):
            out[m.group(1)] = (m.group(2), m.group(3), m.group(4))
    return out


def _has_edid(output, verbose=None):
    """True when `xrandr --verbose` shows a full (>=128B) EDID for output."""
    if verbose is None:
        try:
            out = subprocess.run(
                ["xrandr", "--verbose"], capture_output=True, text=True
            ).stdout
        except Exception:
            return False
        verbose = out.splitlines()
    in_block, in_edid, hexlen = False, False, 0
    for line in verbose:
        stripped = line.strip()
        if not line.startswith((" ", "\t")):
            if in_block and in_edid:
                break
            in_block = stripped.split()[0] == output if stripped else False
            in_edid, hexlen = False, 0
            continue
        if not in_block:
            continue
        if stripped.startswith("EDID:"):
            in_edid = True
            hexlen += len("".join(stripped.split()[1:]))
            continue
        if in_edid:
            tok = stripped.split()
            if tok and re.fullmatch(r"[0-9a-fA-F]+", tok[0]):
                hexlen += len(tok[0])
            else:
                break  # end of EDID hex dump
    return hexlen >= 256  # 128 bytes hex-encoded


def internal_output(names):
    for n in names:
        if _INTERNAL_RE.match(n):
            return n
    return names[0] if names else None


def external_outputs(names):
    return [n for n in names if _EXTERNAL_RE.match(n)]


def _wh(mode):
    """(w, h) ints from a WxH mode string, else (None, None)."""
    try:
        w, h = mode.split("x")
        return int(w), int(h)
    except (ValueError, AttributeError):
        return None, None


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


def current_pos(output, lines=None):
    """Current (x, y) origin of output, else None."""
    lines = lines if lines is not None else _run_xrandr_query()
    m = re.search(
        rf"^{re.escape(output)} connected(?: primary)? \d+x\d+\+(\d+)\+(\d+)",
        "\n".join(lines),
        re.MULTILINE,
    )
    return (int(m.group(1)), int(m.group(2))) if m else None


def current_rects(lines=None):
    """[(name, x, y, w, h)] per connected output, in `xrandr --listmonitors`
    order (CRTC order — panel first here). This is the order qtile itself
    enumerates screens in, so config screens[i] must be built to match it
    (see build_screens): sort-by-x would put the external first and swap
    the bars onto the wrong outputs."""
    if lines is None:
        try:
            out = subprocess.run(
                ["xrandr", "--listmonitors"], capture_output=True, text=True
            ).stdout
        except Exception:
            return []
        lines = out.splitlines()
        rects = []
        for line in lines:
            m = re.match(r"^\s*\d+:\s+\S+\s+(\d+)/\S+x(\d+)/\S+\+(\d+)\+(\d+)\s+(\S+)", line)
            if m:
                w, h, x, y, name = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), m.group(5)
                rects.append((name, x, y, w, h))
        return rects
    rects = []
    for line in lines:
        m = re.match(
            r"^(\S+) connected(?: primary)? (\d+)x(\d+)\+(\d+)\+(\d+)", line
        )
        if m:
            name, w, h, x, y = m.group(1), *(int(g) for g in m.groups()[1:])
            rects.append((name, x, y, w, h))
    # Canned --query text has no CRTC order; sort by x for determinism.
    return sorted(rects, key=lambda r: (r[1], r[2]))


def plan(lines=None, verbose=None):
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
    stale = stale_outputs(lines, verbose)
    if stale:
        # Unplugged-but-mapped outputs keep the framebuffer wide; shrink it
        # to the internal panel so X reports one screen and qtile converges.
        desired["__fb__"] = ("--fb", internal)
    internal_pref = preferred_mode_and_max_rate(internal, lines)
    internal_w, internal_h = _wh(internal_pref[0]) if internal_pref else (None, None)
    # Bottom-align: tallest output's top is y=0, shorter ones shift down.
    ext_prefs = {e: preferred_mode_and_max_rate(e, lines) for e in externals}
    heights = [internal_h or 0] + [
        (_wh(p[0])[1] or 0) for p in ext_prefs.values() if p
    ]
    top = max(heights) if heights else 0
    x = 0
    for ext in externals:
        pref = ext_prefs[ext]
        if pref:
            ew, eh = _wh(pref[0])
            # Bottom-align against the tallest output.
            y = max(0, top - (eh or 0))
            desired[ext] = ("--pos-external", x, y, pref[0], pref[1])
            x += ew or 0
        else:
            desired[ext] = ("--auto-left-of", internal)
    if internal_pref:
        # Primary sits right of the externals, bottoms aligned.
        y = max(0, top - (internal_h or 0))
        desired[internal] = ("--primary", internal_pref[0], internal_pref[1], x, y)
        _ = internal_w  # width unused; x tracks the externals' total width

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
        if spec[0] == "--auto-left-of":
            continue  # --auto fallback: can't compare, always apply
        if spec[0] == "--primary":
            _, want_mode, want_rate, want_x, want_y = spec
        else:  # --pos-external
            _, want_x, want_y, want_mode, want_rate = spec
        if current_mode(output, lines) == (want_mode, want_rate) and current_pos(
            output, lines
        ) == (want_x, want_y):
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
    cmd = ["xrandr"]
    if "__fb__" in desired:
        # Shrink rides in the same call: it matches the post-move layout
        # (solo internal at 0x0), so one atomic xrandr applies both.
        mode = preferred_mode_and_max_rate(desired.pop("__fb__")[1], lines)
        if mode:
            cmd += ["--fb", mode[0]]
    for output, spec in desired.items():
        if spec[0] == "--primary":
            _, mode, rate, x, y = spec
            cmd += [
                "--output", output, "--primary",
                "--mode", mode, "--rate", str(rate),
                "--pos", f"{x}x{y}",
            ]
        elif spec[0] == "--pos-external":
            _, x, y, mode, rate = spec
            cmd += [
                "--output", output, "--auto",
                "--mode", mode, "--rate", str(rate),
                "--pos", f"{x}x{y}",
            ]
        else:  # --auto-left-of fallback
            _, anchor = spec
            cmd += ["--output", output, "--auto", "--left-of", anchor]
    return subprocess.run(cmd, check=False).returncode == 0


_DUAL_Q = """Screen 0: minimum 8 x 8, current 4480 x 1440, maximum 32767 x 32767
HDMI-0 connected 2560x1440+0+0 (normal left inverted right x axis y axis) 698mm x 392mm
   2560x1440     59.95 +  74.96*
eDP-1-1 connected primary 1920x1080+2560+360 (normal left inverted right x axis y axis) 344mm x 194mm
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


_LIVE_BUT_STALE_Q = """Screen 0: minimum 8 x 8, current 4480 x 1440, maximum 32767 x 32767
HDMI-0 disconnected 2560x1440+0+0 (normal left inverted right x axis y axis) 698mm x 392mm
   2560x1440     59.95 +  74.96*
eDP-1-1 connected primary 1920x1080+2560+0 (normal left inverted right x axis y axis) 344mm x 194mm
   1920x1080    120.04*+  48.01""".splitlines()

_LIVE_BUT_STALE_V = """HDMI-0 disconnected (normal left inverted right x axis y axis)
\t\tEDID:
\t\t\t00ffffffffffff001e6d955bb12e0800
\t\t\t0522010380462778ea9fd1a2574c9c24
\t\t\t0c5054256b807140818081c0a9c0b300
\t\t\td1c08100d1cf565e00a0a0a029503020
\t\t\t3500ba882100001a000000fd00304b1e
\t\t\t701f010a202020202020000000fc004c
\t\t\t4720484452205148440a2020000000ff
\t\t\t003430354e54545146533234310a0147
\t\tCTM: \t1.000000 0.000000 0.000000
eDP-1-1 connected primary 1920x1080+2560+0 (normal left inverted right x axis y axis) 344mm x 194mm""".splitlines()


def _selfcheck():
    # ponytail: one runnable check — canned queries, no hardware needed.
    assert plan(_DUAL_Q) == {}, plan(_DUAL_Q)
    assert plan(_FIXED_SOLO_Q) == {}, plan(_FIXED_SOLO_Q)
    # Bottom-aligned: 1440px external at y=0, 1080px panel shifted to y=360.
    got = plan(_DUAL_Q)
    _ = got  # no-op above; positions asserted via the misaligned case below
    mis = [l.replace("+2560+360", "+2560+0") for l in _DUAL_Q]
    got = plan(mis)
    assert got == {
        "eDP-1-1": ("--primary", "1920x1080", 120.04, 2560, 360),
    }, got
    got = plan(_BROKEN_SOLO_Q, [])
    assert got == {
        "__fb__": ("--fb", "eDP-1-1"),
        "eDP-1-1": ("--primary", "1920x1080", 120.04, 0, 0),
    }, got  # never --off; fb shrink + panel move to 0x0, one call
    assert all(s[0] != "--off" for s in got.values())
    # Live-but-cache-stale (reseat fixed EDID, kernel word not flipped):
    # no --fb shrink, converges via --auto instead.
    assert stale_outputs(_LIVE_BUT_STALE_Q, _LIVE_BUT_STALE_V) == {}
    assert stale_outputs(_BROKEN_SOLO_Q, []) == {
        "HDMI-0": ("2560x1440", "0", "0")
    }

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
