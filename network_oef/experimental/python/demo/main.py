from network_oef.experimental.python.demo.SearchNetwork import SearchNetwork
from typing import List, Dict
import time
import argparse
from concurrent.futures import ThreadPoolExecutor
import os

os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"


def main(num_of_nodes: int, links: List[str], http_ports: Dict[int, int] = {}, ssl_cert: str = ""):
    search_network = SearchNetwork()
    pool = ThreadPoolExecutor(20)

    core_port = 10000
    node_port = 20000
    dap_port = 30000
    director_port = 40000

    create_tasks = []
    for i in range(num_of_nodes):
        node_key = "Search{}".format(i)
        core_key = "Core{}".format(i)
        http_port = http_ports.get(i, -1)
        cert_file = "" if http_port == -1 else ssl_cert
        ct = pool.submit(SearchNetwork.create_node, search_network, node_key, "127.0.0.1", node_port+i, dap_port+i,
                         director_port+i, core_key, core_port+i, http_port, cert_file)
        create_tasks.append(ct)

    for ct in create_tasks:
        print(ct.result())

    time.sleep(5)
    for l in links:
        n1, n2 = l.split(":")
        while True:
            if search_network.link("Search{}".format(n1), "Search{}".format(n2)):
                break
            time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DEMO search network')
    parser.add_argument("--num_nodes", required=True, type=int, help="Number of full demo nodes")
    parser.add_argument("--links", nargs='*',  type=str,
                        help="Node connection list: id1:id2 ... (id: 0...num_nodes-1)")
    parser.add_argument("--http_port_map", nargs='*', type=str, help="id:http_port (id: 0...num_nodes-1)")
    parser.add_argument("--ssl_certificate", type=str, required=False, default="", help="SSL file")

    args = parser.parse_args()

    http_port_map = {}
    for e in args.http_port_map:
        k, p = e.split(":")
        http_port_map[int(k)] = int(p)

    main(args.num_nodes, args.links, http_port_map, args.ssl_certificate)