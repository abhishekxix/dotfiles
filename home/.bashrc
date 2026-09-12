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

# fzf key bindings with scoped previews: file preview for Ctrl-T file
# selection, directory preview for Alt-C, none for history/arbitrary input.
if command -v fzf >/dev/null 2>&1; then
  if [ -f ~/.fzf.bash ]; then
    . ~/.fzf.bash
  else
    [ -f /usr/share/doc/fzf/examples/key-bindings.bash ] && . /usr/share/doc/fzf/examples/key-bindings.bash
    [ -f /usr/share/doc/fzf/examples/completion.bash ] && . /usr/share/doc/fzf/examples/completion.bash
  fi
  if command -v bat >/dev/null 2>&1; then
    export FZF_CTRL_T_OPTS="--preview 'bat -n --color=always {}'"
  elif command -v batcat >/dev/null 2>&1; then
    export FZF_CTRL_T_OPTS="--preview 'batcat -n --color=always {}'"
  fi
  if command -v eza >/dev/null 2>&1; then
    export FZF_ALT_C_OPTS="--preview 'eza --tree --level=2 {}'"
  else
    export FZF_ALT_C_OPTS="--preview 'ls -R {}'"
  fi
fi

# fnm setup
if command -v fnm >/dev/null 2>&1; then
  eval "$(fnm env --use-on-cd --shell bash)"
fi

# zoxide directory jumping (guarded) and direnv (guarded; inactive until
# a directory is explicitly allowed with `direnv allow`).
if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init bash)"
fi
if command -v direnv >/dev/null 2>&1; then
  eval "$(direnv hook bash)"
fi

# bash-completion when installed
[ -f /usr/share/bash-completion/bash_completion ] && . /usr/share/bash-completion/bash_completion
