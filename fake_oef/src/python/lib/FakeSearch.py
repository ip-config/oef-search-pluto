from fake_oef.src.python.lib import FakeBase
from pluto_app.src.python.app import PlutoApp
from fake_oef.src.python.lib.ConnectionFactory import SupportsConnectionInterface
from api.src.proto import response_pb2
from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer
from api.src.python.Serialization import serializer, deserializer
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List
import time
import gensim


class SearchResponseSerialization(HasProtoSerializer):
    @deserializer
    def deserialize(self, data: bytes) -> response_pb2.SearchResponse:
        pass

    @serializer
    def serialize(self, proto_msg: response_pb2.SearchResponse) -> bytes:
        pass


class BroadcastFromNode(HasMessageHandler):
    def __init__(self, path, node):
        self._node = node
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
        response = await self._node.broadcast(self._path, msg)
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


class FakeSearch(PlutoApp.PlutoApp, SupportsConnectionInterface):
    def __init__(self, search_node_id, connection_factory, cleaner_pool: ThreadPoolExecutor, cache_lifetime: int = 10):
        self._id = search_node_id
        self._connection_factory = connection_factory
        self._connection_factory.add_obj(search_node_id, self)
        self._connections = {}
        self._cache = {}
        self._cache_lifetime = cache_lifetime
        self._executor = cleaner_pool
        self._last_clean = 0
        self._search_coms = {}
        super().__init__()

    @property
    def connection(self):
        return self._connections

    @connection.setter
    def connection(self, value):
        self._connections = value

    def init(self, w2v: LazyW2V, communication_handler=None):
        self.start(communication_handler)
        self.inject_w2v(w2v)
        self.add_handler("search", BroadcastFromNode("search", self))

    def connect_to_search_node(self, search_node_id):
        self._search_coms[search_node_id] = self._connection_factory.create(search_node_id, self._id)

    def disconnect(self):
        for com in self._search_coms:
            com.disconnect()

    def _cache_cleaner(self):
        t = time.time()
        if (self._last_clean - t) < self._cache_lifetime:
            return
        self._last_clean = t
        for k, v in self._cache.items():
            if (v - t) >= self._cache_lifetime:
                self._cache.pop(k)

    def call(self, path: str, data):
        return asyncio.run(self.callMe(path, data))

    async def broadcast(self, path: str, data):
        cos = []
        for target_search_node_id in self._search_coms:
            proto = data.SerializeToString()
            h = hash(path + ":" + str(proto) + ":" + str(target_search_node_id))
            t = time.time()
            c = self._cache.get(h, t - 2 * self._cache_lifetime)
            if (t - c) < self._cache_lifetime:
                continue
            self._cache[h] = t
            cos.append(self._search_coms[target_search_node_id].callMe(path, proto))
        self._executor.submit(FakeSearch._cache_cleaner, self)
        if len(cos) > 0:
            return await asyncio.gather(*cos)
        return []
