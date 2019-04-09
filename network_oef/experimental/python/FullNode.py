import argparse
import time
from network_oef.experimental.python.FullNodeClass import FullNode


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Test application for PLUTO.')
    parser.add_argument("--core_key", required=False, type=str, default="",
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

    full_node = FullNode()

    full_node.start_search(args.node_key, args.ip, args.search_port, args.dap_port, args.director_api_port,
                           args.http_port,  args.ssl_certificate)

    if len(args.core_key) > 0:
        full_node.start_core(args.core_key, args.ip, args.core_port)

    added_peers = 0
    if args.search_peers is not None:
        while len(args.search_peers) != 0:
            print("SEARCH PEERS: ", args.search_peers)
            for target in args.search_peers:
                key, host, port = target.split(":")
                if full_node.add_peer(key, host, port):
                    args.search_peers.remove(target)
            time.sleep(2)

    full_node.wait()
