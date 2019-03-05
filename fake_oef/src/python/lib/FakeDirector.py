from fake_oef.src.python.lib.FakeSearch import NodeAttributeInterface, MultiFieldObserver, Observer
import numpy as np


class Location:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def distance(self, loc):
        return np.sqrt(np.power(loc.lat-self.lat, 2) + np.power(loc.lon-self.lon, 2))


class FakeDirector(Observer):
    def __init__(self):
        self.location_store = {}
        self.nodes = {}

    def on_change(self, node_id, value):
        self.update_local_locations(node_id)
        self.update_node(node_id)

    def update_local_locations(self, node_id):
        avg_x = 0
        avg_y = 0
        counter = 0.
        node = self.nodes[node_id]
        for loc in node.core_locations:
            avg_x += loc[0]
            avg_y += loc[1]
            counter += 1.
        if counter > 0:
            loc = Location(avg_x/counter, avg_y/counter)
        else:
            loc = None
        self.location_store[node_id] = loc

    def add_node(self, node: NodeAttributeInterface):
        self.nodes[node.identity] = node
        self.update_local_locations(node.identity)
        self.update_node(node.identity)
        node.register_update_observer(self)

    def update_node(self, node_id):
        self.nodes[node_id].location = self.location_store[node_id]
