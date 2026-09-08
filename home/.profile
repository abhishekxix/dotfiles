# shellcheck shell=sh disable=SC1091
# if running bash
if [ -n "$BASH_VERSION" ]; then
	# include .bashrc if it exists
	if [ -f "$HOME/.bashrc" ]; then
		. "$HOME/.bashrc"
	fi
fi

# Shared PATH setup (idempotent; also sourced by .zshenv / .bashrc).
[ -f "$HOME/.path" ] && . "$HOME/.path"

export QT_QPA_PLATFORMTHEME="qt6ct"
