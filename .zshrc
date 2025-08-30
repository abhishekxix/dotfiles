# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# env variables
export EDITOR=nvim

plugins=(git zsh-syntax-highlighting zsh-autosuggestions)

source $ZSH/oh-my-zsh.sh

# ### aliases ###
# directory and file operations
alias ls='ls --color=auto'
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
alias mkdir='mkdir -pv'
alias vimdiff='nvim -d'
alias vim='nvim'

#delete complete word with ctrl+bsp
bindkey '^H' backward-kill-word

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm

export NODE_ENV='development'

WINIT_X11_SCALE_FACTOR=1

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

export FZF_DEFAULT_OPTS="--info=inline --preview 'batcat -n --color=always {}' --border --margin=1 --padding=1"
