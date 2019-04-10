#!/usr/bin/env sh

export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

bazel run network_oef/experimental/python/demo:search_network -- "$@"