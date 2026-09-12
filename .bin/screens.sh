#!/bin/sh
# SUPERSEDED EMERGENCY FALLBACK — not current automation.
# Kept only for manual recovery on this specific hardware pair when the
# generic monitor logic (config_parts/monitors.py) cannot run. Do not wire
# this into autostart or hooks.
xrandr --output HDMI-0 --mode 2560x1440 --pos 0x0 --rotate normal --output eDP-1-1 --primary --mode 1920x1080 --pos 2560x360 --rotate normal
# xrandr --output HDMI-1-0 --mode 2560x1440 --pos 0x0 --rotate normal --output eDP-1 --primary --mode 1920x1080 --pos 2560x360 --rotate normal
