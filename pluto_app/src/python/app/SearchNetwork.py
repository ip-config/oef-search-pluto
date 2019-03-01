from typing import List
import asyncio
from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer
from pluto_app.src.python.app import PlutoApp
from fake_oef.src.python.lib.FakeOef import SearchComInterface, FakeOef
import gensim
import time
from concurrent.futures import ThreadPoolExecutor
from api.src.proto import response_pb2
from api.src.python.Serialization import serializer, deserializer


class SearchResponseSerialization(HasProtoSerializer):
    @deserializer
    def deserialize(self, data: bytes) -> response_pb2.SearchResponse:
        pass

    @serializer
    def serialize(self, proto_msg: response_pb2.SearchResponse) -> bytes:
        pass


class BroadcastFromNode(HasMessageHandler):
    def __init__(self, path, network, node_id):
        self._node = node_id
        self._network = network
        self._path = path
        self._serializer = SearchResponseSerialization()

    def __flatten_list(self, src):
        if type(src) != list:
            if src is None:
                return []
            return [src]
        result = []
        for e in src:
            flatten = self.__flatten_list(e)
            result.extend(flatten)
        return result

    async def handle_message(self, msg):
        response = await self._network.broadcast_from_node(self._node, self._path, msg)
        if type(response) != list:
            response = [response]
        response = self.__flatten_list(response)
        return await asyncio.gather(*[self._serializer.deserialize(serialized) for serialized in response])


class LazyW2V:
    def __init__(self, model="glove-wiki-gigaword-50"):
        self._w2v = None
        self._model = model

    def load(self):
        self._w2v = gensim.downloader.load(self._model)

    def __getitem__(self, item):
        if not self._w2v:
            self.load()
        return self._w2v[item]

    def __getattr__(self, item):
        return getattr(self._w2v, item)


class SearchNetwork:
    def __init__(self, coms={}, number_of_nodes=10):
        self.nodes = []
        w2v = LazyW2V()
        for i in range(number_of_nodes):
            app = PlutoApp.PlutoApp()
            self.nodes.append(app)
            app.start(coms.get(i, None))
            app.inject_w2v(w2v)
            app.add_handler("search", BroadcastFromNode("search", self, i))
        self.connection_map = {}
        self.cores = {}
        self.cache = {}
        self.cache_lifetime = 10
        self.executor = ThreadPoolExecutor(1)
        self.last_clean = 0

    def _cache_cleaner(self):
        t = time.time()
        if (self.last_clean - t) < self.cache_lifetime:
            return
        for k, v in self.cache.items():
            if (v - t) >= self.cache_lifetime:
                self.cache.pop(k)

    def set_connection(self, node: int, connections: List[int]):
        self.connection_map[node] = connections

    def create_oef_core_for_node(self, node: int, oef_id: str, connection_factory):
        self.cores[node] = FakeOef(id=oef_id, connection_factory=connection_factory, search_com=SearchComWrapper(node, self))
        return self.cores[node]

    async def broadcast_from_node(self, node: int, path: str, data):
        cos = []
        for i in self.connection_map[node]:
            if i == node:
                continue
            proto = data.SerializeToString()
            h = hash(path+":"+str(proto)+":"+":"+str(i))
            t = time.time()
            c = self.cache.get(h, t-2*self.cache_lifetime)
            if (t-c) < self.cache_lifetime:
                continue
            self.cache[h] = t
            cos.append(self.nodes[i].callMe(path, proto))
        self.executor.submit(SearchNetwork._cache_cleaner, self)
        if len(cos) > 0:
            return await asyncio.gather(*cos)
        return []

    def call_node(self, node: int, path: str, data):
        return asyncio.run(self.nodes[node].callMe(path, data))


class SearchComWrapper(SearchComInterface):
    def __init__(self, node: int, network: SearchNetwork):
        self._id = node
        self._network = network

    def call(self, path: str, data):
        return self._network.call_node(self._id, path, data)
