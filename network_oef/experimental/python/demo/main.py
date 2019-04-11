import argparse
import os
from network_oef.experimental.python.demo.ProcessMain import main as process_main
from network_oef.experimental.python.demo.ContainerMain import main as container_main
import functools


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DEMO search network')
    parser.add_argument("--num_nodes", required=True, type=int, help="Number of full demo nodes")
    parser.add_argument("--links", nargs='*',  type=str,
                        help="Node connection list: id1:id2 ... (id: 0...num_nodes-1)")
    parser.add_argument("--http_port_map", nargs='*', type=str, help="id:http_port (id: 0...num_nodes-1)")
    parser.add_argument("--ssl_certificate", type=str, required=False, default="", help="SSL file")
    parser.add_argument("--docker", "-d",  action='store_true', help="Docker version")
    parser.add_argument("--image", "-i", type=str, default="oef-search:latest", help="Docker image name")
    parser.add_argument("--build", "-b", action="store_true", help="Build docker image")

    args = parser.parse_args()

    http_port_map = {}
    for e in args.http_port_map:
        k, p = e.split(":")
        http_port_map[int(k)] = int(p)

    if args.docker:
        func = functools.partial(container_main, image_tag=args.image, do_build=args.build)
    else:
        func = process_main

    func(args.num_nodes, args.links, http_port_map, args.ssl_certificate)
