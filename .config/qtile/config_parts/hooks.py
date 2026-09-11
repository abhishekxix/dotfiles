"""Qtile hook subscriptions."""

import os
import subprocess

from libqtile import hook, qtile


@hook.subscribe.startup_once
def autostart():
    autostart_script = os.path.expanduser("~/.config/qtile/autostart.sh")
    # Fire-and-forget: don't block WM startup on slow xrandr/tray apps.
    subprocess.Popen([autostart_script])


# ponytail: re-entry lock only. An earlier 5s cooldown dropped the
# follow-up RandR event our own xrandr fires (same second), so placement +
# reload never ran after replug — the duplicated-bar glitch. configure is
# idempotent and reload fires only on screen-count change, so extra events
# are cheap no-ops, not loops.
_HOTPLUG_BUSY = False


@hook.subscribe.screen_change
def reconfigure_on_hotplug(event=None):
    """Apply monitor config, place groups, reload bars if screen count changed."""
    global _HOTPLUG_BUSY
    if _HOTPLUG_BUSY:
        return
    _HOTPLUG_BUSY = True
    try:
        _reconfigure_on_hotplug_inner()
    finally:
        _HOTPLUG_BUSY = False


def _repaint_wallpaper():
    """Re-run autostart's per-output --zoom paint (new framebuffer size)."""
    import shutil

    if shutil.which("xwallpaper") is None:
        return
    try:
        with open(os.path.expanduser("~/.xwallpaper")) as f:
            wallpaper = f.read().strip()
        if not wallpaper:
            return
        from config_parts.monitors import connected_outputs

        args = []
        for out in connected_outputs():
            args += ["--output", out, "--zoom", wallpaper]
        if args:
            # Fire-and-forget: never block the hook on painting.
            subprocess.Popen(["xwallpaper", *args])
    except Exception:
        pass


def _screen_index_for_rect(x, y, w, h):
    """Index into qtile.screens by geometry (CRTC order is arbitrary)."""
    try:
        for i, s in enumerate(qtile.screens):
            if (s.x, s.y, s.width, s.height) == (x, y, w, h):
                return i
    except Exception:
        pass
    return None


def _reconfigure_on_hotplug_inner():
    from config_parts.monitors import (
        configure_monitors,
        connected_outputs,
        current_rects,
        external_outputs,
        internal_output,
    )

    try:
        before = len(qtile.screens)
    except Exception:
        before = None
    try:
        changed = configure_monitors()
    except Exception:
        changed = False
    if changed:
        # Our own xrandr change fires another screen_change, which is where
        # qtile's rebuilt screen list exists. But the rebuild may already be
        # visible (driver applied geometry synchronously), so fall through
        # when the count already matches instead of waiting for an event
        # the cooldown used to eat.
        try:
            names = connected_outputs()
            want = 2 if external_outputs(names) else 1
            if len(qtile.screens) != want:
                # Fresh geometry under a stale pixmap = smear; repaint now
                # (this event) and again on the follow-up event our own
                # xrandr fires — cheap, idempotent.
                _repaint_wallpaper()
                return
        except Exception:
            return
        _repaint_wallpaper()
    try:
        names = connected_outputs()
        dual = bool(external_outputs(names))
        groups = qtile.groups_map
        from config_parts.groups import PRIMARY_GROUPS, SECONDARY_GROUPS

        # Place by geometry: screen 0 is the panel (CRTC 0), screen 1 the
        # external — NOT left-to-right. A name-based toscreen(0/1) swaps
        # the bars when CRTC order differs from x position.
        rects = current_rects()
        internal = internal_output(names)
        panel_idx, ext_idx = 0, 1
        for name, x, y, w, h in rects:
            idx = _screen_index_for_rect(x, y, w, h)
            if idx is None:
                continue
            if name == internal:
                panel_idx = idx
            else:
                ext_idx = idx
        n_screens = len(qtile.screens)
        for name in PRIMARY_GROUPS:
            groups[name].toscreen(panel_idx if n_screens > 1 else 0)
        for name in SECONDARY_GROUPS:
            groups[name].toscreen(ext_idx if (dual and n_screens > 1) else 0)
        # toscreen focuses each group it moves, so re-show the first of
        # each set — otherwise both screens sit on the last group (5, g).
        try:
            if n_screens > 1 and dual:
                qtile.focus_screen(panel_idx)
                groups[PRIMARY_GROUPS[0]].toscreen()
                qtile.focus_screen(ext_idx)
                groups[SECONDARY_GROUPS[0]].toscreen()
            else:
                qtile.focus_screen(0)
                groups[PRIMARY_GROUPS[0]].toscreen()
        except Exception:
            pass
        after = len(qtile.screens)
        # Converge the bar layout (one vs two Screens) when count changed —
        # reload_config() rebuilds from config, which builds in CRTC order,
        # so this converges instead of looping.
        if before is not None and ((after == 2) != dual or before != after):
            qtile.reload_config()
    except Exception:
        pass


@hook.subscribe.client_new
def bring_to_current_group(window):
    if "copyq" in (window.get_wm_class() or []):
        group = qtile.current_group

        if window.group != group:
            window.togroup(group.name)
