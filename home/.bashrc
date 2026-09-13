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

alias ls='ls --color=auto'
PS1='[\u@\h \W]\$ '

# fnm setup
if command -v fnm >/dev/null 2>&1; then
  eval "$(fnm env --use-on-cd --shell bash)"
fi

# FZF setup (source once: user file preferred, system examples as fallback)
# shellcheck disable=SC1090
if command -v fzf >/dev/null 2>&1; then
  if [ -f ~/.fzf.bash ]; then
    source ~/.fzf.bash
  else
    [ -f /usr/share/doc/fzf/examples/key-bindings.bash ] && source /usr/share/doc/fzf/examples/key-bindings.bash
    [ -f /usr/share/doc/fzf/examples/completion.bash ] && source /usr/share/doc/fzf/examples/completion.bash
  fi
fi
_bat_preview() { command -v bat >/dev/null 2>&1 && printf '%s\n' 'bat -n --color=always {}' || printf '%s\n' 'batcat -n --color=always {}'; }
export FZF_DEFAULT_OPTS="--info=inline --border --margin=1 --padding=1"
# Scoped previews: file/dir widgets only (Ctrl-T/Alt-C). Ctrl-R stays
# preview-free. Revert this hunk alone to restore the global preview.
# single-quoted preview cmd is intentional: fzf splits opts itself
# shellcheck disable=SC2089
FZF_CTRL_T_OPTS="--preview '$(_bat_preview)'"
# shellcheck disable=SC2090
export FZF_CTRL_T_OPTS
# shellcheck disable=SC2089
FZF_ALT_C_OPTS="--preview '$(_bat_preview)'"
# shellcheck disable=SC2090
export FZF_ALT_C_OPTS

# Starship setup (guarded: replaces PS1 when present)
if command -v starship >/dev/null 2>&1; then
  eval "$(starship init bash)"
fi

# zoxide setup (guarded: keep shell usable when missing)
if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init bash)"
fi

# direnv setup (guarded: keep shell usable when missing)
if command -v direnv >/dev/null 2>&1; then
  eval "$(direnv hook bash)"
fi

# bash-completion when installed
[ -f /usr/share/bash-completion/bash_completion ] && . /usr/share/bash-completion/bash_completion
