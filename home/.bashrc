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

# history: large, shared feel, verify expansions (matches zsh opts)
HISTSIZE=100000
HISTFILESIZE=100000
HISTCONTROL=ignoredups:erasedups
shopt -s histappend histverify 2>/dev/null

# Share history across live shells without clobbering existing prompt hooks.
_dotfiles_share_history() {
  history -a
  history -c
  history -r
  return 0
}
case ";${PROMPT_COMMAND:+;${PROMPT_COMMAND};};" in
  *";_dotfiles_share_history;"*) ;;
  *) PROMPT_COMMAND="${PROMPT_COMMAND:+${PROMPT_COMMAND}; }_dotfiles_share_history" ;;
esac

# GPG agent needs the live terminal, refreshed per prompt (covers reattach).
_dotfiles_refresh_gpg_tty() {
  _t=$(tty 2>/dev/null) && export GPG_TTY="$_t"
  unset _t
  return 0
}
case ";${PROMPT_COMMAND:+;${PROMPT_COMMAND};};" in
  *";_dotfiles_refresh_gpg_tty;"*) ;;
  *) PROMPT_COMMAND="${PROMPT_COMMAND:+${PROMPT_COMMAND}; }_dotfiles_refresh_gpg_tty" ;;
esac

alias ls='ls --color=auto'
PS1='[\u@\h \W]\$ '

# fnm setup
if command -v fnm >/dev/null 2>&1; then
  eval "$(fnm env --use-on-cd --shell bash)"
fi

# bash-completion when installed
[ -f /usr/share/bash-completion/bash_completion ] && . /usr/share/bash-completion/bash_completion
