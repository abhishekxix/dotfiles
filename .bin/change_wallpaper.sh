#!/usr/bin/env bash
set -Eeuo pipefail

wallpaper_dir="$HOME/Pictures/wallpapers"
state_file="$HOME/.xwallpaper"

if (($# > 1)); then
  printf 'Usage: %s [wallpaper]\n' "$0" >&2
  exit 2
fi

if (($# == 1)); then
  wallpaper=$1
elif ! IFS= read -r -d '' wallpaper < <(
  find "$wallpaper_dir" -type f -not -path '*/.git/*' -print0 | shuf -z -n 1
); then
  printf 'No wallpapers found in %s\n' "$wallpaper_dir" >&2
  exit 1
fi

if [[ ! -f $wallpaper ]]; then
  printf 'Wallpaper does not exist: %s\n' "$wallpaper" >&2
  exit 1
fi

xwallpaper --stretch "$wallpaper"
printf '%s\n' "$wallpaper" >"$state_file"