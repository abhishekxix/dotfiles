import os
import subprocess
from libqtile import bar, layout, hook, widget, qtile
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy

"""
	! Config dictionary.
"""
colors = {
    "background": "#1e1e2e",
    "foreground": "#cdd6f4",
    "accent": "#89b4fa",
    "inactive": "#585b70",
}
my_config_dict = {
    "terminal": "alacritty",
    "modkey": "mod4",  # The windows key.
    "bar_theme": {
        "background": colors["background"],
        "foreground": colors["foreground"],
        # "margin": [2, 50, 0, 50],
        # "opacity": 0.95,
    },
    "layout_theme": {
        "border_width": 1,
        "margin": 2,
        "border_focus": colors["accent"],
        "border_normal": "#000000",
    },
    "menu": "rofi -combi-modi window,drun,ssh -show combi -icon-theme 'Papirus' -show-icons",
    "run_launcher": "rofi -combi-modi run -show combi",
    "web_browser": "google-chrome",
    "file_manager": "nautilus",
    "pavu": "pavucontrol",
}
"""
	! Config dictionary end.
"""


MODKEY = my_config_dict["modkey"]
SHIFTKEY = "shift"
TABKEY = "Tab"
CONTROLKEY = "control"

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.Spacer(length=12),
                widget.Image(
                    filename=os.path.expanduser("~/.config/qtile/icons/debianlogo.svg"),
                    scale=True,
                    margin_y=4,
                    mouse_callbacks={"Button1": lazy.spawn(my_config_dict["menu"])},
                ),
                widget.Spacer(length=12),
                widget.GroupBox(
                    border_width=3,
                    rounded=True,
                    highlight_method="line",
                    highlight_color=colors["background"],
                    active=colors["accent"],
                    inactive=colors["inactive"],
                    disable_drag=True,
                    visible_groups=["1", "2", "3", "4", "5"],
                ),
                widget.Spacer(length=bar.STRETCH),
                widget.WindowName(),
                widget.Spacer(length=bar.STRETCH),
                widget.Systray(icon_size=20),
                widget.Spacer(length=12),
                widget.Battery(fmt="🗲 {}", format="{char} {percent:2.0%}"),
                widget.Spacer(length=12),
                widget.Backlight(
                    fmt="💡 {}",
                    backlight_name="intel_backlight",
                    brightness_file="brightness",
                ),
                widget.Spacer(length=12),
                widget.Clock(format="%Y-%m-%d %a", fmt="{}"),
                widget.Spacer(length=4),
                widget.Clock(format="%H:%M:%S", fmt="{}"),
                widget.Spacer(length=12),
                widget.CurrentLayoutIcon(padding=0, scale=0.6),
                widget.Spacer(length=12),
            ],
            32,
            **(my_config_dict["bar_theme"]),
        )
    ),
    Screen(
        top=bar.Bar(
            [
                widget.Spacer(length=12),
                widget.Image(
                    filename=os.path.expanduser("~/.config/qtile/icons/debianlogo.svg"),
                    scale=True,
                    margin_y=4,
                    mouse_callbacks={"Button1": lazy.spawn(my_config_dict["menu"])},
                ),
                widget.Spacer(length=12),
                widget.GroupBox(
                    highlight_method="line",
                    highlight_color=colors["background"],
                    active=colors["accent"],
                    inactive=colors["inactive"],
                    disable_drag=True,
                    visible_groups=["a", "s", "d", "f", "g"],
                ),
                widget.Spacer(length=bar.STRETCH),
                widget.WindowName(),
                widget.Spacer(length=bar.STRETCH),
                widget.Clock(format="%Y-%m-%d %a", fmt="{}"),
                widget.Spacer(length=4),
                widget.Clock(format="%H:%M:%S", fmt="{}"),
                widget.Spacer(length=12),
                widget.CurrentLayoutIcon(padding=0, scale=0.6),
                widget.Spacer(length=12),
            ],
            32,
            **(my_config_dict["bar_theme"]),
        )
    ),
]

layouts = [
    layout.Columns(**(my_config_dict["layout_theme"])),
    layout.Max(**(my_config_dict["layout_theme"])),
    layout.Stack(num_stacks=2, **(my_config_dict["layout_theme"])),
    layout.Matrix(**(my_config_dict["layout_theme"])),
    layout.RatioTile(**(my_config_dict["layout_theme"])),
    layout.Tile(**(my_config_dict["layout_theme"])),
    layout.VerticalTile(**(my_config_dict["layout_theme"])),
    layout.Zoomy(**(my_config_dict["layout_theme"])),
    layout.Floating(**(my_config_dict["layout_theme"])),
]

groups = [Group(name, screen_affinity=0) for name in "12345"]
groups.extend([Group(name, screen_affinity=1, label=name.lower()) for name in "asdfg"])

keys = [
    Key([MODKEY], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([MODKEY], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([MODKEY], "j", lazy.layout.down(), desc="Move focus down"),
    Key([MODKEY], "k", lazy.layout.up(), desc="Move focus up"),
    Key(
        [MODKEY], "space", lazy.layout.next(), desc="Move window focus to other window"
    ),
    Key(
        [MODKEY, SHIFTKEY],
        "h",
        lazy.layout.shuffle_left(),
        desc="Move window to the left",
    ),
    Key(
        [MODKEY, SHIFTKEY],
        "l",
        lazy.layout.shuffle_right(),
        desc="Move window to the right",
    ),
    Key([MODKEY, SHIFTKEY], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([MODKEY, SHIFTKEY], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    Key(
        [MODKEY, CONTROLKEY],
        "h",
        lazy.layout.grow_left(),
        desc="Grow window to the left",
    ),
    Key(
        [MODKEY, CONTROLKEY],
        "l",
        lazy.layout.grow_right(),
        desc="Grow window to the right",
    ),
    Key([MODKEY, CONTROLKEY], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([MODKEY, CONTROLKEY], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([MODKEY], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    Key(
        [MODKEY, SHIFTKEY],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key(
        [MODKEY],
        "Return",
        lazy.spawn(my_config_dict["terminal"]),
        desc="Launch terminal",
    ),
    Key([MODKEY], TABKEY, lazy.next_layout(), desc="Toggle between layouts"),
    Key([MODKEY, SHIFTKEY], TABKEY, lazy.prev_layout(), desc="Toggle between layouts"),
    Key([MODKEY], "q", lazy.window.kill(), desc="Kill focused window"),
    Key(
        [MODKEY, SHIFTKEY],
        "z",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key(
        [MODKEY, SHIFTKEY],
        "t",
        lazy.window.toggle_floating(),
        desc="Toggle floating on the focused window",
    ),
    Key([MODKEY, CONTROLKEY], "r", lazy.reload_config(), desc="Reload the config"),
    Key([MODKEY, CONTROLKEY], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([MODKEY], "r", lazy.spawn(my_config_dict["menu"]), desc="Launch rofi run"),
    Key(
        ["mod1"],
        "space",
        lazy.spawn(my_config_dict["run_launcher"]),
        desc="Spawn a command using a prompt widget",
    ),
    Key(
        [MODKEY],
        "w",
        lazy.spawn(my_config_dict["web_browser"]),
        desc="Launch web browser",
    ),
    Key(
        [MODKEY],
        "p",
        lazy.spawn(my_config_dict["pavu"]),
        desc="Launch pavucontrol",
    ),
    Key(
        [MODKEY],
        "m",
        lazy.group.unminimize_all(),
        desc="Toggle minimize state of a window",
    ),
]


def go_to_group(name: str):
    def _inner(qtile):
        if len(qtile.screens) == 1:
            qtile.groups_map[name].toscreen()
            return

        if name in "12345":
            qtile.focus_screen(0)
        else:
            qtile.focus_screen(1)

        qtile.groups_map[name].toscreen()

    return _inner


def move_window_to_group(name: str):
    def _inner(qtile):

        qtile.current_window.togroup(name)

        if len(qtile.screens) != 1:
            if name in "12345":
                qtile.focus_screen(0)
            else:
                qtile.focus_screen(1)

        qtile.groups_map[name].toscreen()

    return _inner


for group in groups:
    keys.extend(
        [
            Key([MODKEY], group.name, lazy.function(go_to_group(group.name))),
            Key(
                [MODKEY, SHIFTKEY],
                group.name,
                lazy.function(move_window_to_group(group.name)),
            ),
        ]
    )

widget_defaults = dict(
    font="Ubuntu Bold",
    fontsize=14,
    background=colors["background"],
    foreground=colors["foreground"],
)

extension_defaults = widget_defaults.copy()

# Drag floating layouts.
mouse = [
    Drag(
        [MODKEY],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [MODKEY],
        "Button3",
        lazy.window.set_size_floating(),
        start=lazy.window.get_size(),
    ),
    Click([MODKEY], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = True
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(wm_class="blueberry.py"),
        Match(wm_class="copyq"),
        Match(wm_class="pavucontrol"),
        Match(wm_class="gnome-system-monitor"),
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True


# * autostart hook
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


# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
