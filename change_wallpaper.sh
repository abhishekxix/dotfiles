#!/bin/bash -e
source $HOME/.bash_profile

declare -x DISPLAY=":0"
declare -x XAUTHORITY="/home/abhi/.Xauthority"

wallpaper=$(find /home/abhi/wallpapers -type f | shuf -n 1)
echo $wallpaper > ~/.xwallpaper
echo $wallpaper | xargs xwallpaper --stretch
