#!/bin/python3
import sys
import subprocess

args = " ".join(sys.argv[1:])

search_port = "20000"
core_port = "10000"

img = "oef-search-tmp"

for i in range(len(sys.argv)):
    if sys.argv[i] == "--search_port":
        search_port = sys.argv[i+1]
    elif sys.argv[i] == "--core_port":
        core_port = sys.argv[i+1]

print("Ports to expose: search={}, core={}".format(search_port, core_port))

cmd = [
    "docker",
    "run",
    "-it",
    "--expose",
    search_port,
    "--expose",
    core_port,
    img,
]

cmd.extend(sys.argv[1:])

print(cmd)

subprocess.run(cmd, check=True)