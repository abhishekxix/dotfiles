"""Shared settings for Qtile configuration."""

from pathlib import Path

# Resolved from this file's real location (the config is symlinked into
# ~/.config), so .bin scripts are found wherever the repo lives. Needed
# because lazy.spawn shlex-splits the command and shutil.which()es the first
# token, so paths must be literal — no $HOME expansion, no shell.
REPO_ROOT = Path(__file__).resolve().parents[3]

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
    # -normal-window: rofi skips its active keyboard grab (rofi 1.7.5 has no
    # toggle for it), so the xbindkeys PrtSc -> flameshot grab keeps working
    # while rofi is open. Requires the rofi float rule in layouts.py.
    "menu": "rofi -normal-window -combi-modi window,drun,ssh -show combi -icon-theme 'Papirus' -show-icons",
    "run_launcher": "rofi -normal-window -show run",
    "power_menu": str(REPO_ROOT / ".bin" / "power-menu.sh"),
    "web_browser": "google-chrome",
    "file_manager": "nautilus",
    "pavu": "pavucontrol",
}

MODKEY = my_config_dict["modkey"]
SHIFTKEY = "shift"
TABKEY = "Tab"
CONTROLKEY = "control"
