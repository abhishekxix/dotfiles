#!/bin/bash -e
source $HOME/.zshenv

files=()

cd ${HOME}/Pictures/wallpapers;

for file in *.*
do
	if [[ -f $file ]]
	then
		files=("${files[@]}" "$file")
	fi
done

# echo "${files[@]}"
wallpaper=${files[0]}
echo $wallpaper > ~/.xwallpaper
