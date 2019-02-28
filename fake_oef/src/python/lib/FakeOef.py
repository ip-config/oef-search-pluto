
from dap_api.src.protos import dap_update_pb2

class FakeOef(object):
    def __init__(self, **kwargs):
        for k in [ 'search_object', 'id', 'connection_factory' ]:
            setattr(self, k, kwargs.get(k, None))

            self.connections = {}
        if self.connection_factory:
            self.connection_factory.addCore(self.id, self)

    def search(self, criteria):
        pass

    def agent_register(self, agent_id, agent, subject, connection):
        self.connections[agent_id] = {
            'id': agent_id,
            'agent': agent,
            'subject': subject,
            'connection': connection,
        }

    def agent_unregister_agent_id(self, agent_id):
        self._unreg('id', agent_id)

    def agent_unregister_agent(self, agent):
        self._unreg('agent', agent)

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
