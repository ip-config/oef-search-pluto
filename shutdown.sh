#!/bin/sh

docker ps | grep oef-search | cut -d' ' -f1 | xargs docker kill
