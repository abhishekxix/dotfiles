"""Mouse behavior for floating windows."""

from libqtile.config import Click, Drag
from libqtile.lazy import lazy


def drag_window_without_warp(qtile, x, y):
    window = qtile.current_window
    if window is None:
        return

    # Avoid pointer warps while dragging across screens.
    old_cursor_warp = qtile.config.cursor_warp
    qtile.config.cursor_warp = False
    try:
        window.set_position_floating(x, y)
    finally:
        qtile.config.cursor_warp = old_cursor_warp


def build_mouse(modkey):
    return [
        Drag(
            [modkey],
            "Button1",
            lazy.function(drag_window_without_warp),
            start=lazy.window.get_position(),
        ),
        Drag(
            [modkey],
            "Button3",
            lazy.window.set_size_floating(),
            start=lazy.window.get_size(),
        ),
        Click([modkey], "Button2", lazy.window.bring_to_front()),
    ]
