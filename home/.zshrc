# Shell options.
set -o extended_history
set -o hist_expire_dups_first
set -o hist_ignore_dups
set -o hist_ignore_space
set -o hist_verify
set -o share_history
set -o inc_append_history
unsetopt append_history
set -o auto_cd
set -o auto_pushd
set -o pushd_ignore_dups
set -o pushdminus

# env variables.
export EDITOR=vim
export WINIT_X11_SCALE_FACTOR=1

# keybinds
bindkey '^H' backward-kill-word
bindkey "^[[1;5D" backward-word
bindkey "^[[1;5C" forward-word

# History.
HISTFILE="$HOME/.zsh_history"
HISTSIZE=120000
SAVEHIST=100000

fpath=( $HOME/.zsh/functions $HOME/.zsh/zsh-completions/src $fpath )

autoload -Uz compinit
mkdir -p "${XDG_CACHE_HOME:-$HOME/.cache}/zsh" 2>/dev/null
compinit -C -d "${XDG_CACHE_HOME:-$HOME/.cache}/zsh/zcompdump-$ZSH_VERSION"

# Plugins (guarded: provisioning may be partial). Autosuggestions loads
# early; syntax highlighting sources last at the end of this file so every
# widget (including fzf key bindings below) initializes first.
[ -f "$HOME/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh" ] && source "$HOME/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh"

# ### aliases ###
alias ls='ls --color=auto'

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
_dir_preview() { command -v eza >/dev/null 2>&1 && print -r 'eza --tree --level=2 {}' || print -r 'ls -R {}'; }
export FZF_DEFAULT_OPTS="--info=inline --border --margin=1 --padding=1"
# Previews apply only to file/directory selection, never to history or
# arbitrary input; each preview degrades when its command is unavailable.
if command -v bat >/dev/null 2>&1 || command -v batcat >/dev/null 2>&1; then
  export FZF_CTRL_T_OPTS="--preview '$(_bat_preview)'"
fi
export FZF_ALT_C_OPTS="--preview '$(_dir_preview)'"

# Starship setup (guarded: provisioning may be partial)
if command -v starship >/dev/null 2>&1; then
  eval "$(starship init zsh)"
fi

# GPG agent needs the live terminal, refreshed on attach/reattach.
tty=$(tty 2>/dev/null) && export GPG_TTY="$tty"; unset tty

# fnm setup
if command -v fnm >/dev/null 2>&1; then
  eval "$(fnm env --use-on-cd --shell zsh)"
fi

# zoxide directory jumping (guarded) and direnv (guarded; inactive until
# a directory is explicitly allowed with `direnv allow`).
if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init zsh)"
fi
if command -v direnv >/dev/null 2>&1; then
  eval "$(direnv hook zsh)"
fi

# Syntax highlighting runs last so earlier widgets are already defined.
[ -f "$HOME/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ] && source "$HOME/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
