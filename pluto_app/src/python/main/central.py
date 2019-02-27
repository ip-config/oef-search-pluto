#!/usr/bin/env python3
from utils.src.python.Logging import configure as configure_logging
from pluto_app.src.python.app import PlutoApp
import argparse
from typing import List
import asyncio
from api.src.python.CommunicationHandler import socket_server, http_server, CommunicationHandler
from api.src.python.Interfaces import HasMessageHandler


class BroadcastFromNode(HasMessageHandler):
    def __init__(self, path, network, node_id):
        self._node = node_id
        self._network = network
        self._path = path

    async def handle_message(self, msg):
        return await self._network.broadcast_from_node(self._node, self._path, msg)


class SearchNetwork:
    def __init__(self, coms={}, number_of_nodes=10):
        self.nodes = []
        for i in range(number_of_nodes):
            app = PlutoApp.PlutoApp()
            self.nodes.append(app)
            app.run(coms.get(i, None))
            app.add_handler("search", BroadcastFromNode("search", self, i))
        self.connection_map = {}
        self.working = {}

    def set_connection(self, node: int, connections: List[int]):
        self.connection_map[node] = connections

    async def broadcast_from_node(self, node: int, path: str, data):
        self.working = {node: 1}
        cos = []
        for i in self.connection_map[node]:
            self.working[i] = self.working.get(i, 0) + 1
            cos.append(self.nodes[i].callMe(path, data))
        return await asyncio.gather(*cos)

    def call_node(self, node: int, path: str, data):
        self.working = {node: 1}
        asyncio.run(self.nodes[node].callMe(path, data))


if __name__ == "__main__":
    configure_logging()

    parser = argparse.ArgumentParser(description='Test application for PLUTO.')
    parser.add_argument("--ssl_certificate", required=True, type=str, help="specify an SSL certificate PEM file.")
    parser.add_argument("--http_port", required=True, type=int, help="which port to run the HTTP interface on.")
    parser.add_argument("--socket_port", required=True, type=int, help="which port to run the socket interface on.")
    parser.add_argument("--html_dir", required=False, type=str, help="where ", default="api/src/resources/website")
    args = parser.parse_args()

    com = CommunicationHandler(1)
    com.add(http_server, "0.0.0.0", args.http_port, args.ssl_certificate, args.html_dir)

    search_network = SearchNetwork({0: com}, 5)

    # Search connectivity
    search_network.set_connection(0, [1, 4])
    search_network.set_connection(1, [2, 3])
    search_network.set_connection(2, [3, 4])
    search_network.set_connection(3, [4, 0])
    search_network.set_connection(4, [1, 2])




