#!/usr/bin/env bash
set -Eeuo pipefail

# Session power menu. Lock and Suspend mirror the xbindkeys bindings
# (~/.xbindkeysrc): lock first, then suspend, so resume lands on the locker.
choice=$(
  printf '%s\n' Lock Logout Suspend Reboot Shutdown |
    rofi -dmenu -i -p power
) || exit 0

case "$choice" in
Lock) lxlock ;;
Logout) qtile cmd-obj -o cmd -f shutdown ;;
Suspend) lxlock && systemctl suspend ;;
Reboot) systemctl reboot ;;
Shutdown) systemctl poweroff ;;
*) exit 0 ;;
esac
