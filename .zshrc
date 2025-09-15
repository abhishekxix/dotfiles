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

autoload -Uz compinit
compinit

# Plugins.
source "$HOME/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
source "$HOME/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh"
fpath=( $HOME/.zsh/zsh-completions/src $fpath )

# ### aliases ###
alias ls='ls --color=auto'
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
alias mkdir='mkdir -pv'

# Delete complete word with ctrl+bsp
bindkey '^H' backward-kill-word

# nvm Setup.
lazy-nvm() {
	unset -f nvm node npm npx
	export NVM_DIR="$HOME/.nvm"
	[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
}

nvm() {
	lazy-nvm
	nvm "$@"
}

node() {
	lazy-nvm
	node "$@"
}

npm() {
	lazy-nvm
	npm "$@"
}

npx() {
	lazy-nvm
	npx "$@"
}

# FZF setup
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
export FZF_DEFAULT_OPTS="--info=inline --preview 'batcat -n --color=always {}' --border --margin=1 --padding=1"

# Starship setup
eval "$(starship init zsh)"
