#!/usr/bin/env sh

if [[ "$1" = "node" ]];then
    ./node `echo "$@" | sed -e "s/node//g"`
elif [[ "$1" = "director" ]];then
    ./demo/demo_director `echo "$@" | sed -e "s/director//g"`
else
    ./node "$@"
fi

sh