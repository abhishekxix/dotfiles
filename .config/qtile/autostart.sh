#! /usr/bin/env bash

lxsession  --session=qtile &

xrandr --output HDMI-0 --mode 2560x1440 --pos 1920x0 --rotate normal --output eDP-1-1 --primary --mode 1920x1080 --pos 0x360 --rotate normal

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
xargs xwallpaper --stretch < ~/.xwallpaper &
# mictray &