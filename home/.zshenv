export GTK2_RC_FILES="$HOME/.gtkrc-2.0"
export QT_QPA_PLATFORMTHEME="qt6ct"

# Shared PATH setup (idempotent; also sourced by .profile / .bashrc).
[ -f "$HOME/.path" ] && . "$HOME/.path"
