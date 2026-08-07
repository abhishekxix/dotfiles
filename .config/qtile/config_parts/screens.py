"""Screen and bar definitions."""

import os

from libqtile import bar, widget
from libqtile.config import Screen
from libqtile.lazy import lazy


def build_screens(my_config_dict, colors):
    return [
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
                    widget.StatusNotifier(icon_size=20, padding=3),
                    widget.Systray(icon_size=20),
                    widget.Spacer(length=12),
                    widget.ThermalSensor(
                        format=":  {temp: .0f}{unit}",
                    ),
                    widget.NvidiaSensors(
                        format="󰢮   {temp}°C",
                    ),
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
                    widget.ThermalSensor(
                        format=":  {temp: .0f}{unit}",
                    ),
                    widget.NvidiaSensors(
                        format="󰢮   {temp}°C",
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
    ]
