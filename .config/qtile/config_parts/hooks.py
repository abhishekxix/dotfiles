"""Qtile hook subscriptions."""

import os
import subprocess

from libqtile import hook, qtile


@hook.subscribe.startup_once
def autostart():
    autostart_script = os.path.expanduser("~/.config/qtile/autostart.sh")
    # Fire-and-forget: don't block WM startup on slow xrandr/tray apps.
    subprocess.Popen([autostart_script])


# ponytail: re-entry lock + 5s cooldown + one reload per plug state.
# screen_change fires per RandR event (xrandr calls cascade); without these,
# configure→event→configure→reload_config() never converges (black-screen loop).
_HOTPLUG_BUSY = False
_HOTPLUG_LAST_RUN = 0.0
_HOTPLUG_LAST_RELOAD_DUAL = None


@hook.subscribe.screen_change
def reconfigure_on_hotplug(event=None):
    """Apply monitor config, place groups, reload bars if screen count changed."""
    import time

    global _HOTPLUG_BUSY, _HOTPLUG_LAST_RUN, _HOTPLUG_LAST_RELOAD_DUAL
    if _HOTPLUG_BUSY:
        return
    now = time.monotonic()
    if now - _HOTPLUG_LAST_RUN < 5:
        return
    _HOTPLUG_BUSY = True
    _HOTPLUG_LAST_RUN = now
    try:
        _reconfigure_on_hotplug_inner()
    finally:
        _HOTPLUG_BUSY = False


def _reconfigure_on_hotplug_inner():
    from config_parts.monitors import (
        configure_monitors,
        connected_outputs,
        external_outputs,
    )

    try:
        before = len(qtile.screens)
    except Exception:
        before = None
    try:
        changed = configure_monitors()
    except Exception:
        changed = False
    # Our own xrandr change fires another screen_change, which is where
    # placement + reload happen — doing them here too would run against
    # qtile's not-yet-rebuilt screen list.
    if changed:
        return
    try:
        names = connected_outputs()
        dual = bool(external_outputs(names))
        groups = qtile.groups_map
        from config_parts.groups import PRIMARY_GROUPS, SECONDARY_GROUPS

        n_screens = len(qtile.screens)
        for name in PRIMARY_GROUPS:
            groups[name].toscreen(0)
        for name in SECONDARY_GROUPS:
            # Target screen 1 only if it exists yet; the reload below
            # converges the bar layout, the next event places leftovers.
            groups[name].toscreen(1 if (dual and n_screens > 1) else 0)
        after = len(qtile.screens)
        # Converge the bar layout (one vs two Screens) when count changed —
        # at most once per plug state, so a flapping driver can't loop reloads.
        global _HOTPLUG_LAST_RELOAD_DUAL
        if (
            before is not None
            and ((after == 2) != dual or before != after)
            and _HOTPLUG_LAST_RELOAD_DUAL != dual
        ):
            _HOTPLUG_LAST_RELOAD_DUAL = dual
            qtile.reload_config()
    except Exception:
        pass


@hook.subscribe.client_new
def bring_to_current_group(window):
    if "copyq" in (window.get_wm_class() or []):
        group = qtile.current_group

        if window.group != group:
            window.togroup(group.name)
