from typing import List
import asyncio
from api.src.python.Interfaces import HasMessageHandler
from pluto_app.src.python.app import PlutoApp
from fake_oef.src.python.lib.FakeOef import SearchComInterface, FakeOef
import gensim


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
        w2v = gensim.downloader.load("glove-wiki-gigaword-50")
        for i in range(number_of_nodes):
            app = PlutoApp.PlutoApp()
            self.nodes.append(app)
            app.start(coms.get(i, None))
            app.inject_w2v(w2v)
            app.add_handler("search", BroadcastFromNode("search", self, i))
        self.connection_map = {}
        self.cores = {}
        self.working = {}

    def set_connection(self, node: int, connections: List[int]):
        self.connection_map[node] = connections

    def create_oef_core_for_node(self, node: int, oef_id: str, connection_factory):
        self.cores[node] = FakeOef(id=oef_id, connection_factory=connection_factory, search_com=SearchComWrapper(node, self))
        return self.cores[node]

    async def broadcast_from_node(self, node: int, path: str, data):
        self.working = {node: 1}
        cos = []
        for i in self.connection_map[node]:
            self.working[i] = self.working.get(i, 0) + 1
            cos.append(self.nodes[i].callMe(path, data.SerializeToString()))
        return await asyncio.gather(*cos)

    def call_node(self, node: int, path: str, data):
        self.working = {node: 1}
        return asyncio.run(self.nodes[node].callMe(path, data))


class SearchComWrapper(SearchComInterface):
    def __init__(self, node: int, network: SearchNetwork):
        self._id = node
        self._network = network

    def call(self, path: str, data):
        return self._network.call_node(self._id, path, data)
