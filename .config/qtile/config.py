from config_parts.groups import build_groups, extend_group_keys
from config_parts.keys import build_keys
from config_parts.layouts import build_floating_layout, build_layouts
from config_parts.mouse import build_mouse
from config_parts.screens import build_screens
from config_parts.settings import (
    CONTROLKEY,
    MODKEY,
    SHIFTKEY,
    TABKEY,
    colors,
    my_config_dict,
)

# Import hooks so subscribers are registered.
import config_parts.hooks  # noqa: F401

screens = build_screens(my_config_dict, colors)
layouts = build_layouts(my_config_dict["layout_theme"])
groups = build_groups()

keys = build_keys(
    MODKEY,
    SHIFTKEY,
    TABKEY,
    CONTROLKEY,
    my_config_dict,
)
extend_group_keys(keys, groups, MODKEY, SHIFTKEY)

widget_defaults = dict(
    font="Ubuntu Bold",
    fontsize=14,
    background=colors["background"],
    foreground=colors["foreground"],
)
extension_defaults = widget_defaults.copy()

mouse = build_mouse(MODKEY)

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
# Keep cursor warp enabled generally; drag helper disables it only while dragging.
cursor_warp = True
floating_layout = build_floating_layout()
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True


# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
