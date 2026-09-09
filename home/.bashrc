# shellcheck shell=bash disable=SC1091
#
# ~/.bashrc
#

# Shared PATH setup (idempotent; also sourced by .zshenv / .profile).
# Sourced before the interactive guard so non-interactive bash (scripts,
# `bash -c`) finds user tools too.
[ -f "$HOME/.path" ] && . "$HOME/.path"

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
PS1='[\u@\h \W]\$ '

# fnm owns node (lazy: env only on first node/fnm use; replaces system nvm)
if command -v fnm >/dev/null 2>&1; then
  _fnm_lazy() { unset -f node npm npx fnm 2>/dev/null; eval "$(fnm env --use-on-cd --shell bash)"; }
  node() { _fnm_lazy; node "$@"; }
  npm() { _fnm_lazy; npm "$@"; }
  npx() { _fnm_lazy; npx "$@"; }
  fnm() { _fnm_lazy; fnm "$@"; }
fi

# bash-completion when installed
[ -f /usr/share/bash-completion/bash_completion ] && . /usr/share/bash-completion/bash_completion
