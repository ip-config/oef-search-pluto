#!/bin/python3
import sys
import subprocess

args = " ".join(sys.argv[1:])

search_port = "20000"
core_port = "10000"

img = "oef-search-tmp"
name = None

for i in range(len(sys.argv)):
    if sys.argv[i] == "--search_port":
        search_port = sys.argv[i+1]
    elif sys.argv[i] == "--core_port":
        core_port = sys.argv[i+1]
    elif sys.argv[i] == "--name":
        name = sys.argv[i+1]

print("Ports to expose: search={}, core={} for node={}".format(search_port, core_port, name))

cmd = [
    "docker",
    "run",
    "-it",
    "--name",
    "FullNode"+name,
    "--network=oef_search_net",
    "-p",
    search_port+":"+search_port,
    #"--expose="+core_port,
    img,
]

cmd.extend(sys.argv[1:])

print(cmd)

subprocess.run(cmd, check=True)