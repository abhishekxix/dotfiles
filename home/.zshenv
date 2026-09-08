export GTK2_RC_FILES="$HOME/.gtkrc-2.0"
export QT_QPA_PLATFORMTHEME="qt6ct"

[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"

# opencode installs to ~/.opencode/bin (the ansible installer runs the
# upstream script with --no-modify-path so it never touches these dotfiles).
[ -d "$HOME/.opencode/bin" ] && export PATH="$HOME/.opencode/bin:$PATH"
