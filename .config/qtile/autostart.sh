#! /usr/bin/env bash

lxsession  --session=qtile &

# gnome-keyring-daemon --start --components=pkcs11,secrets,ssh &

picom &
# lxqt-powermanagement &
xbindkeys &
flameshot &
# deadd-notification-center &
# dunst &
volumeicon &
copyq &
nm-applet &
# blueberry &
blueman-applet &
xscreensaver --nosplash &
xargs xwallpaper --stretch < ~/.xwallpaper &
mictray &
# find /home/abhi/dotfiles/wallpapers -type f | shuf -n 1 | xargs xwallpaper --stretch &
