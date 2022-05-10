from typing import List  # noqa: F401
import os
import subprocess
import libqtile as qtile
from libqtile import bar, layout, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy

# * vars
colors = {
    "background": "#23272E",
    "foreground":  "#FDFDFD",
    "highlight": "#44475a",
    "color0":  "#282A36",
    "color1":  "#F37F97",
    "color2":  "#5ADECD",
    "color3":  "#F2A272",
    "color4":  "#8897F4",
    "color5":  "#C574DD",
    "color6":  "#79E6F3",
    "color7":  "#FDFDFD",
    "color8":  "#414458",
    "color9":  "#FF4971",
    "color10": "#18E3C8",
    "color11": "#FF8037",
    "color12": "#556FFF",
    "color13": "#B043D1",
    "color14": "#3FDCEE",
    "color15": "#BEBEC1",
    "color16": "#B380F0"
}
my_menu = "rofi -combi-modi window,drun,ssh -show combi -icon-theme 'Papirus' -show-icons"
my_run_launcher = "rofi -combi-modi run -show combi"
mod = "mod4"
my_terminal = "alacritty"
my_browser = "google-chrome-stable --force-dark-mode"
my_vscode = "code"
my_spotify = "spotify"
my_screensaver = "xscreensaver-command -lock"
my_file_manager = "thunar"
my_video_player = "vlc"
my_obsidian = "obsidian"

bar_theme = {
    "background": colors["background"],
    "foreground": colors["foreground"],
    "opacity": 0.85,
}

layout_theme = {
    "border_width": 1,
    "margin": 8,
    "border_focus": colors["color9"],
    "border_normal": "#000000"
}

# * vars end

# * Functions


def parse_window_name(name: str):
  if name.endswith('-'):
    return name
  return f'Current Window [{name[name.rfind("-") + 1:]}]'


def kbd_shortcuts():
  return [
      #   * Lock screen
      Key([mod], "BackSpace", lazy.spawn(my_screensaver)),
      #   * Move focus
      Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
      Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
      Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
      Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
      Key([mod], "space", lazy.layout.next(),
          desc="Move window focus to other window"),

      #    * Shuffle windows in a layout
      Key([mod, "shift"], "h", lazy.layout.shuffle_left(),
          desc="Move window to the left"),
      Key([mod, "shift"], "l", lazy.layout.shuffle_right(),
          desc="Move window to the right"),
      Key([mod, "shift"], "j", lazy.layout.shuffle_down(),
          desc="Move window down"),
      Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),


      #   * Window resize
      Key([mod, "control"], "h", lazy.layout.grow_left(),
          desc="Grow window to the left"),
      Key([mod, "control"], "l", lazy.layout.grow_right(),
          desc="Grow window to the right"),
      Key([mod, "control"], "j",
          lazy.layout.grow_down(), desc="Grow window down"),
      Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
      Key([mod], "n", lazy.layout.normalize(),
          desc="Reset all window sizes"),


      # * Toggle between split and unsplit sides of stack.
      Key(
          [mod, "shift"],
          "Return",
          lazy.layout.toggle_split(),
          desc="Toggle between split and unsplit sides of stack",
      ),

      #   * Toggle layouts
      Key([mod], "Tab", lazy.next_layout(), desc="Switch to next layout"),
      Key([mod, "shift"], "Tab", lazy.prev_layout(),
          desc="Switch to previous layout"),

      #   * Toggle floating mode
      Key([mod, "shift"], "t", lazy.window.toggle_floating(),
          desc="Toggle floating mode"),

      #   * Toggle fullscreen
      Key([mod, "shift"], "f", lazy.window.toggle_fullscreen(),
          desc="Toggle floating mode"),

      #   * Reload Qtile
      Key([mod, "control"], "r",
          lazy.reload_config(), desc="Reload the config"),
      #     * Shutdown Qtile
      Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
      #   * Kill Window
      Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),

      #   * Launch programs
      Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
      Key([mod], "e", lazy.spawn(my_vscode), desc="Launch vscode"),
      Key([mod], "w", lazy.spawn(my_browser), desc="Launch chrome"),
      Key([mod], "s", lazy.spawn(my_spotify), desc="Launch chrome"),
      Key([mod], "r", lazy.spawn(my_menu), desc="Launch rofi run menu"),
      Key([mod], "f", lazy.spawn(my_file_manager), desc="Launch file manager"),
      Key([mod], "v", lazy.spawn(my_video_player), desc="Launch video player"),
      Key([mod], "o", lazy.spawn(my_obsidian), desc="Launch obsidian"),

      #   * launch pavucontrol
      Key([mod], "p", lazy.spawn("pavucontrol"), desc="Launch pavucontrol"),
      Key(["mod1"], "space", lazy.spawn(
          my_run_launcher), desc="Launch rofi run"),

  ]


def setup_groups(groups):
  for i in groups:
    keys.extend(
        [
            # mod1 + letter of group = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            # mod1 + shift + letter of group = switch to & move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc="Switch to & move focused window to group {}".format(
                    i.name),
            ),
            # Or, use below if you prefer not to switch to that group.
            # # # mod1 + shift + letter of group = move focused window to group
            # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
            #     desc="move focused window to group {}".format(i.name)),
        ]
    )

# * Functions end


terminal = my_terminal
keys = kbd_shortcuts()

groups = [Group(i) for i in "123456789"]
setup_groups(groups)


layouts = [
    layout.Columns(
        border_focus_stack=["#d75f5f", "#8f3d3d"], **layout_theme
    ),
    layout.Max(**layout_theme),
    # Try more layouts by unleashing below layouts.
    layout.Stack(num_stacks=2, **layout_theme),
    # layout.Bsp(),
    layout.Matrix(**layout_theme),
    # layout.MonadTall(),
    # layout.MonadWide(),
    layout.RatioTile(**layout_theme),
    layout.Tile(**layout_theme),
    # layout.TreeTab(),
    layout.VerticalTile(**layout_theme),
    layout.Zoomy(**layout_theme),
    layout.Floating(**layout_theme)
]

widget_defaults = dict(
    font="Ubuntu Bold",
    fontsize=12,
    padding=3,
    background=colors["background"],
    foreground=colors["color9"],
)

extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.Sep(
                    linewidth=0,
                    padding=12,
                ),
                widget.Image(
                    filename="~/.config/qtile/icons/debianlogo.svg",
                    scale=True,
                    margin=3,
                    mouse_callbacks={
                        "Button1": lazy.spawn(my_menu)
                    }
                ),
                widget.Sep(
                    linewidth=0,
                    padding=6,
                ),


                widget.GroupBox(
                    margin_x=3, margin_y=3,
                    padding_x=3, padding_y=5,
                    border_width=3,
                    rounded=True,
                    highlight_method="line",
                    highlight_color=colors["background"],
                    active=colors["color9"], inactive="#6272a4",
                    this_current_screen_border=colors["foreground"]
                ),




                widget.Spacer(length=bar.STRETCH),
                widget.Net(
                    fmt="{}",
                    format="{down} ↓↑ {up}",
                ),
                widget.Sep(
                    linewidth=0,
                    padding=12,
                ),
                widget.CPU(),

                widget.Sep(
                    linewidth=0,
                    padding=12,
                ),

                widget.Sep(
                    linewidth=0,
                    padding=12,
                ),
                widget.Memory(fmt="MEM:{}", measure_mem="M"),

                widget.Spacer(length=bar.STRETCH),




                widget.Sep(
                    linewidth=0,
                    padding=12,
                ),

                widget.Systray(icon_size=20),
                widget.Sep(
                    linewidth=0,
                    padding=12,
                ),
                widget.Clock(
                    format="%Y-%m-%d %a",
                    fmt="{}"
                ),
                widget.Sep(
                    linewidth=0,
                    padding=4,
                ),
                widget.Clock(
                    format="%I:%M:%S %p",
                    fmt="{}"
                ),

                widget.Sep(
                    linewidth=0,
                    padding=12,
                ),
                widget.CurrentLayoutIcon(
                    custom_icon_paths=[
                        os.path.expanduser("~/.config/qtile/icons")],
                    padding=0,
                    scale=0.6
                ),
                widget.Sep(
                    linewidth=0,
                    padding=12,
                ),

            ],
            30,
            **bar_theme, margin=[2, 100, 0, 100]
        )
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
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
        Match(wm_class="pavucontrol")
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True


# * autostart hook
@hook.subscribe.startup_once
def autostart():
  home = os.path.expanduser('~/.config/qtile/autostart.sh')
  subprocess.run([home])


# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
# # custom functions
