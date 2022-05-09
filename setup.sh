#!/bin/bash

cd $1

DOTFILES_DIRECTORY=${pwd}
DOTCONFIG_SOURCES=()

SRC_LIST=$(ls -a)
HOME_CONFIGS=(
  ".git" ".gitignore" ".git"
  ".bashrc"
  ".gtkrc-2"
  ".p10k.zsh" ".zshrc" ".zshenv"
)
echo "${HOME_CONFIGS[*]}"

# for SOURCE in ${SRCLIST[@]}
# do
#   if [[ "$SOURCE" =~  ]]
#   then echo $SOURCE
#   fi
# end

# # TARGET=$HOME/.config
# TARGET = ${pwd}/.config

# mkdir $TARGET

# for thing in $SRC;
# do
#   ln -sf thing
