#!/bin/sh
# The docker group exists only after install; membership takes effect at next login.
# Idempotent: exits 0 when DOTFILES_USER is already a member.
: "${DOTFILES_USER:?hook requires DOTFILES_USER}"
if id -nG "$DOTFILES_USER" | tr ' ' '\n' | grep -qx docker; then
    exit 0
fi
usermod -aG docker "$DOTFILES_USER"
