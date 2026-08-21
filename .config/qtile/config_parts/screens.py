"""Screen and bar definitions."""

import os

from libqtile import bar, widget
from libqtile.config import Screen
from libqtile.lazy import lazy


def _separator(colors):
    return widget.TextBox(text="│", foreground=colors["inactive"], padding=5)


def _group_box(visible_groups, colors):
    return widget.GroupBox(
        border_width=3,
        rounded=True,
        highlight_method="block",
        highlight_color=colors["background"],
        active=colors["foreground"],
        inactive=colors["inactive"],
        this_current_screen_border=colors["surface"],
        block_highlight_text_color=colors["accent"],
        disable_drag=True,
        padding=6,
        visible_groups=visible_groups,
    )


def _temperature_widgets(colors):
    return [
        widget.ThermalSensor(
            format="   {temp:.0f}{unit}",
            foreground=colors["red"],
            padding=6,
        ),
        widget.NvidiaSensors(
            format="󰢮   {temp}°C",
            foreground=colors["red"],
            padding=6,
        ),
    ]


def _build_bar_widgets(my_config_dict, colors, visible_groups, primary=False):
    status_widgets = []

    status_widgets.extend(
        [
            widget.Net(
                interface="wlo1",
                format="󰖩   {down:.0f}{down_suffix}↓ {up:.0f}{up_suffix}↑",
                foreground=colors["accent"],
                padding=6,
            ),
            _separator(colors),
            widget.Memory(
                format="󰍛  {MemUsed: .2f}/{MemTotal: .2f} {mm}",
                measure_mem="G",
                padding=6,
            ),
            _separator(colors),
            *_temperature_widgets(colors),
            _separator(colors),
            widget.Battery(
                format="󰁹  {char} {percent:2.0%}",
                foreground=colors["green"],
                padding=6,
            ),
            widget.Backlight(
                fmt="󰃠   {}",
                backlight_name="intel_backlight",
                brightness_file="brightness",
                foreground=colors["yellow"],
                padding=6,
            ),
        ]
    )

    status_widgets.extend(
        [
            _separator(colors),
            widget.Clock(format="%a %d %b %Y · %H:%M:%S", padding=6),
        ]
    )

    if primary:
        status_widgets.extend(
            [
                _separator(colors),
                widget.StatusNotifier(icon_size=20, padding=4),
                widget.Systray(icon_size=20, padding=4),
            ]
        )

    status_widgets.extend(
        [
            _separator(colors),
            widget.CurrentLayoutIcon(padding=8, scale=0.6),
        ]
    )

    return [
        widget.Image(
            filename=os.path.expanduser("~/.config/qtile/icons/debianlogo.svg"),
            scale=True,
            margin_y=4,
            margin_x=10,
            mouse_callbacks={"Button1": lazy.spawn(my_config_dict["menu"])},
        ),
        _group_box(visible_groups, colors),
        _separator(colors),
        widget.TaskList(
            border=colors["surface"],
            borderwidth=1,
            highlight_method="block",
            icon_size=20,
            foreground=colors["muted"],
            max_title_width=150,
            padding=4,
            urgent_border=colors["red"],
        ),
        *status_widgets,
    ]


def _build_screen(my_config_dict, colors, visible_groups, primary=False):
    return Screen(
        top=bar.Bar(
            _build_bar_widgets(my_config_dict, colors, visible_groups, primary),
            32,
            **my_config_dict["bar_theme"],
        )
    )


def build_screens(my_config_dict, colors):
    return [
        _build_screen(my_config_dict, colors, ["1", "2", "3", "4", "5"], True),
        _build_screen(my_config_dict, colors, ["a", "s", "d", "f", "g"]),
    ]
