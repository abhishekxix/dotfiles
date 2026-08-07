"""Layout and floating layout definitions."""

from libqtile import layout
from libqtile.config import Match


def build_layouts(layout_theme):
    return [
        layout.Columns(**layout_theme),
        layout.Max(**layout_theme),
        layout.Stack(num_stacks=2, **layout_theme),
        layout.Matrix(**layout_theme),
        layout.RatioTile(**layout_theme),
        layout.Tile(**layout_theme),
        layout.VerticalTile(**layout_theme),
        layout.Zoomy(**layout_theme),
        layout.Floating(**layout_theme),
    ]


def build_floating_layout():
    return layout.Floating(
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
