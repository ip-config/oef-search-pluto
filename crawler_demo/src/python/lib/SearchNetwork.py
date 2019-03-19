from typing import List
from fake_oef.src.python.lib import FakeSearch
from fake_oef.src.python.lib.FakeOef import FakeOef
from concurrent.futures import ThreadPoolExecutor
from fake_oef.src.python.lib import FakeAgent
from fetch_teams.oef_core_protocol import query_pb2
from api.src.proto import update_pb2
from fake_oef.src.python.lib.FakeSearch import MultiFieldObserver, NodeAttributeInterface, Observer, ObserverNotifier
from fake_oef.src.python.lib.FakeDirector import Location
from fake_oef.src.python.lib.ConnectionFactory import ConnectionFactory
from fake_oef.src.python.lib.OEFSocketAdapter import OEFSocketAdapterServerBuilder
from utils.src.python.Logging import get_logger, has_logger


def get_attr_b(name, desc, t=2):
    attr1 = query_pb2.Query.Attribute()
    attr1.name = name
    attr1.type = t
    attr1.required = True
    attr1.description = desc
    return attr1


def create_dm(name: str, description: str, attributes: list) -> update_pb2.Update:
    dm = query_pb2.Query.DataModel()
    dm.name = name
    dm.description = description
    dm.attributes.extend(attributes)
    return dm


def create_weather_dm_update(agent) -> update_pb2.Update.BulkUpdate:
    upd1 = create_dm("weather_data_"+agent,
                         "All possible weather data.", [
                             get_attr_b("wind_speed", "Provides wind speed measurements.", 0),
                             get_attr_b("temperature", "Provides wind speed measurements.", 1),
                             get_attr_b("air_pressure", "Provides wind speed measurements.", 2)
                         ])
    return upd1


class FakeDirector(MultiFieldObserver):
    def __init__(self, entities):
        self.location_store = {}
        self.nodes = {}
        for key, entity in entities.items():
            self.location_store[entity.name + "-search"] = Location(*entity.coords)
        self.node_activity = {}
        self._activity_observer = ObserverNotifier()

    def register_activity_observer(self, observer: Observer):
        self._activity_observer.register_observer(observer)

    def on_change(self, field, node_id, value):
        if field == "update":
            self.update_local_locations(node_id)
            self.update_node(node_id)
        elif field == "activity":
            self.node_activity[node_id] = value
            self._activity_observer.on_change(node_id, value)
        else:
            raise KeyError("Unregistered observer field")

    def update_local_locations(self, node_id):
        pass

    def add_node(self, node: NodeAttributeInterface):
        self.nodes[node.identity] = node
        self.update_local_locations(node.identity)
        self.update_node(node.identity)
        node.register_update_observer(self.get_field_observer("update"))
        node.register_activity_observer(self.get_field_observer("activity"))

    def update_node(self, node_id):
        self.nodes[node_id].location = self.location_store[node_id]


class SearchNetwork:
    @has_logger
    def __init__(self, connection_factory: ConnectionFactory, entities):
        self.connection_factory = connection_factory
        self.w2v = FakeSearch.LazyW2V()
        self.cache_lifetime = 10
        self.executor = ThreadPoolExecutor(1)
        self.server_executor = ThreadPoolExecutor(1)
        self.director = FakeDirector(entities)
        self.stacks = {}  # mapping of name -> { 'search_node', 'eof_core' }
        self._socket_servers = OEFSocketAdapterServerBuilder(connection_factory, "127.0.0.1")

    def close_sockets(self):
        self._socket_servers.cancel()

    def register_activity_observer(self, observer: Observer):
        self.director.register_activity_observer(observer)

    def add_search_node(self, search_node_id, communication_handler=None) -> FakeSearch.FakeSearch:
        app = FakeSearch.FakeSearch(self.connection_factory, self.executor, self.cache_lifetime, id=search_node_id)
        app.init(self.w2v, communication_handler)
        self.director.add_node(app)
        return app

    def create_oef_core_for_node(self, search_node_id: str, oef_core_id: str, port: int):
        core = FakeOef(id=oef_core_id, connection_factory=self.connection_factory, port=port)
        core.connect_to_search(search_node_id)
        if port == 10000:
            self.error("Create oef socket adapter for node %s and port %d", oef_core_id, port)
            self._socket_servers.create_socket(port, oef_core_id)
        return core

    def create_weather_agent_for_core(self, oef_core_id: str, agent_id: str):
        agent = FakeAgent.FakeAgent(connection_factory=self.connection_factory, id=agent_id)
        agent.connect(target=oef_core_id)
        agent.register_service(create_weather_dm_update(agent_id))
        return agent

    def add_stack(self, node_id: str, oef_port: int, communication_handler=None):
        r = self.stacks.setdefault(node_id, {'oef_core': None, 'search_node': None})
        search_node_id = node_id + "-search"
        oef_core_id = node_id + "-core"
        agent_id = node_id + "-agent"
        r['search_node'] = self.add_search_node(search_node_id, communication_handler)
        r['oef_core'] = self.create_oef_core_for_node(search_node_id, oef_core_id, oef_port)
        r['agent'] = self.create_weather_agent_for_core(oef_core_id, agent_id)
        return r

    def build_from_entities(self, entities, initial_port=10000):
        connections = {}
        port = initial_port
        for key, entity in entities.items():
            self.add_stack(entity.name, port)
            port += 1
            connections[entity.name] = [link[0].name for link in entity.links]
        for key in connections:
            self.set_connection(key, connections[key])
        self.server_executor.submit(OEFSocketAdapterServerBuilder.run_forever, self._socket_servers)

    def set_connection(self, search_node_id: str, connections: List[str]):
        for target_search_id in connections:
            self.stacks[search_node_id]["search_node"].connect_to_search_node(target_search_id+"-search")

    def destroy(self):
        for core in self.cores:
            core.disconnect_search()
            core.kill()
        for node in self.search_nodes:
            node.disconnect()
            node.kill()
