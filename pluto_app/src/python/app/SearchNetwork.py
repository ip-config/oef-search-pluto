from typing import List
import asyncio
from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer
from fake_oef.src.python.lib import FakeSearch
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
    def __init__(self, comms_handlers_to_inject_by_ident={}, search_nodes_to_create=[]):
        self.search_nodes = {}
        self.w2v = LazyW2V()
        for search_node_id in search_nodes_to_create:
            self.add_search_node(search_node_id, comms_handlers_to_inject_by_ident.get(search_node_id, None))

        self.connection_map = {} # mapping of search_node_id -> [ search_node_id ] 
        self.cores = {}
        self.cache = {}
        self.cache_lifetime = 10
        self.executor = ThreadPoolExecutor(1)
        self.last_clean = 0

        self.stacks = {}  # mapping of name -> { 'search_node', 'eof_core' }

    def add_search_node(self, search_node_id, communication_handler=None):
        app = FakeSearch.FakeSearch()
        self.search_nodes[search_node_id] = app
        app.start(communication_handler)
        app.inject_w2v(self.w2v)
        app.add_handler("search", BroadcastFromNode("search", self, search_node_id))
        return app

    def add_stack(self, oef_core_id, search_node_id, communication_handler=None, connection_factory=None):
        r = self.stacks.setdefault(oef_ident, { 'oef_core': None, 'search_node': None })
        r['search_node'] = self.add_search_node(search_node_id, communication_handler)
        r['oef_core'] = self.create_oef_core_for_node(search_node_id, oef_core_id, connection_factory)
        return r

    def _cache_cleaner(self):
        t = time.time()
        if (self.last_clean - t) < self.cache_lifetime:
            return
        for k, v in self.cache.items():
            if (v - t) >= self.cache_lifetime:
                self.cache.pop(k)

    def set_connection(self, search_node_id: str, connections: List[str]):
        self.connection_map[search_node_id] = connections

    def create_oef_core_for_node(self, search_node_id: str, oef_core_id: str, connection_factory):
        self.cores[oef_core_id] = FakeOef(id=oef_core_id, connection_factory=connection_factory, search_com=SearchComWrapper(search_node_id, self))
        return self.cores[oef_core_id]

    async def broadcast_from_node(self, search_node_id: str, path: str, data):
        cos = []
        for target_search_node_id in self.connection_map[search_node_id]:
            if target_search_node_id == search_node_id:
                continue
            proto = data.SerializeToString()
            h = hash(path+":"+str(proto)+":"+str(target_search_node_id))
            t = time.time()
            c = self.cache.get(h, t-2*self.cache_lifetime)
            if (t-c) < self.cache_lifetime:
                continue
            self.cache[h] = t
            cos.append(self.search_nodes[target_search_node_id].callMe(path, proto))
        self.executor.submit(SearchNetwork._cache_cleaner, self)
        if len(cos) > 0:
            return await asyncio.gather(*cos)
        return []

    def call_node(self, search_node_id: str, path: str, data):
        return asyncio.run(self.search_nodes[search_node_id].callMe(path, data))


class SearchComWrapper(SearchComInterface):
    def __init__(self, node: int, network: SearchNetwork):
        self._id = node
        self._network = network

    def call(self, path: str, data):
        return self._network.call_node(self._id, path, data)
