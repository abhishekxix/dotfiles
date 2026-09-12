#! /usr/bin/env bash

# Session identity (XDG_*/WINIT) and keyring ownership live in ~/.xsessionrc,
# sourced by Debian Xsession before Qtile starts. Fall back here only when
# that file was not sourced (e.g. a display manager that skips Xsession).
if [ -z "$XDG_SESSION_DESKTOP" ]; then
  export XDG_CURRENT_DESKTOP=qtile
  export XDG_SESSION_DESKTOP=qtile
  export XDG_SESSION_TYPE=x11
  export WINIT_X11_SCALE_FACTOR=1
fi

# Qtile's guarded script is the single owner of desktop daemons. LXSession
# application autostart is disabled in desktop.conf; Flameshot's own
# startup-launch setting stays disabled so exactly one instance runs.
lxsession --session=qtile &

# Monitor layout via the step-01 helper: same generic logic as the hotplug
# hook (internal primary @ max rate, externals left of it, --auto fallback).
# Foreground: xwallpaper below must paint after the framebuffer settles,
# or the image lands on stale geometry (smeared panel).
python3 "$HOME/.config/qtile/config_parts/monitors.py"

# Launch only if installed — keeps fresh machines boot-noise-free.
try_launch() {
  command -v "$1" >/dev/null 2>&1 && "$@" &
}

# Compositor needs a real GPU: skip in VMs/containers (software rendering
# burns CPU for no gain) and when no DRI device exists. Fail open when
# systemd-detect-virt is missing (assume bare metal, today's behavior).
if { ! command -v systemd-detect-virt >/dev/null 2>&1 || ! systemd-detect-virt --quiet; } \
  && compgen -G '/dev/dri/card*' >/dev/null; then
  try_launch picom
fi
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
# whole framebuffer. Empty/missing state file runs nothing (-r). Arrays
# keep wallpapers with spaces intact across login/hotplug.
if [ -s "$HOME/.xwallpaper" ]; then
  IFS= read -r wallpaper <"$HOME/.xwallpaper"
  wp_args=()
  while IFS= read -r out; do
    wp_args+=(--output "$out" --zoom "$wallpaper")
  done < <(xrandr --query | awk '/ connected/{print $1}')
  xwallpaper "${wp_args[@]}" &
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
