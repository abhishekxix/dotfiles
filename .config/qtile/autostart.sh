#! /usr/bin/env bash

export XDG_CURRENT_DESKTOP=qtile
export XDG_SESSION_DESKTOP=qtile
export XDG_SESSION_TYPE=x11

lxsession --session=qtile &

gnome-keyring-daemon --start --login --components=pkcs11,secrets,ssh

xrandr --output HDMI-0 --mode 2560x1440 --rate 75 --pos 0x0 --rotate normal --output eDP-1-1 --primary --mode 1920x1080 --rate 120 --pos 2560x360 --rotate normal

export WINIT_X11_SCALE_FACTOR=1

picom &
xbindkeys &
flameshot &
dunst &
volumeicon &
copyq &
nm-applet &
# blueberry &
blueman-applet &
xscreensaver --nosplash &
xargs xwallpaper --stretch <~/.xwallpaper &
# mictray &

# Set the audio settings.
pactl load-module module-echo-cancel source_master=alsa_input.pci-0000_00_1f.3.analog-stereo sink_master=alsa_output.pci-0000_00_1f.3.analog-stereo aec_method=webrtc aec_args="analog_gain_control=0 digital_gain_control=0" use_master_format=yes
pactl set-default-source echo-cancel-source
