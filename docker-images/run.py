#!/usr/bin/env python3
import sys
import subprocess

# Before running;
#   docker network create -d bridge oef_search_net

args = " ".join(sys.argv[1:])

search_port = "20000"
core_port = "10000"
http_port = None

img = "oef-search:latest"
name = None

for i in range(len(sys.argv)):
    if sys.argv[i] == "--search_port":
        search_port = sys.argv[i+1]
    elif sys.argv[i] == "--core_port":
        core_port = sys.argv[i+1]
    elif sys.argv[i] == "--node_key":
        name = sys.argv[i+1]
    elif sys.argv[i] == "--http_port":
        http_port = sys.argv[i+1]
    elif sys.argv[i] == "--image":
        img = sys.argv[i+1]

print("Ports to expose: search={}, core={} for node={}".format(search_port, core_port, name))

cmd = [
    "docker",
    "run",
    "--rm",
    "-it",
    "--name",
    "node_"+name,
    "--network=oef_search_net",
    "-p",
    search_port+":"+search_port,
    "-p",
    core_port+":"+core_port,
]

if http_port is not None:
    cmd.extend([
        "--publish",
        http_port+":"+http_port
    ])
cmd.append(img)

cmd.extend(sys.argv[1:])

print(cmd)

subprocess.run(cmd, check=True)
