from concurrent.futures import ThreadPoolExecutor
from network_oef.experimental.python.demo.SearchNetwork import SearchNetwork
from typing import List, Dict
import time
import os


def main(num_of_nodes: int, links: List[str], http_ports: Dict[int, int] = {}, ssl_cert: str = "", log_dir: str = ""):
    search_network = SearchNetwork()
    pool = ThreadPoolExecutor(num_of_nodes)

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
        node_log_dir = ""
        if len(log_dir) > 0:
            node_log_dir = "{}/node{}/".format(log_dir, i)
            if not os.path.exists(node_log_dir):
                os.mkdir(node_log_dir)
        ct = pool.submit(SearchNetwork.create_node, search_network, node_key, "127.0.0.1", node_port+i, dap_port+i,
                         director_port+i, core_key, core_port+i, http_port, cert_file, node_log_dir)
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