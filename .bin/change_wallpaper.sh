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
  find "$wallpaper_dir" -type f -not -path '*/.git/*' -not -iname '*.svg' -print0 | shuf -z -n 1
); then
  printf 'No wallpapers found in %s\n' "$wallpaper_dir" >&2
  exit 1
fi

if [[ ! -f $wallpaper ]]; then
  printf 'Wallpaper does not exist: %s\n' "$wallpaper" >&2
  exit 1
fi

if [[ ${wallpaper,,} == *.svg ]]; then
  printf 'SVG wallpapers are not supported: %s\n' "$wallpaper" >&2
  exit 1
fi

# --zoom crops to fill per-output (aspect kept); --stretch smears one
# 16:9 image across the whole 4480x1440 framebuffer (the bug in #2's photo).
args=()
while IFS= read -r out; do
  args+=(--output "$out" --zoom "$wallpaper")
done < <(xrandr --query | awk '/ connected/{print $1}')
xwallpaper "${args[@]}"
printf '%s\n' "$wallpaper" >"$state_file"