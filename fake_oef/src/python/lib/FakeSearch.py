from fake_oef.src.python.lib import FakeBase
from pluto_app.src.python.app import PlutoApp
from fake_oef.src.python.lib.ConnectionFactory import SupportsConnectionInterface
from api.src.proto import response_pb2
from api.src.proto import query_pb2
from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer
from api.src.python.Serialization import serializer, deserializer
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List
import time
import gensim
import abc


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


class Observer(abc.ABC):
    @abc.abstractmethod
    def on_change(self, node_id, value=None):
        pass


class ObserverNotifier(Observer):
    def __init__(self):
        self._store = []

    def register_observer(self, observer: Observer):
        self._store.append(observer)

    def on_change(self, node_id, value=None):
        for observer in self._store:
            observer.on_change(node_id, value)


class MultiFieldObserver(abc.ABC):
    class FieldObserver(Observer):
        def __init__(self, field, multifield_observer):
            self._field = field
            self._multifield_observer = multifield_observer

        def on_change(self, node_id, value=None):
            return self._multifield_observer.on_change(self._field, node_id, value)

    def get_field_observer(self, field_name):
        return MultiFieldObserver.FieldObserver(field_name, self)

    @abc.abstractmethod
    def on_change(self, field, node_id, value):
        pass


class NodeAttributeInterface:
    def __init__(self):
        self._attributes = {
            "location": None
        }
        self._update_observer = ObserverNotifier()
        self._activity_observer = ObserverNotifier()

    def _setup(self, dapManager):
        self._geo_store = dapManager.getInstance("geo_search")
        self._location_table = "locations"

    def register_update_observer(self, observer: Observer):
        self._update_observer.register_observer(observer)

    def register_activity_observer(self, activity_observer: Observer):
        self._activity_observer.register_observer(activity_observer)

    def notify_update(self):
        self._update_observer.on_change(self._id)

    def notify_activity(self, t):
        self._activity_observer.on_change(self._id, t)

    @property
    def identity(self):
        return self._id

    @property
    def core_locations(self):
        return self._geo_store.getGeoByTableName(self._location_table).store.values()

    @property
    def location(self):
        return self._attributes["location"]

    @location.setter
    def location(self, location):
        self._attributes["location"] = location


class FakeSearch(PlutoApp.PlutoApp, SupportsConnectionInterface, NodeAttributeInterface):
    def __init__(self, search_node_id, connection_factory, cleaner_pool: ThreadPoolExecutor, cache_lifetime: int = 10):
        self._id = search_node_id
        self._bin_id = self._id.encode("utf-8")
        self._connection_factory = connection_factory
        self._connection_factory.add_obj(search_node_id, self)
        self._connections = {}
        self._cache = {}
        self._cache_lifetime = cache_lifetime
        self._executor = cleaner_pool
        self._last_clean = 0
        self._search_coms = {}
        self._attributes = {
            "loc": ()
        }
        PlutoApp.PlutoApp.__init__(self)
        SupportsConnectionInterface.__init__(self)
        NodeAttributeInterface.__init__(self)

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
        self._setup(self.dapManager)

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
        if path == "query" and not self._am_i_closer_and_update_query(data):
            return []
        result = asyncio.run(self.callMe(path, data))
        if path == "update":
            self.notify_update()
        return result

    def _am_i_closer_and_update_query(self, query: query_pb2.Query):
        if self.location is None:
            return False
        my_distance = self.location.distance(query.directed_search.target.geo)
        source_distance = query.directed_search.distance.geo
        if my_distance <= source_distance:
            query.directed_search.distance.geo = my_distance
            return True
        else:
            return False

    async def broadcast(self, path: str, data):
        source = None
        if isinstance(data, query_pb2.Query):
            data.ttl -= 1
            if data.ttl <= 0:
                return []
            source = data.source_key
            data.source_key = self._bin_id
        cos = []
        proto = data.SerializeToString()
        proto_model = data.model.SerializeToString()
        t = time.time()
        self.notify_activity(t)
        for target_search_node_id in self._search_coms:
            h = hash(path + ":" + str(proto_model) + ":" + str(target_search_node_id))
            c = self._cache.get(h, t - 2 * self._cache_lifetime)
            if (t - c) < self._cache_lifetime:
                continue
            self._cache[h] = t
            if source is None or source != target_search_node_id.encode("utf-8"):
                cos.append(self._search_coms[target_search_node_id].callMe(path, proto))
        self._executor.submit(FakeSearch._cache_cleaner, self)
        if len(cos) > 0:
            return await asyncio.gather(*cos)
        return []
