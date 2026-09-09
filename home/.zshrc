# Shell options.
set -o extended_history
set -o hist_expire_dups_first
set -o hist_ignore_dups
set -o hist_ignore_space
set -o hist_verify
set -o share_history
set -o append_history
set -o inc_append_history
set -o auto_cd
set -o auto_pushd
set -o pushd_ignore_dups
set -o pushdminus

# env variables.
export EDITOR=nvim
export WINIT_X11_SCALE_FACTOR=1

# keybinds
bindkey '^H' backward-kill-word
bindkey "^[[1;5D" backward-word
bindkey "^[[1;5C" forward-word

# History.
HISTFILE="$HOME/.zsh_history"
HISTSIZE=100000
SAVEHIST=100000

fpath=( $HOME/.zsh/functions $HOME/.zsh/zsh-completions/src $fpath )

autoload -Uz compinit
compinit -C -d "${XDG_CACHE_HOME:-$HOME/.cache}/zsh/zcompdump-$ZSH_VERSION"

# Plugins.
source "$HOME/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
source "$HOME/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh"

# ### aliases ###
alias ls='ls --color=auto'
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
alias mkdir='mkdir -pv'

# Functions
help() {
  bash -c "help $1"
}

# FZF setup (source once: user file preferred, system examples as fallback)
if command -v fzf >/dev/null 2>&1; then
  if [ -f ~/.fzf.zsh ]; then
    source ~/.fzf.zsh
  else
    [ -f /usr/share/doc/fzf/examples/key-bindings.zsh ] && source /usr/share/doc/fzf/examples/key-bindings.zsh
    [ -f /usr/share/doc/fzf/examples/completion.zsh ] && source /usr/share/doc/fzf/examples/completion.zsh
  fi
fi
_bat_preview() { command -v bat >/dev/null 2>&1 && print -r 'bat -n --color=always {}' || print -r 'batcat -n --color=always {}'; }
export FZF_DEFAULT_OPTS="--info=inline --preview '$(_bat_preview)' --border --margin=1 --padding=1"

# Starship setup
eval "$(starship init zsh)"

# fnm setup (lazy: env only on first node/fnm use)
if command -v fnm >/dev/null 2>&1; then
  _fnm_lazy() { unfunction node npm npx fnm 2>/dev/null; eval "$(fnm env --use-on-cd --shell zsh)"; }
  node() { _fnm_lazy; node "$@"; }
  npm() { _fnm_lazy; npm "$@"; }
  npx() { _fnm_lazy; npx "$@"; }
  fnm() { _fnm_lazy; fnm "$@"; }
fi
