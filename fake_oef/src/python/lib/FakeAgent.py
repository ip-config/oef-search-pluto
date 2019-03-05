from dap_api.src.protos import dap_update_pb2
from fake_oef.src.python.lib.ConnectionFactory import SupportsConnectionInterface, Endpoint
from fake_oef.src.python.lib.Connection import Connection
from utils.src.python.Logging import has_logger


class FakeAgent(SupportsConnectionInterface):
    @has_logger
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
        if target is None:
            for con in self.connections:
                self.connections[con].disconnect()
                self.connections.pop(con)

    def register_service(self, service_upd):
        for key, con in self.connections.items():
            self.log.info("Register service: %s to connection %s", service_upd.name, key)
            con.register_service(self.id, service_upd.SerializeToString())

    def search(self, query):
        res = []
        for key, con in self.connections.items():
            res.append(con.search(query))
        return res

    def get_from_core(self, what):
        if len(self.connections) == 0:
            return None
        elif len(self.connections) > 1:
            raise Exception("To many connection")
        key = list(self.connections.keys())[0]
        return self.connections[key].get(what)

    def swap_core(self, new_core):
        if len(self.connections) == 0:
            return None
        elif len(self.connections) > 1:
            raise Exception("To many connection")
        key = list(self.connections.keys())[0]
        self.disconnect(key)
        self.connect(new_core.key.decode("UTF-8"))