from typing import List, Dict
import time
import subprocess
import os
import shutil
from concurrent.futures import ThreadPoolExecutor


def get_workdir(start_dir: str = ""):
    if start_dir == "":
        start_dir = os.path.abspath(os.path.dirname(__file__))
    if start_dir == "/":
        print("workspace directory not found")
        return ""
    files = os.listdir(start_dir)
    result = next((x for x in files if x.find("docker-images") != -1), None)
    if result is not None:
        return start_dir + "/docker-images"
    return get_workdir(os.path.abspath(os.path.join(start_dir, '..')))


def build(image_tag: str, path: str):
    try:
        subprocess.check_call(["docker", "network", "create", "-d", "bridge", "oef_search_net"])
    except Exception as e:
        print("Docker network creation failed: ", str(e))
    build_dir = path+"/build"
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    shutil.copyfile(path+"/Dockerfile", build_dir+"/Dockerfile")
    shutil.copyfile(path+"/project.tar.gz", build_dir+"/project.tar.gz")
    cmd = [
        'docker',
        'build',
        '-t', image_tag,
        '.',
    ]
    subprocess.check_call(cmd, cwd=build_dir)


def main(num_of_nodes: int, links: List[str], http_ports: Dict[int, int] = {}, ssl_cert: str = "", *,
         image_tag: str, do_build: bool):
    path = get_workdir()
    if do_build:
        build(image_tag, path)

    pool = ThreadPoolExecutor(num_of_nodes)

    CORE_PORT = 10000
    SEARCH_PORT = 20000
    dap_port = 30000
    director_port = 40000

    for i in range(num_of_nodes):
        http_port = http_ports.get(i, -1)
        search_port = SEARCH_PORT+i
        core_port = CORE_PORT+i
        args = [
            "--node_key", "Search{}".format(i),
            "--core_key", "Core{}".format(i),
            "--ip", "0.0.0.0",
            "--search_port", str(search_port),
            "--core_port", str(core_port),
            "--dap_port", str(dap_port+i),
            "--director_api_port", str(director_port+i),
            "--http_port", str(http_port),
            "--ssl_certificate", ssl_cert
        ]
        peers = []
        for l in links:
            if l.find(str(i)) == -1:
                continue
            i1, i2 = l.split(":")
            target = i1 if i1 != str(i) else i2
            target = int(target)
            host = "oef_node{}".format(target)
            port = SEARCH_PORT+target
            peers.append("Search{}:".format(target)+host+":"+str(port))
        args.append("--search_peers")
        args.extend(peers)

        cmd = [
            "docker",
            "run",
            "--rm",
            "-it",
            "--name",
            "oef_node" + str(i),
            "--network=oef_search_net",
            "-p",
            str(search_port) + ":" + str(search_port),
            "-p",
            str(core_port) + ":" + str(core_port),
        ]
        i += 1

        if http_port != -1:
            cmd.extend([
                "-p",
                str(http_port) + ":" + str(http_port)
            ])
        cmd.append(image_tag)
        cmd.extend(args)
        print("EXECUTE: ", cmd)
        pool.submit(subprocess.check_call, cmd)
