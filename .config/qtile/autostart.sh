#! /usr/bin/env bash

export XDG_CURRENT_DESKTOP=qtile
export XDG_SESSION_DESKTOP=qtile
export XDG_SESSION_TYPE=x11

lxsession --session=qtile &

gnome-keyring-daemon --start --login --components=pkcs11,secrets,ssh &

# Dual-monitor layout; only when both outputs are connected, else leave the
# server layout alone (single-monitor / foreign dock).
if xrandr --query 2>/dev/null | grep -q '^HDMI-0 connected' \
  && xrandr --query 2>/dev/null | grep -q '^eDP-1-1 connected'; then
  xrandr --output HDMI-0 --mode 2560x1440 --rate 75 --pos 0x0 --rotate normal --output eDP-1-1 --primary --mode 1920x1080 --rate 120 --pos 2560x360 --rotate normal
fi

export WINIT_X11_SCALE_FACTOR=1

# Launch only if installed — keeps fresh machines boot-noise-free.
try_launch() {
  command -v "$1" >/dev/null 2>&1 && "$@" &
}

try_launch picom
try_launch xbindkeys
try_launch flameshot
try_launch dunst
try_launch volumeicon
try_launch copyq
try_launch nm-applet
# try_launch blueberry
try_launch blueman-applet
try_launch xscreensaver --nosplash
# try_launch mictray

# Wallpaper list may not exist (fresh install); -r runs nothing on empty input.
if [ -s "$HOME/.xwallpaper" ]; then
  xargs -r xwallpaper --stretch <"$HOME/.xwallpaper" &
fi

# Set the audio settings.
pactl load-module module-echo-cancel source_master=alsa_input.pci-0000_00_1f.3.analog-stereo sink_master=alsa_output.pci-0000_00_1f.3.analog-stereo aec_method=webrtc aec_args="analog_gain_control=0 digital_gain_control=0" use_master_format=yes
pactl set-default-source echo-cancel-source
