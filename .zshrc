# env variables
export EDITOR=nvim

# plugins=(git zsh-syntax-highlighting zsh-autosuggestions)

source "$HOME/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
source "$HOME/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh"

# ### aliases ###
# directory and file operations
alias ls='ls --color=auto'
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
alias mkdir='mkdir -pv'

#delete complete word with ctrl+bsp
bindkey '^H' backward-kill-word

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm

export NODE_ENV='development'

WINIT_X11_SCALE_FACTOR=1

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

export FZF_DEFAULT_OPTS="--info=inline --preview 'batcat -n --color=always {}' --border --margin=1 --padding=1"
eval "$(starship init zsh)"
