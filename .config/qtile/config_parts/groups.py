"""Workspace groups and related key helpers."""

from libqtile.config import Group, Key
from libqtile.lazy import lazy


PRIMARY_GROUPS = "12345"
SECONDARY_GROUPS = "asdfg"


def build_groups():
    groups = [Group(name, screen_affinity=0) for name in PRIMARY_GROUPS]
    groups.extend(
        [Group(name, screen_affinity=1, label=name.lower()) for name in SECONDARY_GROUPS]
    )
    return groups


def go_to_group(name: str):
    def _inner(qtile):
        if len(qtile.screens) == 1:
            qtile.groups_map[name].toscreen()
            return

        if name in PRIMARY_GROUPS:
            qtile.focus_screen(0)
        else:
            qtile.focus_screen(1)

        qtile.groups_map[name].toscreen()

    return _inner


def move_window_to_group(name: str):
    def _inner(qtile):
        if qtile.current_window is None:
            return

        qtile.current_window.togroup(name)

        if len(qtile.screens) != 1:
            if name in PRIMARY_GROUPS:
                qtile.focus_screen(0)
            else:
                qtile.focus_screen(1)

        qtile.groups_map[name].toscreen()

    return _inner


def extend_group_keys(keys, groups, modkey, shiftkey):
    for group in groups:
        keys.extend(
            [
                Key([modkey], group.name, lazy.function(go_to_group(group.name))),
                Key(
                    [modkey, shiftkey],
                    group.name,
                    lazy.function(move_window_to_group(group.name)),
                ),
            ]
        )
