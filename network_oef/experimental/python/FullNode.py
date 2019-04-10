import argparse
import multiprocessing
import subprocess
import time
import os
from utils.src.python.resources import binaryfile
import time
import socket


def run_node(name: str, node_ip: str, node_port: int, dap_port_start: int, http_port: int, director_api_port: int, ssl_certificate: str, q: multiprocessing.Queue):
    from network_oef.src.python.FullLocalSearchNode import FullSearchNone
    from utils.src.python.Logging import configure as configure_logging
    configure_logging(id_flag="_"+name)

    node = FullSearchNone(name, node_ip, node_port, [{
        "run_py_dap": True,
        "file": "ai_search_engine/src/resources/dap_config.json",
        "port": dap_port_start
    }
    ],http_port, ssl_certificate, "api/src/resources/website", director_api_port=director_api_port)
    print("**** Node {} started".format(name))
    time.sleep(1)
    con = q.get()
    print("**** SearchProcess ({}) {} got: ".format(name, id), con)
    node.add_remote_peer(*con)
    node.block()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Test application for PLUTO.')
    parser.add_argument("--core_key", required=True, type=str,
                        help= "Core public key")
    parser.add_argument("--node_key", required=True, type=str, help="Search node public key.")
    parser.add_argument("--ip", required=False, type=str, default="0.0.0.0",
                        help="IP address")
    parser.add_argument("--http_port", required=False, type=int, default=-1,
                        help="Http API port number. If -1 (default) then it's disabled")
    parser.add_argument("--ssl_certificate", required=False, type=str, default=None,
                        help="Specify an SSL certificate PEM file for the http API")
    parser.add_argument("--core_port", required=False, type=int, default=10000,
                        help="Port number for the core")
    parser.add_argument("--search_port", required=False, type=int, default=20000,
                        help="Port number of the search")
    parser.add_argument("--dap_port", required=False, type=int, default=30000,
                        help="Starting port for the network daps")
    parser.add_argument("--search_peers", nargs='*',  type=str,
                        help="Search peers to connect to, format: node_key:ip:port node_key:ip:port ...")
    parser.add_argument("--director_api_port", required=False, type=int, default=40000,
                        help="Director api port")

    args = parser.parse_args()

    oef_core = binaryfile("fetch_teams/OEFNode", as_file=True).name

    core_key    = args.core_key
    search_name = args.node_key

    search_queue = multiprocessing.Queue()
    search_process = multiprocessing.Process(target=run_node, args=(search_name, args.ip, args.search_port,
                                                                    args.dap_port, args.http_port,
                                                                    args.director_api_port, args.ssl_certificate,
                                                                    search_queue))
    search_process.start()

    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock.connect_ex((args.ip, args.search_port)) != 0:
            time.sleep(0.5)
        else:
            break

    process = subprocess.Popen([oef_core, core_key, args.ip, str(args.core_port), args.ip, str(args.search_port)],
                               stdout=None, stderr=None)

    added_peers = 0

    if args.search_peers is not None:
        while len(args.search_peers) != 0:
            print("SEARCH PEERS: ", args.search_peers)
            for target in args.search_peers:
                key, host, port = target.split(":")
                try:
                    host = socket.gethostbyname(host)
                except Exception as e:
                    print("Resolution failed, because: "+str(e))
                port = int(port)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if sock.connect_ex((host, port)) != 0:
                    continue
                search_queue.put([host, port, key])
                args.search_peers.remove(target)
            time.sleep(2)

    process.wait()
