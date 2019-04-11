from pluto_app.src.python.app import PlutoApp
from network_oef.src.python.Connection import Connection
from api.src.proto.core import response_pb2
from api.src.proto.core import query_pb2, update_pb2
from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer, DataWrapper
from api.src.python.Serialization import serializer, deserializer
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import gensim
import abc
from utils.src.python.Logging import has_logger
from api.src.python.network import network_support
import api.src.python.RouterBuilder as RouterBuilder
from utils.src.python.distance import geo_distance
import copy


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
        response = await self._node.broadcast(self._path, copy.deepcopy(msg))
        if type(response) != list:
            response = [response]
        response = self.__flatten_list(response)
        transformed = []
        for r in response:
            if len(r.data) < 1:
                deserialized = None
            else:
                deserialized = await self._serializer.deserialize(r.data)
            transformed.append(DataWrapper(r.success, r.uri, deserialized, r.error_code, "", r.narrative, r.id))
        return transformed


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


class SearchNode(PlutoApp.PlutoApp, NodeAttributeInterface):
    @has_logger
    @network_support
    def __init__(self, cache_lifetime: int, id: str, cleaner_pool: ThreadPoolExecutor = None):
        self._id = id
        self._bin_id = self._id.encode("utf-8")
        self._connections = {}
        self._cache = {}
        self._cache_lifetime = cache_lifetime
        if cleaner_pool is None:
            self._executor = ThreadPoolExecutor(1)
        else:
            self._executor = cleaner_pool
        self._last_clean = 0
        self._search_coms = {}
        self._attributes = {
            "loc": ()
        }
        PlutoApp.PlutoApp.__init__(self)
        NodeAttributeInterface.__init__(self)
        self.log.update_local_name(self._id)
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError as e:
            self.error("Failed to get event loop, because: ", str(e), "! Creating a new one..")
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        self.director_router = RouterBuilder.DirectorAPIRouterBuilder()\
            .set_name("DirectorRouter")\
            .set_dap_manager(self.dapManager)\
            .add_location_config({"table": "locations", "field": "locations.update"})\
            .build()
        self._com = None
        self._com_director = None

    def init(self, node_ip: str, node_port: int, network_dap_config: dict, http_port: int = -1, ssl_certificate: str = None, html_dir: str = None, *, director_port: int = None):
        for name, conf in network_dap_config.items():
            self.add_network_dap_conf(name, conf)
        self.start()
        self.add_handler("search", BroadcastFromNode("search", self))
        self._setup(self.dapManager)

        if node_ip is not None and node_port is not None and hasattr(self, "start_network"):
            self._com = self.start_network(self.router, node_ip, node_port, http_port, ssl_certificate, html_dir)
            if director_port is not None:
                self._com_director = self.start_network(self.director_router, node_ip, director_port)

    def connect_to_search_node(self, host: str, port: int, search_node_id=None):
        if search_node_id is None:
            search_node_id = host + ":" + str(port)
        self.info("Create search network link with search node {} @ {}:{}".format(search_node_id, host, port))
        self._search_coms[search_node_id] = Connection(host, port)

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

    async def broadcast(self, path: str, data):
        source = None
        if isinstance(data, query_pb2.Query):
            if data.ttl <= 0:
                self.warning("Stop broadcasting query because TTL is 0")
                return []
            data.ttl -= 1
            source = data.source_key.decode("UTF-8")
            data.source_key = self._bin_id
            try:
                location = self.dapManager.getPlaneInformation("location")["values"]
                if len(location) > 1:
                    self.warning("Got more then 1 location from dapManager (I'm using first, ignoring the rest now): ",
                                 location)
                # TODO: multiple core
                # TODO: nicer way?
                location = location[0].value.l
                target = data.directed_search.target.geo
                data.directed_search.distance.geo = geo_distance(location, target)
            except Exception as e:
                self.warning("Set distance failed in broadcast, because: ", str(e))
        else:
            self.warning("query is not api query (missing TTL)")
        cos = []
        #proto = data.SerializeToString()
        proto_model = data.model.SerializeToString()
        t = time.time()
        self.notify_activity(t)
        self.info("Coms to broadcast: ", self._search_coms.keys())
        for target_search_node_id in self._search_coms:
            h = hash(path + ":" + str(proto_model) + ":" + str(data.directed_search.target.geo) + ":" + str(target_search_node_id))
            c = self._cache.get(h, t - 2 * self._cache_lifetime)
            if (t - c) < self._cache_lifetime:
                self.info("Skip broadcast to {} because last broadcast was @ {} (current time = {})".format(target_search_node_id, c, t))
                continue
            self._cache[h] = t
            if source is None or source != target_search_node_id:
                self.info("Broadcasting search to ", target_search_node_id, ", data=", data)
                cos.append(self._search_coms[target_search_node_id].call_node(path, data.SerializeToString()))
            else:
                self.info("Skip broadcast to {} because last broadcast source ({}) is the same".format(
                    target_search_node_id, source))
        self.info("Active co-routines: ", cos)
        try:
            self._executor.submit(SearchNode._cache_cleaner, self)
        except Exception as e:
            self.warning("Failed to schedule cache cleaner, because: ", str(e))
        if len(cos) > 0:
            self.info("Await gather")
            resp = await asyncio.gather(*cos)
            self.info("Response to broadcast: num = ", len(resp))
            for r in resp:
                if not r.success:
                    self.info("Response to broadcast is error: code=", r.error_code, ", message: ", r.msg())
            return resp
        return []

    def block(self):
        if self._com is not None:
            self._com.wait()
        elif self._com_director is not None:
            self._com_director.wait()
        else:
            time.sleep(1e6)