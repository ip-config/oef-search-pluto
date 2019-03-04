from typing import List
from fake_oef.src.python.lib import FakeSearch
from fake_oef.src.python.lib.FakeOef import SearchComInterface, FakeOef
from concurrent.futures import ThreadPoolExecutor


class SearchNetwork:
    def __init__(self, comms_handlers_to_inject_by_ident={}, search_nodes_to_create=[], connection_factory=None):
        self.connection_factory = connection_factory
        self.w2v = FakeSearch.LazyW2V()
        self.cache_lifetime = 10
        self.executor = ThreadPoolExecutor(1)
        self.search_nodes = {}
        for search_node_id in search_nodes_to_create:
            self.search_nodes[search_node_id] = self.add_search_node(search_node_id, comms_handlers_to_inject_by_ident.get(search_node_id, None))
        self.cores = {}
        self.stacks = {}  # mapping of name -> { 'search_node', 'eof_core' }

    def add_search_node(self, search_node_id, communication_handler=None) -> FakeSearch.FakeSearch:
        app = FakeSearch.FakeSearch(search_node_id, self.connection_factory, self.executor, self.cache_lifetime)
        app.init(self.w2v, communication_handler)
        return app

    def add_stack(self, oef_core_id, search_node_id, communication_handler=None):
        r = self.stacks.setdefault(oef_core_id, {'oef_core': None, 'search_node': None})
        r['search_node'] = self.add_search_node(search_node_id, communication_handler)
        r['oef_core'] = self.create_oef_core_for_node(search_node_id, oef_core_id)
        return r

    def set_connection(self, search_node_id: str, connections: List[str]):
        for target_search_id in connections:
            self.search_nodes[search_node_id].connect_to_search_node(target_search_id)

    def create_oef_core_for_node(self, search_node_id: str, oef_core_id: str):
        self.cores[oef_core_id] = FakeOef(id=oef_core_id, connection_factory=self.connection_factory)
        self.cores[oef_core_id].connect_to_search(search_node_id)
        return self.cores[oef_core_id]

    def destroy(self):
        for core in self.cores:
            core.disconnect_search()
            core.kill()
        for node in self.search_nodes:
            node.disconnect()
            node.kill()