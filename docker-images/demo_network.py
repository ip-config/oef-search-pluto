import argparse
from typing import List, Dict
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor
import atexit
import functools
import os
import gensim
import gensim.downloader
import json
import nltk


def gensim_setup():
    model = "glove-wiki-gigaword-50"
    gensim_dir = os.path.expanduser("~/gensim-data/")
    model_bin = gensim_dir + model + ".bin"
    if os.path.exists(gensim_dir) and os.path.exists(model_bin):
        return
    gmodel = gensim.downloader.load(model)
    gmodel.init_sims(replace=True)
    gmodel.save(model_bin)


def nltk_setup():
    nltk_dir = os.path.expanduser("~/nltk-data/")
    if not os.path.exists(nltk_dir+"corpora/stopwords"):
        nltk.download('stopwords')
    if not os.path.exists(nltk_dir+"tokenizers/punkt"):
        nltk.download('punkt', quiet=True)
    if not os.path.exists(nltk_dir+"corpora/wordnet"):
        nltk.download('wordnet', quiet=True)


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


def build(image_tag: str, path: str, fast: bool):
    if fast:
        print("FAST DOCKER RE-BUILD")
    else:
        print("DOCKER BUILD")
    try:
        subprocess.check_call(["docker", "network", "create", "-d", "bridge", "oef_search_net"])
    except Exception as e:
        print("Docker network creation failed: ", str(e))
    try:
        print('Generating source archive... (location: {})'.format(path))
        cmd = [
            'git-archive-all', os.path.join(path, 'project.tar.gz')
        ]
        subprocess.check_call(cmd, cwd=path)
        print('Generating source archive...complete')
    except Exception as e:
        print("Source archive generation failed: ", str(e))
        if os.path.exists(path+"/project.tar.gz"):
            print("Using {} as source archive for container building!".format(path+"/project.tar.gz"))
        else:
            print("No project source archive found! Can't build container image without it!")
            exit(1)

    builder_image_tag = image_tag+"_builder"

    if fast:
        f_in = open(path+"/Dockerfile.template", "r")
        f_out = open(path+"/Dockerfile", "w")
        lines = f_in.readlines()
        lines[0] = lines[0].replace("PREV_LOCAL_BUILDER_IMAGE", builder_image_tag)
        f_out.writelines(lines)
        f_out.close()

    cmd = [
        'docker',
        'build',
        '--target',
        'builder',
        '-t', builder_image_tag,
        '.',
    ]
    subprocess.check_call(cmd, cwd=path)
    cmd = [
        'docker',
        'build',
        '--target',
        'runtime',
        '-t', image_tag,
        '.',
    ]
    subprocess.check_call(cmd, cwd=path)


def create_symlinks(target=None):
    print("Gensim setup....")
    gensim_setup()
    print("Gensim setup...complete")
    print("NLTK setup....")
    nltk_setup()
    print("NLTK setup...complete")

    files = [
        "gensim-data/glove-wiki-gigaword-50/glove-wiki-gigaword-50.gz",
        "gensim-data/glove-wiki-gigaword-50/__init__.py",
        "gensim-data/glove-wiki-gigaword-50.bin",
        "gensim-data/glove-wiki-gigaword-50.bin.vectors.npy",
        "nltk_data/corpora/stopwords.zip",
        "nltk_data/corpora/wordnet.zip",
        "nltk_data/tokenizers/punkt.zip",
    ]
    if target is not None:
        files = target
    docker_dir = os.path.abspath(os.path.dirname(__file__))
    if args.fast_build:
        docker_dir = docker_dir + "/faster_docker"
    print(docker_dir)
    for file in files:
        print("CREATE LINK TO {}....".format(file))
        directory = "/".join(file.split("/")[:-1])
        if not os.path.exists(docker_dir + "/" + directory):
            print("CREATE DIRECTORY: ", directory)
            os.makedirs(docker_dir + "/" + directory, exist_ok=True)
        if os.path.exists("~/" + file):
            print("REQUIRED FILE NOT FOUND: ", "~/" + file)
            print("You need to run gensim/nltk once in your computer so it downloads these files!")
            print("Running non docker version of the search will also trigger downloading of these files, afterwards"
                  " you can run this version too!")
            exit(1)
        try:
            subprocess.check_call(["ln", os.path.expanduser("~/" + file), file], cwd=docker_dir)
        except Exception as e:
            print(e)
        if not os.path.exists(docker_dir + "/" + file):
            print("FILE NOT FOUND: ", file)
            exit(1)
        print("DONE")

    return docker_dir


def kill_containers(names: List[str]):
    for name in names:
        try:
            subprocess.check_call(["docker", "kill", name])
        except Exception as e:
            print("Failed to kill container {} because: {}".format(name, str(e)))


def container_main(num_of_nodes: int, links: List[str], http_ports: Dict[int, int] = {}, ssl_cert: str = "", *,
         image_tag: str, do_build: bool, log_dir: str, fast_build: bool, docker_dir: str = "",
                   run_director: bool = True, config_file: str = ""):
    path = get_workdir()
    if do_build:
        build(image_tag, docker_dir if len(docker_dir) > 0 else path, fast_build)
    pool = ThreadPoolExecutor(num_of_nodes)

    CORE_PORT = 10000
    SEARCH_PORT = 20000
    DAP_PORT = 30000
    DIRECTOR_PORT = 40000

    config = None
    if config_file != None:
        with open(config_file, "r") as f:
            config = json.load(f)
        if len(config["nodes"]) != num_of_nodes:
            print("!!!!!!!! NUMBER OF NODES DOES NOT MATCH CONFIG FILE")
            return

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
        if config is not None:
            nc = config["nodes"][i]
            search_port = int(nc["uri"].split(":")[1])
            core_port = int(nc["core_uri"].split(":")[1])
            director_port =int(nc["director_uri"].split(":")[1])
            node_name = config["internal_hosts"][nc["name"]]
        else:
            search_port = SEARCH_PORT + i
            core_port = CORE_PORT + i
            director_port = DIRECTOR_PORT + i
            node_name = "oef_node" + str(i)

        args = [
            "--node_key", "Search{}".format(i),
            "--core_key", "Core{}".format(i),
            "--ip", "0.0.0.0",
            "--search_port", str(search_port),
            "--core_port", str(core_port),
            "--dap_port", str(DAP_PORT+i),
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

        log_cmd = []
        set_log_dir = []
        if len(log_dir) > 0:
            node_log_dir = "{}/node{}".format(log_dir, i)
            if not os.path.exists(node_log_dir):
                os.mkdir(node_log_dir)
            log_cmd = [
                "-v",
                node_log_dir+":"+"/logs"
            ]
            set_log_dir = [
                "--log_dir",
                "/logs"
            ]
        args.extend(set_log_dir)

        cmd = []
        cmd.extend(docker_cmd)
        cmd.extend([
            "--name",
            node_name,
            "-p",
            str(search_port) + ":" + str(search_port),
            "-p",
            str(core_port) + ":" + str(core_port),
            "-p",
            str(director_port)+":"+str(director_port)
        ])
        cmd.extend(log_cmd)
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
        cmd.extend(["--ip", "0.0.0.0"])
        try:
            subprocess.check_call(["docker", "kill", node_name])
        except:
            pass
        print("EXECUTE: ", " ".join(cmd))
        pool.submit(subprocess.check_call, cmd)
        names.append(node_name)
        api_targets.append(node_name+":"+str(search_port))
        director_targets.append(node_name+":"+str(director_port))

    if run_director:
        director_cmd = []
        director_cmd.extend(docker_cmd)
        director_cmd.extend(["--name", "location_director"])
        director_cmd.extend([
            image_tag,
            "director",
            "no_sh",
            "--type",
            "location_and_connection",
            "--targets"
        ])
        director_cmd.extend(director_targets)
        print("EXECUTE: ", " ".join(director_cmd))
        subprocess.check_call(director_cmd, stderr=subprocess.STDOUT, stdout=open(log_dir+"/director_lp.log", "w"))

        weather_director_cmd = []
        weather_director_cmd.extend(docker_cmd)
        weather_director_cmd.extend(["--name", "weather_director"])
        weather_director_cmd.extend([
            image_tag,
            "director",
            "no_sh",
            "--type",
            "weather_agent",
            "--targets"
        ])
        weather_director_cmd.extend(api_targets)
        print("EXECUTE: ", " ".join(weather_director_cmd))
        subprocess.check_call(weather_director_cmd, stderr=subprocess.STDOUT, stdout=open(log_dir+"/director_weather.log",
                                                                                      "w"))
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
    parser.add_argument("--log_dir", type=str, required=False, default="", help="Log directory")
    parser.add_argument("--fast_build", "-f", action="store_true", help="Enable faster rebuilding")
    parser.add_argument("--run_director", action="store_true", default=False,
                        help="Run director to set location and connectivity")
    parser.add_argument("--config_file", "-c", required=False, help="JSON configuration file used by director")

    args = parser.parse_args()

    docker_dir = create_symlinks()

    http_port_map = {}
    for e in args.http_port_map:
        k, p = e.split(":")
        http_port_map[int(k)] = int(p)

    log_dir = args.log_dir
    if log_dir[-1] == "/":
        log_dir = log_dir[:-1]

    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    if args.links is None:
        links = []
    else:
        links = args.links
    container_main(args.num_nodes, links, http_port_map, "/app/server.pem", image_tag=args.image,
                   do_build=args.build, log_dir=log_dir, fast_build=args.fast_build, docker_dir=docker_dir,
                   run_director=args.run_director, config_file=args.config_file)
