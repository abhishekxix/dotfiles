#! /usr/bin/env bash

export XDG_CURRENT_DESKTOP=qtile
export XDG_SESSION_DESKTOP=qtile
export XDG_SESSION_TYPE=x11

lxsession --session=qtile &

gnome-keyring-daemon --start --login --components=pkcs11,secrets,ssh &

# Monitor layout via the step-01 helper: same generic logic as the hotplug
# hook (internal primary @ max rate, externals left of it, --auto fallback).
# Foreground: xwallpaper below must paint after the framebuffer settles,
# or the image lands on stale geometry (smeared panel).
python3 "$HOME/.config/qtile/config_parts/monitors.py"

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

# Per-output --zoom (aspect kept); --stretch smears one image across the
# whole framebuffer. Empty/missing state file runs nothing (-r).
if [ -s "$HOME/.xwallpaper" ]; then
  wallpaper=$(cat "$HOME/.xwallpaper")
  wp_args=""
  for out in $(xrandr --query | awk '/ connected/{print $1}'); do
    wp_args="$wp_args --output $out --zoom $wallpaper"
  done
  # shellcheck disable=SC2086
  xwallpaper $wp_args &
fi

# Echo-cancel: skip if already loaded (login is not idempotent-safe),
# tolerate machines without this card.
if command -v pactl >/dev/null 2>&1 \
  && ! pactl list modules short 2>/dev/null | grep -q 'module-echo-cancel'; then
  pactl load-module module-echo-cancel source_master=alsa_input.pci-0000_00_1f.3.analog-stereo sink_master=alsa_output.pci-0000_00_1f.3.analog-stereo aec_method=webrtc aec_args="analog_gain_control=0 digital_gain_control=0" use_master_format=yes || true
fi
if command -v pactl >/dev/null 2>&1 \
  && pactl list sources short 2>/dev/null | grep -q 'echo-cancel-source'; then
  pactl set-default-source echo-cancel-source
fi
