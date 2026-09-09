"""Qtile hook subscriptions."""

import os
import subprocess

from libqtile import hook, qtile


@hook.subscribe.startup_once
def autostart():
    autostart_script = os.path.expanduser("~/.config/qtile/autostart.sh")
    # Fire-and-forget: don't block WM startup on slow xrandr/tray apps.
    subprocess.Popen([autostart_script])


@hook.subscribe.screen_change
def reconfigure_on_hotplug(event=None):
    """Apply monitor config, place groups, reload bars if screen count changed."""
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
        configure_monitors()
    except Exception:
        pass
    try:
        names = connected_outputs()
        dual = bool(external_outputs(names))
        groups = qtile.groups_map
        from config_parts.groups import PRIMARY_GROUPS, SECONDARY_GROUPS

        n_screens = len(qtile.screens)
        for name in PRIMARY_GROUPS:
            groups[name].toscreen(0)
        for name in SECONDARY_GROUPS:
            # ponytail: target screen 1 only if it exists yet; reload below
            # converges the bar layout, next hotplug event places leftovers.
            groups[name].toscreen(1 if (dual and n_screens > 1) else 0)
        after = len(qtile.screens)
        # Converge the bar layout (one vs two Screens) when count changed.
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
