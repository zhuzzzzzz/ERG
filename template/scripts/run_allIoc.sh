#!/bin/bash

# 仅对有图形界面的操作系统使用

script_abs=$(readlink -f "$0")
script_dir=$(dirname $script_abs)

# top path
#top_path=$script_dir/../IOC

cd $top_path

for item in `ls`
do
	echo `readlink -f $item`
	echo $item
	if test -d `readlink -f $item` -a -d $item/iocBoot
	then
		echo $item is a dir
		cd $item/iocBoot
		for item in `ls`
		do
			if test -x ${item}/st.cmd
			then
				gnome-terminal -- bash -c "cd ${item};./st.cmd;exec bash"
			fi
		done
	fi
	cd $top_path
done

