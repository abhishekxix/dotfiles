#!/bin/bash -e
source "$HOME/.zshenv"

#declare -x DISPLAY=":0"
#declare -x XAUTHORITY="/home/abhi/.Xauthority"

wallpaper=""

# Get wallpaper from script arg or pick a random one from the wallpapers directory
if [[ -n "$1" ]]; then
  wallpaper=$1
else
  wallpaper=$(find "$HOME/Pictures/wallpapers" -type f -not -path "*.git*" | shuf -n 1)
fi

# wallpaper=$(find /home/abhi/Pictures/wallpapers -type f -not -path "*.git*" | shuf -n 1)
echo "$wallpaper" >~/.xwallpaper
echo "$wallpaper" | xargs xwallpaper --stretch
