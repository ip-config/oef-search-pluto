#!/usr/bin/env sh

arguments=`echo "$@" | sed -e "s/no_sh//g"`

if [[ "$1" = "node" ]];then
    ./node `echo "$arguments" | sed -e "s/^node//g"`
elif [[ "$1" = "director" ]];then
    ./demo/demo_director `echo "$arguments" | sed -e "s/^director//g"`
else
    ./node "$arguments"
fi

if [[ "$2" != "no_sh" ]]; then
    sh
fi