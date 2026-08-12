"""Shared settings for Qtile configuration."""

colors = {
    "background": "#1e1e2e",
    "surface": "#313244",
    "foreground": "#cdd6f4",
    "accent": "#89b4fa",
    "inactive": "#585b70",
    "muted": "#7f849c",
    "green": "#a6e3a1",
    "yellow": "#f9e2af",
    "red": "#f38ba8",
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

MODKEY = my_config_dict["modkey"]
SHIFTKEY = "shift"
TABKEY = "Tab"
CONTROLKEY = "control"
