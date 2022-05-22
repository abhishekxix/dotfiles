#! /usr/bin/env bash

lxsession &
picom &
mictray &
xbindkeys &
flameshot &
# deadd-notification-center &
dunst &
volumeicon &
copyq &
nm-applet &
blueberry &
xscreensaver --nosplash &
xargs xwallpaper --stretch <~/.xwallpaper &
# find /home/abhi/dotfiles/wallpapers -type f | shuf -n 1 | xargs xwallpaper --stretch &
