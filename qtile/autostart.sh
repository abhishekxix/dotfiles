#! /usr/bin/env bash

lxsession &
picom &
mictray &
xbindkeys &
flameshot &
deadd-notification-center &
volumeicon &
copyq &
nm-applet &
blueman-applet &
xargs xwallpaper --stretch <~/.xwallpaper &
# find /home/abhi/dotfiles/wallpapers -type f | shuf -n 1 | xargs xwallpaper --stretch &
