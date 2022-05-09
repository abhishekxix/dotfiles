#!/bin/bash -e
source $HOME/.bash_profile

cd /home/abhi/dotfiles/
git switch auto-push
git add .
git commit -m 'auto push'
git push
