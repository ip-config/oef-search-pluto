import argparse
from typing import List, Dict
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor
import atexit
import functools


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
    print('Generating source archive... (location: {})'.format(path))
    cmd = [
        'git-archive-all', os.path.join(path, 'project.tar.gz')
    ]
    subprocess.check_call(cmd, cwd=path)
    print('Generating source archive...complete')
    cmd = [
        'docker',
        'build',
        '-t', image_tag,
        '.',
    ]
    subprocess.check_call(cmd, cwd=path)


def kill_containers(names: List[str]):
    for name in names:
        try:
            subprocess.check_call(["docker", "kill", name])
        except Exception as e:
            print("Failed to kill container {} because: {}".format(name, str(e)))


def container_main(num_of_nodes: int, links: List[str], http_ports: Dict[int, int] = {}, ssl_cert: str = "", *,
         image_tag: str, do_build: bool):
    path = get_workdir()
    if do_build:
        build(image_tag, path)

    pool = ThreadPoolExecutor(num_of_nodes)

    CORE_PORT = 10000
    SEARCH_PORT = 20000
    dap_port = 30000
    DIRECTOR_PORT = 40000

    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "-it",
        "--network=oef_search_net",
    ]

    names = []
    api_targets = []
    director_targets = []
    for i in range(num_of_nodes):
        http_port = http_ports.get(i, -1)
        search_port = SEARCH_PORT+i
        core_port = CORE_PORT+i
        director_port = DIRECTOR_PORT + i
        args = [
            "--node_key", "Search{}".format(i),
            "--core_key", "Core{}".format(i),
            "--ip", "0.0.0.0",
            "--search_port", str(search_port),
            "--core_port", str(core_port),
            "--dap_port", str(dap_port+i),
            "--director_api_port", str(director_port),
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
        node_name = "oef_node"+str(i)

        cmd = []
        cmd.extend(docker_cmd)
        cmd.extend([
            "--name",
            node_name,
            "-p",
            str(search_port) + ":" + str(search_port),
            "-p",
            str(core_port) + ":" + str(core_port),
        ])
        i += 1

        if http_port != -1:
            cmd.extend([
                "-p",
                str(http_port) + ":" + str(http_port)
            ])
        cmd.append(image_tag)
        cmd.extend([
            "node",
            "no_sh"
        ])
        cmd.extend(args)
        print("EXECUTE: ", cmd)
        pool.submit(subprocess.check_call, cmd)
        names.append(node_name)
        api_targets.append(node_name+":"+str(search_port))
        director_targets.append(node_name+":"+str(director_port))

    loc_director_cmd = []
    loc_director_cmd.extend(docker_cmd)
    loc_director_cmd.extend([
        image_tag,
        "director",
        "no_sh",
        "--type",
        "location",
        "--targets"
    ])
    loc_director_cmd.extend(director_targets)
    subprocess.check_call(loc_director_cmd)

    weather_director_cmd = []
    weather_director_cmd.extend(docker_cmd)
    weather_director_cmd.extend([
        image_tag,
        "director",
        "no_sh",
        "--type",
        "weather_agent",
        "--targets"
    ])
    weather_director_cmd.extend(api_targets)
    subprocess.check_call(weather_director_cmd)

    pool.shutdown(wait=True)

    atexit.register(functools.partial(kill_containers, names))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DEMO search network')
    parser.add_argument("--num_nodes", required=True, type=int, help="Number of full demo nodes")
    parser.add_argument("--links", nargs='*',  type=str,
                        help="Node connection list: id1:id2 ... (id: 0...num_nodes-1)")
    parser.add_argument("--http_port_map", nargs='*', type=str, help="id:http_port (id: 0...num_nodes-1)")
    parser.add_argument("--image", "-i", type=str, default="oef-search:latest", help="Docker image name")
    parser.add_argument("--build", "-b", action="store_true", help="Build docker image")

    args = parser.parse_args()

    http_port_map = {}
    for e in args.http_port_map:
        k, p = e.split(":")
        http_port_map[int(k)] = int(p)

    container_main(args.num_nodes, args.links, http_port_map, "/app/server.pem", image_tag=args.image,
                   do_build=args.build)
