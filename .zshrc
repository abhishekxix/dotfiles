# Shell options.
set -o autocd
set -o extended_history
set -o hist_expire_dups_first
set -o hist_ignore_dups
set -o hist_ignore_space
set -o auto_cd
set -o auto_pushd
set -o pushd_ignore_dups
set -o pushdminus

# env variables.
export EDITOR=vim
export NODE_ENV='development'
export WINIT_X11_SCALE_FACTOR=1

# History.
HISTFILE="$HOME/.zsh_history"
HISTSIZE=100000
SAVEHIST=100000

fpath=( $HOME/.zsh/functions $HOME/.zsh/zsh-completions/src $fpath )

autoload -Uz compinit
compinit

# Plugins.
source "$HOME/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
source "$HOME/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh"

# ### aliases ###
alias ls='ls --color=auto'
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
alias mkdir='mkdir -pv'

# Delete complete word with ctrl+bsp
bindkey '^H' backward-kill-word

# FZF setup
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
export FZF_DEFAULT_OPTS="--info=inline --preview 'batcat -n --color=always {}' --border --margin=1 --padding=1"
source /usr/share/doc/fzf/examples/key-bindings.zsh
source /usr/share/doc/fzf/examples/completion.zsh

# Starship setup
eval "$(starship init zsh)"

#fnm setup
eval "$(fnm env --use-on-cd --shell zsh)"
