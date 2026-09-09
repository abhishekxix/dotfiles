"""Keybinding definitions."""

from libqtile.config import Key
from libqtile.lazy import lazy


def build_keys(modkey, shiftkey, tabkey, controlkey, my_config_dict):
    return [
        Key([modkey], "h", lazy.layout.left(), desc="Move focus to left"),
        Key([modkey], "l", lazy.layout.right(), desc="Move focus to right"),
        Key([modkey], "j", lazy.layout.down(), desc="Move focus down"),
        Key([modkey], "k", lazy.layout.up(), desc="Move focus up"),
        Key(
            [modkey],
            "space",
            lazy.layout.next(),
            desc="Move window focus to other window",
        ),
        Key(
            [modkey, shiftkey],
            "h",
            lazy.layout.shuffle_left(),
            desc="Move window to the left",
        ),
        Key(
            [modkey, shiftkey],
            "l",
            lazy.layout.shuffle_right(),
            desc="Move window to the right",
        ),
        Key(
            [modkey, shiftkey], "j", lazy.layout.shuffle_down(), desc="Move window down"
        ),
        Key([modkey, shiftkey], "k", lazy.layout.shuffle_up(), desc="Move window up"),
        Key(
            [modkey, controlkey],
            "h",
            lazy.layout.grow_left(),
            desc="Grow window to the left",
        ),
        Key(
            [modkey, controlkey],
            "l",
            lazy.layout.grow_right(),
            desc="Grow window to the right",
        ),
        Key(
            [modkey, controlkey], "j", lazy.layout.grow_down(), desc="Grow window down"
        ),
        Key([modkey, controlkey], "k", lazy.layout.grow_up(), desc="Grow window up"),
        Key([modkey], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
        Key(
            [modkey, shiftkey],
            "Return",
            lazy.layout.toggle_split(),
            desc="Toggle between split and unsplit sides of stack",
        ),
        Key(
            [modkey],
            "Return",
            lazy.spawn(my_config_dict["terminal"]),
            desc="Launch terminal",
        ),
        Key([modkey], tabkey, lazy.next_layout(), desc="Toggle between layouts"),
        Key(
            [modkey, shiftkey],
            tabkey,
            lazy.prev_layout(),
            desc="Toggle between layouts",
        ),
        Key([modkey], "q", lazy.window.kill(), desc="Kill focused window"),
        Key(
            [modkey, shiftkey],
            "z",
            lazy.window.toggle_fullscreen(),
            desc="Toggle fullscreen on the focused window",
        ),
        Key(
            [modkey, shiftkey],
            "t",
            lazy.window.toggle_floating(),
            desc="Toggle floating on the focused window",
        ),
        Key([modkey, controlkey], "r", lazy.reload_config(), desc="Reload the config"),
        Key([modkey, controlkey], "q", lazy.shutdown(), desc="Shutdown Qtile"),
        Key([modkey], "r", lazy.spawn(my_config_dict["menu"]), desc="Launch rofi run"),
        Key(
            ["mod1"],
            "space",
            lazy.spawn(my_config_dict["run_launcher"]),
            desc="Spawn a command using a prompt widget",
        ),
        Key(
            [modkey],
            "w",
            lazy.spawn(my_config_dict["web_browser"]),
            desc="Launch web browser",
        ),
        Key(
            [modkey],
            "p",
            lazy.spawn(my_config_dict["pavu"]),
            desc="Launch pavucontrol",
        ),
        Key(
            [modkey],
            "m",
            lazy.window.toggle_minimize(),
            desc="Toggle minimize state of a window",
        ),
        Key([], "XF86AudioRaiseVolume", lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ +5%"), desc="Raise volume"),
        Key([], "XF86AudioLowerVolume", lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ -5%"), desc="Lower volume"),
        Key([], "XF86AudioMute", lazy.spawn("pactl set-sink-mute @DEFAULT_SINK@ toggle"), desc="Mute volume"),
        Key([], "XF86AudioMicMute", lazy.spawn("pactl set-source-mute @DEFAULT_SOURCE@ toggle"), desc="Mute mic"),
        Key([], "XF86MonBrightnessUp", lazy.spawn("sh -c 'b=$(cat /sys/class/backlight/*/brightness | head -1); m=$(cat /sys/class/backlight/*/max_brightness | head -1); echo $((b + m / 20 > m ? m : b + m / 20)) | tee /sys/class/backlight/*/brightness'"), desc="Brightness up"),
        Key([], "XF86MonBrightnessDown", lazy.spawn("sh -c 'b=$(cat /sys/class/backlight/*/brightness | head -1); m=$(cat /sys/class/backlight/*/max_brightness | head -1); echo $((b - m / 20 < 1 ? 1 : b - m / 20)) | tee /sys/class/backlight/*/brightness'"), desc="Brightness down"),
        Key([modkey], "o", lazy.next_screen(), desc="Focus next screen"),
        Key([modkey, shiftkey], "o", lazy.window.toscreen(), desc="Move window to next screen"),
        Key([modkey], "u", lazy.group.unminimize_all(), desc="Unminimize all windows"),
    ]
