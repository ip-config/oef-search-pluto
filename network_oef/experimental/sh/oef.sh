#!/usr/bin/env sh

if [[ "$1" = "node" ]];then
    ./node "${@:2}"
elif [[ "$1" = "director" ]];then
    ./demo/demo_director "${@:2}"
else
    ./node "$@"
fi

sh