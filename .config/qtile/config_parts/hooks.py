"""Qtile hook subscriptions."""

import os
import subprocess

from libqtile import hook, qtile


@hook.subscribe.startup_once
def autostart():
    autostart_script = os.path.expanduser("~/.config/qtile/autostart.sh")
    subprocess.run([autostart_script])


@hook.subscribe.client_new
def bring_to_current_group(window):
    if "copyq" in window.get_wm_class():
        group = qtile.current_group

        if window.group != group:
            window.togroup(group.name)
