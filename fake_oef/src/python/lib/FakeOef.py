
from api.src.proto import update_pb2
import abc


class SearchComInterface(abc.ABC):
    def call(self, path: str, data):
        pass


def create_address_attribute_update(key: str, ip: str, port: int):
    attr = update_pb2.Update.Attribute()
    key = key.encode("utf-8")
    attr.name = update_pb2.Update.Attribute.Name.Value("NETWORK_ADDRESS")
    attr.value.type = 10
    attr.value.a.ip = ip
    attr.value.a.port = port
    attr.value.a.key = key
    attr.value.a.signature = "Signed".encode("utf-8")
    upd = update_pb2.Update()
    upd.key = key
    upd.attributes.extend([attr])
    return upd


class FakeOef(object):
    def __init__(self, **kwargs):
        for k in [ 'search_object', 'id', 'connection_factory', 'search_com' ]:
            setattr(self, k, kwargs.get(k, None))

            self.connections = {}
            self.service_directory = {}
        if self.connection_factory:
            self.connection_factory.addCore(self.id, self)
        super().__init__(**kwargs)

    def search(self, query):
        return self.search_com.call("search". query)

    def agent_register(self, agent_id, agent, subject, connection):
        self.connections[agent_id] = {
            'id': agent_id,
            'agent': agent,
            'subject': subject,
            'connection': connection,
        }

    def register_oef_address(self, port: int):
        self.search_com.call("update", create_address_attribute_update(self.id, "127.0.0.1", port).SerializeToString())

    def agent_unregister_agent_id(self, agent_id):
        self._unreg('id', agent_id)

    def agent_unregister_agent(self, agent):
        self._unreg('agent', agent)
        self.search_com.call("remove", self.service_directory[agent])

    def register_service(self, agent_id, service_update):
        print("OEF got service from agent {}".format(agent_id))
        self.search_com.call("update", service_update)
        self.service_directory[agent_id] = service_update

    def unregister_service(self, agent_id, service_update):
        self.search_com.call("remove", service_update)
        self.service_directory.pop(agent_id, None)

    def agent_unregister_connection(self, connection):
        self._unreg('connection', connection)

    def _unreg(self, fieldname, value):
        keys = [
            k
            for k,v
            in self.connections.items()
            if v.get(fieldname, None) == value
        ]
        for k in keys:
            self.connections.pop(k)

    def kill(self):
        conns = [ c['connection'] for c in self.connections.values() ]
        self.connections = {}
        for c in conns:
            c.kill()
