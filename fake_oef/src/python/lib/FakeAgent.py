from dap_api.src.protos import dap_update_pb2
from fake_oef.src.python.lib.ConnectionFactory import SupportsConnectionInterface, Endpoint
from fake_oef.src.python.lib.Connection import Connection


class FakeAgent(SupportsConnectionInterface):
    def __init__(self, **kwargs):
        for k in ['connection_factory', 'id']:
            setattr(self, k, kwargs.get(k, None))
        if self.connection_factory:
            self.connection_factory.add_obj(self.id, self)
        self.connections = {}

    @property
    def connection(self):
        return self.connections

    @connection.setter
    def connection(self, value):
        self.connections = value

    def connect(self, target):
        self.connections[target] = self.connection_factory.create(target, self.id)
        return self.connections[target]

    def disconnect(self, target):
        c = self.connections.get(target, None)
        if isinstance(c, Connection):
            self.connections.pop(target)
            c.disconnect()

    def register_service(self, service_upd):
        for key, con in self.connections.items():
            print("Register service: ", service_upd, " To con: ", key)
            con.register_service(self.id, service_upd.SerializeToString())

    def search(self, query):
        res = []
        for key, con in self.connections.items():
            res.append(con.search(query.SerializeToString()))
        return res