from pluto_app.src.python.app import PlutoApp
from network_oef.src.python.Connection import Connection
from api.src.proto.core import query_pb2, update_pb2
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from utils.src.python.Logging import has_logger
from api.src.python.network import network_support
import api.src.python.RouterBuilder as RouterBuilder
from api.src.python.director.PeerEndpoint import ConnectionManager
from utils.src.python.distance import geo_distance
from network_oef.src.python.Broadcast import BroadcastFromNode
from dap_api.src.python import DapQueryRepn


class LocationLookupVisitor(DapQueryRepn.DapQueryRepn.Visitor):
    @has_logger
    def __init__(self, location_table_name, location_field_name):
        self.location_table_name = location_table_name
        self.location_field_name = location_field_name
        self.location = []

    def visitNode(self, node, depth):
        pass

    def visitLeaf(self, node, depth):
        if node.target_field_name != self.location_table_name or node.target_field_name != self.location_field_name:
            return
        if len(self.location) > 0:
            self.warning("Found multiple location in the query: ", self.location, node.query_field_value)
        self.location = node.query_field_value


class SearchNode(PlutoApp.PlutoApp, ConnectionManager):
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
            .add_connection_manager(self)\
            .build()
        self._com = None
        self._com_director = None

    def init(self, node_ip: str, node_port: int, network_dap_config: dict, http_port: int = -1, ssl_certificate: str = None, html_dir: str = None, *, director_port: int = None):
        for name, conf in network_dap_config.items():
            self.add_network_dap_conf(name, conf)
        self.start()
        self.add_handler("search", BroadcastFromNode("search", self))

        if node_ip is not None and node_port is not None and hasattr(self, "start_network"):
            self._com = self.start_network(self.router, node_ip, node_port, http_port, ssl_certificate, html_dir)
            if director_port is not None:
                self._com_director = self.start_network(self.director_router, node_ip, director_port)

    def connect_to_search_node(self, host: str, port: int, search_node_id=None):
        if search_node_id is None:
            search_node_id = host + ":" + str(port)
        self.info("Create search network link with search node {} @ {}:{}".format(search_node_id, host, port))
        self._search_coms[search_node_id] = Connection(host, port)

    def add_peer(self, name: str, host: str, port: int) -> bool:
        self.connect_to_search_node(host, port, name)
        return True

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
                plane_info = self.dapManager.getPlaneInformation("location")
                location = plane_info["values"]
                if len(location) > 1:
                    self.warning("Got more then 1 location from dapManager (I'm using first, ignoring the rest now): ",
                                 location)

                if not data.directed_search.target.hasField("geo"):
                    visitor = LocationLookupVisitor(plane_info["table_name"], plane_info["field_name"])
                    query_rpn = self.dapManager.makeQuery(data)
                    query_rpn.visit(visitor)
                    target_location = visitor.location
                    if len(target_location) == 2:
                        self.info("LOCATION in the query, setting up header to include location: ", target_location)
                        data.directed_search.target.geo.lon = target_location[0]
                        data.directed_search.target.geo.lat = target_location[1]
                target = data.directed_search.target.geo
                # TODO: multiple core
                # TODO: nicer way?
                location = location[0].value.l
                data.directed_search.distance.geo = geo_distance(location, target)
            except Exception as e:
                self.warning("Set distance failed in broadcast, because: ", str(e))
        else:
            self.warning("query is not api query (missing TTL)")
        cos = []
        #proto = data.SerializeToString()
        proto_model = data.model.SerializeToString()
        t = time.time()
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